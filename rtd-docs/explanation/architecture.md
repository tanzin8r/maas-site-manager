# MAAS Site Manager Architecture

## Important terms

* Site: A MAAS instance or a MAAS Cluster. This is usually the regiond connected to MAAS Site Manager
* Enrolment: The process to connect a Site to Site Manager is called "Enrolment"
* [Rocks](https://ubuntu.com/server/docs/about-rock-images): An opinionated way of designing an OCI compatible
  container using a process manager called [pebble](https://github.com/canonical/pebble) and
  [Rockcraft](https://documentation.ubuntu.com/rockcraft/en/latest/explanation/rockcraft/) as build environment
* [Charms](https://charmhub.io): Software that can be installed using [Juju](https://juju.js) on
  [kubernetes](https://kubernetes.io) or bare metal machines

## Distribution

MAAS Site Manager is distributed as Rock and Charm to be run on a kubernetes (K8S),
such as [MicroK8s](https://ubuntu.com/kubernetes) or [Canonical kubernetes](https://ubuntu.com/kubernetes).

We distribute Site Manager like this so that you can install and scale it up easily.
Depending on the number of Sites that you want to manage, a single back-end pods might
not be enough to process the heartbeat signals from your sites. At this point you have
two options. Firstly you can increase the time between heartbeats or you can scale up
the number of back-ends (and possibly your database) to be able to process more hartbeats in time.

Site manger charms relate to [traefik](https://charmhub.io/traefik-k8s) as an ingress.
Traefik will do the load balancing and this way it is guaranteed that no single back-end will
need to process the load from your connected Sites.

## Code Structure

MAAS Site Manager consists of three main components: a frontend web application, a backend API server, and a Temporal worker.

### Frontend

The frontend is a React/TypeScript application located in `frontend/` that provides a web interface for managing sites, images, settings, and user accounts. It communicates with the backend API through an axios-based client generated from OpenAPI specifications. React Query manages state for API query data, and Playwright is used for end-to-end testing.

### Backend

The backend API server is located in `backend/msm/apiserver/` and exposes two APIs. The User/Worker API (`/api`) is used by the web interface and the Temporal worker and is handled by `user/handlers/` for site management (list, edit, approve, reject, delete), custom image management (`images.py`), upstream boot asset management (`bootassets.py`), site token management, user management and authentication, application settings, image source configuration, and selections (which images are available to sites from upstream sources). The Site API (`/site`) is used by MAAS instances and is handled by `site/handlers/` for site enrollment (`enroll.py`), heartbeat and status reporting (`report.py`), and image downloads (`images.py`).

The backend is organized into several layers. Handlers in `user/handlers/` and `site/handlers/` process HTTP requests and delegate to services. Services in `service/` provide a wrapper around SQLAlchemy for API handlers and implement business logic for sites, images, tokens, users, S3 operations, and Temporal workflow orchestration. The database layer in `db/` contains SQLAlchemy models in `db/models/` for sites, tokens, users, images, and settings, query utilities in `db/queries/` for counting, searching, and aggregating, and migrations in `db/alembic/versions/`. Schema validation in `schema/` handles pagination, search, and sorting.

### Temporal Worker

The Temporal worker (`backend/msm/temporal/`) handles long-running background tasks such as image synchronization. It contains workflows in `workflows/` that orchestrate image synchronization (`sync.py`), deletion (`delete.py`), and downloading from upstream sources (`download_upstream.py`). Activities in `activities/` perform the actual work such as downloading images from upstream sources, processing boot assets (`bootasset.py`), handling simplestream operations (`simplestream.py`), and managing S3 operations. The worker runs as a separate process and communicates with the Temporal server to execute workflows triggered by the API server.

### Common Utilities

Common utilities shared between the API server and Temporal worker are located in `msm/common/` and include API models in `common/api/`, enums in `common/enums.py`, JWT handling in `common/jwt.py`, and workflow names and parameter definitions in `common/workflows/`.

## Important processes

### Onboarding a Site

To onboard a Site a user generates onboarding tokens that should have a rather short lifetime
(the time needed to onboard the site). During onboarding these tokens are exchanged with
system to system JWT tokens that use the lifetime and token rotation time configured in Site Manager.

Before the Site can start reporting data, a Site Manager administrator needs to authorize the site
in the Site Manager UI.

After doing so, the site will start sending updates every heartbeat interval.

See [mermaid sequence diagram](/explanation/onboarding-workflow-sequence-diagram.mermaid) for details of this workflow.

### Re-onboarding a Site

If network connectivity is broken or Site Manager cannot be reached by a Site for more than the
Token Rotation interval, the Site is removed from Site Manager.

However, it can be re-added using the onboarding process and it's identity is tied to MAAS' cluster ID
so that Site Manager will recognize that the Site was already known.

Once MAAS notices that it cannot send updates anymore due to an expired token it will automatically
stop doing so.

### Removing a Site

When a site is removed in Site Manager, MAAS is notified and will disconnect from Site Manager and stop
sending updates.

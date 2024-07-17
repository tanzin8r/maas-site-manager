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

TODO: Describe layers and pages

## Important processes

### Onboarding a Site

To onboard a Site a user generates onboarding tokens that should have a rather short lifetime
(the time needed to onboard the site). During onboarding these tokens are exchanged with
system to system JWT tokens that use the lifetime and token rotation time configured in Site Manager.

Before the Site can start reporting data, a Site Manager administrator needs to authorize the site
in the Site Manager UI.

After doing so, the site will start sending updates every heartbeat interval.

See [mermaid sequence diagram](./onboarding-workflow-sequence-diagram.mermaid) for details of this workflow.

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

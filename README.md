# MAAS Site Manager

MAAS Site Manager is a tool to manage multiple MAAS installations (called 'sites') at the same time.
It provides an overview of all connected sites, as well as some statistics for those sites.
Finally, it can show the physical locations of sites on a map.

This repository contains a sub-folder the backend and the frontend.

## How to install MAAS Site Manager?

The preferred way of installing MAAS Site Manager is using Juju and Kubernetes charms.

### Installing the Juju Controller

Installing the MAAS Site manager charm requires a running Kubernetes (k8s) Juju controller.

There is more than one way to create this setup, e.g.

- Use a [charm development environment generator](https://github.com/canonical/maas-charm-dev-env-setup/tree/main) or
- [Getting started on MicroK8s](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s#heading--configure-microk8s)

### Installing MAAS Site Manager

Once you have a k8s Juju controller installing MAAS Site Manager is as simple as:

```bash
juju switch $YOUR_MODEL
juju deploy postgresql-k8s --channel 14/stable
# postgres may enter a blocked state, but will return to waiting/idle after some time
juju deploy maas-site-manager-k8s
juju integrate postgresql-k8s maas-site-manager-k8s

# wait for applications to become ready
juju status --watch 5s
```

### Installing COS lite

This step is optional but recommended if you want to monitor MAAS Site Manager.
Currently we are offering limited monitoring capability, mostly exposing the performance of the Site Manager endpoints.
This will be improved in future versions.

To setup COS lite and integrate MAAS Site Manager with it do the following:

```bash
# bind MetalLB to a local IP
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
microk8s enable metallb:$IPADDR-$IPADDR
sudo microk8s enable dns
sudo microk8s enable hostpath-storage

# create a model for COS Lite
juju add-model cos-lite

# get bundle default offer definitions
curl -L https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays/offers-overlay.yaml -O
# reduce COS storage requirements (non production env)
curl -L https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays/storage-small-overlay.yaml -O
# deploy COS Lite
juju deploy cos-lite --trust --overlay ./offers-overlay.yaml --overlay ./storage-small-overlay.yaml
# Prometheus scrape is no longer part of the default offers
juju offer prometheus:metrics-endpoint prometheus-scrape
# wait for everything to be ready
juju status --watch 5s --relations

# integrate
juju switch $YOUR_MODEL
juju integrate maas-site-manager-k8s admin/cos-lite.loki-logging
juju integrate maas-site-manager-k8s admin/cos-lite.grafana-dashboards
juju integrate maas-site-manager-k8s admin/cos-lite.prometheus-scrape
```

### Enabling Charm-Level Tracing

For development and debugging it can be useful to enable tracing for your charms. This step is optional.

To enable charm-level tracing, follow these steps:

```bash
# to enable charm-level tracing
juju deploy tempo-coordinator-k8s --channel edge --trust tempo
# wait for blocked/idle (missing any worker relation)
juju status --watch 5s --relations
juju deploy tempo-worker-k8s --channel edge --trust tempo-worker
# wait for blocked/idle (missing relation to a coordinator charm)
juju status --watch 5s --relations
juju integrate tempo tempo-worker
# secret-key must be at least 8 characters
export ACCESS_KEY=accesskey
export SECRET_KEY=mysoverysecretkey
juju deploy minio --channel edge --trust --config access-key=$ACCESS_KEY --config secret-key=$SECRET_KEY
juju status
# wait for active/idle
juju deploy s3-integrator --channel edge --trust s3
juju status
# wait for s3 to go blocked/idle
juju run s3/leader sync-s3-credentials access-key=$ACCESS_KEY secret-key=$SECRET_KEY

juju status
# here, store the IP address of the minio/0 unit
export MINIO_IP="10.1.64.154"
```

Next, create a bucket in Minio. First, install the `minio` pip package

```bash
pip install minio
```

Then, run the following python script:

```python
from minio import Minio
from os import getenv
# Replace this with IP of the minio unit
# shown by juju status
address = getenv("MINIO_IP")
bucket_name = "tempo"

mc_client = Minio(
    f"{address}:9000",
    access_key=getenv("ACCESS_KEY"),
    secret_key=getenv("SECRET_KEY"),
    secure=False,
)

found = mc_client.bucket_exists(bucket_name)
if not found:
    mc_client.make_bucket(bucket_name)
```

Finally, complete the setup:

```bash
juju config s3 endpoint=minio-0.minio-endpoints.cos-lite.svc.cluster.local:9000 bucket=tempo
juju integrate tempo s3
juju integrate tempo:ingress traefik
juju relate tempo:grafana-source grafana:grafana-source
```

### Setup a Reverse Proxy

MAAS Site Manager requires a reverse-proxy service. The easiest way to get one
is reusing the Traefik service that comes with COS. If you have set up charm-level tracing,
you must use Traefik for the reverse-proxy service.

```bash
juju switch cos-lite
juju offer traefik:ingress
juju offer tempo:tracing

juju switch $YOUR_MODEL
juju integrate maas-site-manager-k8s admin/cos-lite.traefik
juju integrate maas-site-manager-k8s admin/cos-lite.tempo
```

MAAS Site Manager should be available at `http://$IPADDR/$YOUR_MODEL-maas-site-manager-k8s`

## How to set up a development environment

### Backend

#### Manual setup on your host or on a virtual machine

The application is currently supported on Ubuntu 22.04 (Jammy Jellyfish). It is suggested to use an [LXD](https://canonical.com/lxd) container for the development environment.

The following steps are needed for basic setup, after ensuring you are in the right directory (`/backend`):

- ensure make is installed

```bash
sudo apt install make
```

- install project dependencies

```bash
make install-dependencies
```

The application is run using the `uvicorn` ASGI server. It requires a postgres database to connect to. Having installed the (system-wide) PostgreSQL instance with `make install-dependencies`, the required user and database can be set up as follows:

- create new user with password

```bash
sudo -i -u postgres psql -c "CREATE USER \"msm\" WITH ENCRYPTED PASSWORD 'msm'"
sudo -i -u postgres createdb -O "msm" "msm"
```

- edit `pg_hba.conf` (under e.g. `/etc/postgres/14/main/`) to include at the bottom

```txt
host    msm     msm     0/0     md5
```

- restart postgres

```bash
sudo systemctl restart postgresql
```

#### Setup using Docker

Ensure that you have a recent version of [Docker](https://docs.docker.com/get-docker/) installed. To build and start the backend and the database run,

```bash
docker compose up --build
```

After the build has succeeded, `--build` can be omitted when bringing up the containers in the future (unless changes to `backend/Dockerfile` were made).

#### Nginx TLS Proxy in Dev Environment

If you need the Site Manager API to provide a self-signed TLS certificate, follow the steps below.
You will need this if you are planning on issuing an enrolment request from a MAAS instance.

1. To start the `nginx` service when the backend container starts, set `USE_NGINX_TLS_PROXY=1` in `docker-compose.env`.
2. Start the container with `docker compose up`. You will need to include the `--build` option if you haven't done so since pulling the change to create the certificate and set up `nginx` within `backend/Dockerfile`.
3. Once the container has started, copy the certificate onto your machine: `docker cp maas-site-manager_backend_1:/root/certs/msm.crt ~/`. This will copy the certificate to your home directory (change the second path if you would like to copy it elsewhere).
4. On the MAAS side, the LXD container needs to know that this is a trusted certificate. If using `setup-dev-env.sh` from the [`maas-dev-setup` repository](https://github.com/canonical/maas-dev-setup), you can enable this by providing the `-c` or `--ca-crt` option and the location of the `msm.crt` file on your machine.

If you are not using the script in step 4 above, follow these steps to tell MAAS that this is a trusted certificate:

1. `scp` the `msm.crt` file to the LXD container running MAAS: `scp /path/on/your/machine.crt ubuntu@$container_ip:/home/ubuntu/`.
2. `ssh` to the LXD container and place the file in the correct location. Note this cannot be handled above as we cannot `scp` as root: `sudo cp /home/ubuntu/msm.crt /usr/local/share/ca-certificates`
3. Update the trusted CA's: `sudo update-ca-certificates`
4. Add the cert's CN as a hostname with the following commands:

```bash
hn=$(openssl x509 -noout -subject -in msm.crt -nameopt multiline | grep commonName | awk '{ print $3 }')
# here, MAAS_MANAGEMENT_IP_RANGE is the gateway for your maas-kvm lxd network (e.g. 10.20.0.1)
echo $MAAS_MANAGEMENT_IP_RANGE $hn | sudo tee --append /etc/hosts
```

#### Starting containers manually

Note: you can stop here if you're using `docker compose`.

It is simple to launch a PostgreSQL instance via Docker,

```bash
docker run --rm -it \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=msm \
    --name postgres \
    postgres:14
```

#### Running the app

When using Docker, to run the application simply execute,

```bash
docker compose exec backend bash
```

Manually, do the following:

- export the following environment variables when running the application

```bash
export MSM_DB_HOST="localhost"  # change if PostgreSQL is running elsewhere
export MSM_DB_PORT=5432
export MSM_DB_NAME="msm"
export MSM_DB_USER="msm"
export MSM_DB_PASSWORD="msm"
```

Then, the application can be run using

```bash
tox run -e api
```

A database schema is created for you on application startup. If the schema changes or you want a fresh start, you can do the following.

Using Docker, you should first stop the app:

```bash
docker compose down
```

and then run:

```bash
docker volume rm maas-site-manager_postgres-data
```

A new database will be automatically created on the next `docker compose up`

To manually recreate the database, do the following,

- connect to your database

```bash
psql
\c <database_name>
```

- empty and recreate the database

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

#### Sample data

There is sample data available for testing. To load this, do the following:

- export the `MSM_DB_*` environment variables as needed
- run `tox run -e sampledata -- create-fixtures`

If you're running the backend with docker, you'll need to access the container first:

```bash
docker compose exec backend bash
```

The command to generate sample data is almost the same, but with the path for tox included:

```bash
~/.local/bin/tox run -e sampledata -- create-fixtures
```

If you used the test data, you can generate a token for the pre-existing `admin` user with,

```bash
export TOKEN=$(curl -X 'POST' 'http://localhost:8000/api/v1/login' -H 'accept: application/json' -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin@example.com&password=admin' | jq -r .access_token)
```

and then call the endpoints with,

```bash
curl http://localhost:8000/api/v1/sites -H "Authorization: bearer $TOKEN"
```

Database migrations are managed using [Alembic](https://alembic.sqlalchemy.org). The command is available through the `alembic` tox environment.

To ensure that the database is up to date with the changes in migrations, run,

```bash
tox run -e alembic -- upgrade head
```

When table definitions are changed, you can create a new patch by running,

```bash
tox run -e alembic -- revision --autogenerate -m $name
```

where `$name` is the desired migration name. The resulting filename will be of the form `$id_$name.py`, where the revision id is automatically incremented from the last one (note that, for this reason, passing `--rev-id` won't have any effect).

The `--autogenerate` parameter can be omitted to create an empty migration which can later be manually edited.

**NB** the database should be at the correct state previous to the modifications that the path should contain. This should be done by calling the env with `upgrade head` before generating new revisions.

#### Other settings

There are other settings, configurable by setting environment variables, to control behaviours of the app.

- heartbeat interval: the time interval at which MSM expects its connected sites to send heartbeat. This is configurable as,

```bash
export MSM_HEARTBEAT_INTERVAL_SEC=<value>
```

in seconds. The default value is 300s.

- connection lost threshold: threshold value for which a site gets marked as 'connection lost' in MSM. This is configurable as,

```bash
export MSM_CONN_LOST_THRESHOLD_SEC=<value>
```

in seconds. The default value is 600s. Note that the connection lost threshold has to be greater than the heartbeat interval.

- metrics refresh interval: the time interval at which MSM metrics are refreshed. This is configurable as,

```bash
export MSM_METRICS_REFRESH_INTVAL_SEC=<value>
```

in seconds. The default value is 300s.

#### Linting and testing

The project uses `tox` for running Python-related workflows.

- code formatting: `tox -e format`
- linting: `tox -e lint`
- type checking: `tox -e check`

Unit tests use `pytest`. Tests can be run using,

```bash
tox run -e test
```

or alternatively just,

```bash
tox
```

since this is the default target. This runs all tests in parallel, and reports coverage.

To run the tests sequentially, possibly selecting a subset of them, it is possible to use the default `py` environment passing additional arguments to `pytest`:

```bash
tox run -e py -- <extra args> ..
```

### Frontend

- When installing the frontend for the first time, read the _note on installing the frontend_ below. Prerequisite steps for running anything with yarn (starting frontend, testing, etc.) are:

```bash
cd frontend
yarn
```

after which you can start the frontend (`yarn dev`).
Note that when running a local setup, it is not advised to run `make ci-dep`, since, depending on the host system, this might install outdated dependencies and cause issues.

#### A note on installing the frontend

As per default, `apt install yarn` installs `cmdtest`, a distinct package from the one we actually want to use. Instead, we recommend the following steps sourced from [yarn package](https://yarnpkg.com/):

```bash
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
```

The yarn package is now added as a source, so install as expected

```bash
sudo apt update && sudo apt install --no-install-recommends yarn
```

If not already installed, you'll also want NodeJS. We recommend using [nvm](https://github.com/nvm-sh/nvm) to accomplish this:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
```

NodeJS 20 is the minimum recommended version for MAAS Site Manager

```bash
nvm install 20
nvm use 20
```

After which you should be able to serve the frontend

```bash
cd frontend
yarn
yarn dev
```

#### Updating API Client

You can update TypeScript API Client from the OpenAPI schema by running the following command. Make sure that the backend is running beforehand.

```bash
yarn generate-api-client
```

#### Using a local backend

Setup local environment variables

```bash
cp .env.development .env.development.local
```

Set `VITE_USE_MOCK_DATA` to `false` in `.env.development.local` and start the backend

#### Project conventions

##### CSS

###### Mobile-first approach

We first write CSS styles specifically for mobile devices, and then progressively enhance them for larger screen sizes using min-width media queries.

Single and consistent direction of media queries (min-width) makes the code easier to read and maintain.

#### Testing

We use [Playwright](https://playwright.dev/) for end-to-end tests and [Vitest](https://vitest.dev/) for unit/integration tests. We prefer integration testing over unit testing as we focus on user-centric testing and avoid testing implementation details. That makes changes and refactoring easier and helps ensure that things continue to work as expected for the end user.

##### How to run tests

###### end-to-end

```bash
yarn playwright test
```

###### unit/integration

```bash
yarn test
```

#### Keeping packages up-to-date

Run `yarn upgrade-all` to attempt to upgrade all packages to latest version.

#### Map assets

##### Fonts

Noto Sans fonts in pbf format compatible with MapLibre GL JS (located in `/frontend/public/`) are sourced from [protomaps](https://github.com/protomaps/basemaps-assets/tree/main/fonts).

##### Tiles

Natural Earth Vector tiles sourced from <https://github.com/lukasmartinelli/naturalearthtiles/releases/download/v1.0/natural_earth.vector.mbtiles> are converted to pmtiles using <https://github.com/protomaps/PMTiles>.

## Building for production

### Snap

To build the snap run

```bash
snapcraft -v -o maas-site-manager.snap
```

The resulting snap can be installed via

```bash
sudo snap install --dangerous ./maas-site-manager.snap
```

After installation, the service won't be enabled automatically and needs to be
configured.

The snap provides a few settings.

For database configuration:

- `db.host`: host to connect to (defaults: `localhost`)
- `db.port`: port to connect to (default: `5432`)
- `db.name`: database name (default: `msm`)
- `db.user`: database username (default: empty)
- `db.password`: database password (default: empty)

These can be set, after installing the snap via

```bash
sudo snap set maas-site-manager db.host=<hostname> db.name=<name> db.password=<password>
```

After setting the configuration, the service can be enabled

```bash
sudo snap start --enable maas-site-manager
```

Once the service is enabled, changing settings will automatically restart it
with the new ones.

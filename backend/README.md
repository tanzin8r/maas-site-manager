# MAAS site manager

## Development environment

The application is currently supported on Ubuntu 22.04 (Jammy). It's suggested
to use a LXD container for the development environment.

These are the step needed for setup:

 - ensure make is installed
   ```
   sudo apt install -y make
   ```

 - install project dependencies
   ```
   make install-dependencies
   ```


## Linting and testing

The project uses `tox` for running python-related workflows:

  - Code formatting: `tox -e format`
  - Linting: `tox -e lint`
  - Type checking: `tox -e check`


## Unit testing

Unit tests use `pytest`. Test can be run either via

```
tox -e test
```

or just

```
tox
```

(as this is the default target).

It's also possible to pass additional arguments to `pytest` (e.g. to run a
subset of tests) by passing them to `tox` via extra args:

```
tox -- <extra args>...
```


## Running the app in development

In development, the application can be run using the `uvicorn` ASGI server.

It requires a PostgreSQL database set up to connect to.  One (more persistent)
option is to set up the required user and database in the system-wide
PostgreSQL instance (installed via `make install-dependencies`).

Make sure to set the following environment variables when starting the app:

```
export POSTGRES_HOST="hostname"
export POSTGRES_PORT=5432
export POSTGRES_DB="postgres"  # default for postgres docker image
export POSTGRES_USER="postgres"  # default for postgres docker image
export POSTGRES_PASSWORD="msm"
```

Another (quicker) way is to launch a PostgreSQL instance via `docker`:

```
docker run --rm -it \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=msm \
    --name postgres \
    postgres:14
```

Database schema setup will happen automatically at application startup.

The application can be run via

```
tox -e run run
```

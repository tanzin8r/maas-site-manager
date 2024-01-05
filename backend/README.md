# MAAS site manager backend


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
tox run -e test
```

or just

```
tox
```

(as this is the default target). This runs all tests in parallel and reports
coverage.

To run tests sequentially, possibly selecting a subset of them, it's possibly
to use the default `py` env, passing additional arguments to `pytest`:

```
tox run -e py -- <extra args>...
```


## Running the app in development

The application is run using the `uvicorn` ASGI server.

It requires a PostgreSQL database set up to connect to.  One (more persistent)
option is to set up the required user and database in the system-wide
PostgreSQL instance (installed via `make install-dependencies).

Make sure to set the following environment variables when starting the app:

```
export MSM_DB_HOST="localhost"  # change if PostgreSQL is running elsewhere
export MSM_DB_PORT=5432
export MSM_DB_NAME="postgres"  # default for postgres docker image
export MSM_DB_USER="postgres"  # default for postgres docker image
export MSM_DB_PASSWORD="msm"
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
tox run -e api
```


## Delete and recreate the database

There is not yet functionality to migrate the database with MAAS site manager.
However a database is created for you on application startup. If the schema changes
or you just want a fresh start, you can do the following.

### Using docker

To recreate the database stop the app (e.g. `docker compose down`) and run

```
docker volume rm maas-site-manager_postgres-data
```

A new database will be created for you on the next `docker-compose up`.

### Any postgresql database

(This also works if you use docker. In that case make sure to connect with the correct credentials)

If you are using your own postgres you can usually do the following to empty the database:

- Connect to your database
```
psql
\c <database_name>
```

- Execute the following to empty and recreate the database.
```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

### Importing test data to the database

There are CSV files available that can be used as test data.

If you are running the app in docker you can easily load those

- export the `MSM_DB_*` environment vars as needed
- run `tox run -e sampledata -- create-fixtures`

### Interact with the API

If you used the `test-data`, then you can generate a token for the pre-existing `admin` user with 

```bash
export TOKEN=$(curl -X POST http://localhost:8000/api/v1/login -d '{"email": "admin@example.com", "password": "admin"}' -H "Content-Type: application/json" | jq -r .access_token)
```

and call the endpoints with 

```bash
curl http://localhost:8000/api/v1/sites -H "Authorization: bearer $TOKEN"
```


## Database migrations

Database migrations are managed using [Alembic](https://alembic.sqlalchemy.org).
The command is available through the `alembic` tox environment.

To ensure that the database status is up to date with the changes in migrations, run

```
tox run -e alembic -- upgrade head
```

When table definitions are changed, to create a new patch run

```
tox run -e alembic -- revision --autogenerate -m $name
```

where `$name` is the desired migration name.  The resulting filename will be in
the form `$id_$name.py`, where the revision `id` is automatically incremented
from the last one (note that, for this reason, passing `--rev-id` won't have
any effect).

The `--autogenerate` parameter can be omitted to create an empty migration that
can be later manually edited.

**Note**: the database should be at the correct state previous to the
modifications that the patch should contain.  This should be done by calling
the env with `upgrade head` before generating new revisions.

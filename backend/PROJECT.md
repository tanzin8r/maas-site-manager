# MAAS site manager backend layout

This document describes the code structure and layout for the MAAS site manager
backend, as well as some best practices to keep in mind when adding new
components or extending existing ones.


## Components

The code layout is intended to match components and layers of the application.

The tree structure of the Python project is shown here (as obtained from `tree -d msm`):

```
msm
├── api
│   ├── site
│   │   └── handlers
│   └── user
│       └── handlers
├── cmd
│   ├── admin
│   └── sampledata
├── db
│   ├── alembic
│   │   └── versions
│   ├── models
│   └── queries
├── sampledata
├── schema
├── service
└── snap
    └── templates
```

In general each top-level package should contain "private" sub-packages
(conventionally with the name starting with an underscore), and export public
names in their `__init__.py`, to encourage decoupling and making the public API
more evident.

## Entry points

The project provides the following entry points:

- `msm-api`, the API server (FastAPI application running with uvicorn)
- `msm-admin`, admin script, mainly for initial service setup
- `msm-sampledata`, script to generate sample data in the database

Scripts should have their entry point defined as
`msm.cmd.<script-name>.script`, so that code specific to each one lives under a
`msm/cmd/<script-name>` directory.

The API server is defined separately, since it makes use of uvicorn.

# Application layers

The main layers in the API service are the following:

- REST API (`msm/api`)
- service layer (`msm/service`)
- database layer (`msm/db`)

Each of the layers is described below in a separate section.

## REST API

this layer is responsible for logic related to the request handling, such as
routing the request to the correct handler, raising HTTP error responses,
validating request payload and so on. The logic needed for the functionality
performed by each API endpoint should be provided by methods defined in the
service layer (described below). Access to service layer classes is provided
via handler dependencies.

The FastAPI application that gets run by uvicorn is set up in
`msm.api.create_app()`. This adds middlewares and mounts the sub-applications
for the user and site APIs.

Each API has a similar structure (under `msm/api/user` and `msm/api/site`
respectively), providing a `handlers.ROUTERS` variable.  This contains a
sequence of routers collecting all the API endpoints which are added to each
sub-application that gets mounted under the main one.

Handlers for each application are defined in different sub-packages of the
`handlers` one, grouped by functionality or entity they relate to. Each
submodule should define a `v1_router` variable which is a local API router
under the `/v1` prefix, so that in the future additional routers can be created
and endpoints added to each version.  Adding a new API version would consist in
creating an additional `v2_router = APIRouter(prefix="/v2")` and registering new handlers to it, as well as collecting the v2 routers in the application `ROUTERS` global variable.

Common prerequisites for handlers (e.g. authentication/authorization) can be
implemented as dependencies declared as handler parameters. Those can be either
placed under the the `api` package, or packages specific to either
sub-application, if they're spcific to its API.

### Adding new handlers

Adding a new handler consists in creating a new function under
`msm/api/<api-name>/handlers/`.

If the handler is for a new type of resource/interaction, the first step would be to add a new file with a router definition like

```python
v1_router = APIRouter(prefix="/v1")
```

and add the router to the `ROUTERS` list to the corresponding
`msm/api/<api-name>/__init__.py`.

The handler itself should be in the form

```python
@v1_router.get("/<api-name>/<path>")
async def <verb>_<path>(...):
```

matching the final path. This is useful since the OpenAPI spec will by default
name endpoints based on their function name.

Authentication/authorization for handlers is implemented via dependencies (
e.g. by `authenticated_user` or `authenticated_admin` for the `msm.api.user`
sub-application, or `authenticated.site` for the `msm.api.site` one). The
dependency automatically takes care of raising the appropriate error in case of
failed authentication.

The parameter holding request body (such as POST/PUT data) should be defined
with a Pydantic model named `<Handler><Verb>Request`next to the handler
(e.g. `TokensPostRequest`) and passed as a paramter to the handler, named
`<verb>_request` (e.g. `post_request`), for consistency.

Similarly the response should generally be defined with a Pydantic model named
`<Handler><Verb>Response`.  In some cases, e.g. when a single instance of a
model coming from the service layer (see below) is returned, that model can
just be used as response, but in general it's better to keep models decoupled,
in case new fields are added in the model from the service layer that are not
desired in the API.

As an example, consider a model as the following, defined in the service layer

```python
class Foo(BaseModel):
    id: int
    name: str
```

and the handler API is also defined to return a `Foo` instance as:

```
@router.get("/foo/{id}")
async def get_foo(...) -> Foo:
```

Now, let's say a `secret: str` field is added to the model to hold a
secret. This would automatically be included in the API output as well (which
is not desired in this case).

A way to handle this would be to have two separate models, one for the db:

```python
class Foo(BaseModel):
    id: int
    name: str
    secret: str
```

and one for the handler, which converts between the two:

```python
class GetFooResponse(BaseModel):
    id: int
    name: str

@router.get("/foo/{id}")
async def get_foo(...) -> GetFooResponse:
    ...
    foo = async service.get_foo(...)  # this returns the Foo instance
    return GetFooResponse(**foo.model_dump())
```

## Service layer

The purpose of the service layer is to encapsulate business logic, providing
common functionality and reusable components that can be used by the API or
other higher level components (e.g. scripts or additional services).

Currently the main focus for the service layer is to provide CRUD operations
for database models. While there's no necessarily a 1:1 match with database
tables, in many case a service class is targeted at a specific database
model.

It's in general preferred to wrap data returned by database queries with
Pydanic models (or a collection of them), rather than plain dicts, since it
makes clear which fields are present in the returned data and improves type
definitions.  Similarly, it's better to group related composite parameters
passed to the methods in a Pydantic model.

The service layer also exposes a `ServiceCollection` class, which is purely a
conveniency collection of all service classes, to avoid having to pass them
individually as a dependency in API handlers. Thus every newly implemented
service should be added to to the `ServiceCollection`.

## Database layer

The database layer is responsible for the actual interaction with the
PostgreSQL database.

The `msm.db` module contains tables definitions (under `msm.db.tables`) as well
custom DB types and generic helpers to generate queries (e.g. related to
counting and filtering).

The `msm.db.models` submodule also contains some Pydantic models which are
intended to hold data returned from the database. These are generally used by
the service layer (as describe above), and they're not meant to be a 1:1 match
with table defintions, but rather contain fields that are needed for specific
purposes, possibly computed or coming from different tables.  This helps
keeping the model focused on specific use cases, and decouple it from where the
info is actually stored in the database.

Finally, the `msm.db.alembic` package contains the database migrations setup,
which is achived via [Alembic](https://alembic.sqlalchemy.org/). The migrations
themselves are generated under `msm/db/alembic/versions`.

## Other modules

Additional support modules are:

- `msm.sampledata` contains the logic for creating sampledata, used by the
  `msm-sampledata` script.
- `msm.schema` contains helpers and schema defintions related to common API
  request parameters handing, such as pagination, sorting and search filters.
- `msm.snap` contains logic related to the snap setup, including snap hooks.
  

# MAAS Site Manager

This repository contains the MVP for the MAAS Site Manager. It contains one sub-folder for every sub-project.

## How to Run a Local Development Environment?

### Manual Setup

Please follow the instructions in [MAAS Site Manager Backend](/backend/README.md) and [MAAS Site Manager Frontend](/frontend/README.md).

### Using Docker Compose

Ensure that you have a recent version of [Docker](https://docs.docker.com/get-docker/) installed.

* Run `docker-compose up --build` to start the backend and the database.
* Run `cd frontend` and `yarn dev` to start the frontend

# MAAS Site Manager Frontend

This is the frontend for the [MAAS Site Manager Project](https://launchpad.net/maas-site-manager).

## How to run a development environment

First start the backend

```bash
$LP_USERNAME=your-username
sudo apt-get install tox

git clone https://code.launchpad.net/~maas-committers/maas-site-manager/+git/site-manager

cd site-manager

docker run --rm -it \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=pass \
    --name postgres \
    postgres:14

tox -e run
```

Then run this frontend

```bash
git clone https://code.launchpad.net/~maas-committers/maas-site-manager/+git/site-manager-frontend
cd site-manager-frontend

# TODO, possibly edit an env/config file to point to a local backend

yarn  # install dependencies
yarn run dev
```

## Project conventions

## Testing

We use [Playwright](https://playwright.dev/) for end-to-end tests and [Vitest](https://vitest.dev/) for unit/integration tests. We prefer integration testing over unit testing as we focus on user-centric testing and avoid testing implementation details. That makes changes and refactoring easier and helps ensure that things continue to work as expected for the end user.

### How to run tests

#### end-to-end

```bash
yarn playwright test
```

#### unit/integration

```bash
yarn test
```

## Keeping packages up-to-date

Run `yarn upgrade-all` to attempt to upgrade all packages to latest version.

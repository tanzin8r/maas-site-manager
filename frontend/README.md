# MAAS Site Manager Frontend

This is the frontend for the [MAAS Site Manager Project](https://launchpad.net/maas-site-manager).

## How to run a development environment

The quickest way to get started is run frontend with mock backend which is enabled by default.

```bash
yarn dev
```

### Using a local backend

Setup local environment variables

```bash
cp .env.development .env.local.development
```

Set `VITE_USE_MOCK_DATA` to `false` in `.env.development.local`.

Start the backend
[MAAS Site Manager Backend Readme](/backend/README.md).

## Project conventions

## CSS

### Mobile-first approach

We first write CSS styles specifically for mobile devices, and then progressively enhance them for larger screen sizes using min-width media queries.

Single and consistent direction of media queries (min-width) makes the code easier to read and maintain.

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

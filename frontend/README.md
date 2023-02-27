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

## How to run tests

### End to end

```bash
yarn playwright test
```

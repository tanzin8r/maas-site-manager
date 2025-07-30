# MAAS Site Manager Deployment

The preferred way of installing MAAS Site Manager is by deploying it as a Kubernetes charm. Using Terraform, we can deploy the charm and necessary dependencies, as well as provide integrations between them easily.

## Installing the Juju Controller

Installing the MAAS Site manager charm requires a running Kubernetes (k8s) Juju controller.

There is more than one way to create this setup, e.g.

- Use a [charm development environment generator](https://github.com/canonical/maas-charm-dev-env-setup/tree/main) or
- [Getting started on MicroK8s](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s#heading--configure-microk8s)

To ensure you have everything set up properly, check the output of `juju clouds` and ensure that the `microk8s` cloud is listed with type `k8s`:

```bash
$ juju clouds

Clouds available on the controller:
Cloud     Regions  Default    Type
microk8s  1        localhost  k8s
```

## Install and Initialize Terraform

To install and initialize Terraform, simply run:

```bash
sudo apt install terraform
terraform init
```

## Deploy MAAS Site Manager

Before executing the deployment script, set some environment variables so Terraform can talk to the Juju controller:

```bash
export CONTROLLER=$(juju whoami | yq .Controller)
export JUJU_CONTROLLER_ADDRESSES=$(juju show-controller | yq .$CONTROLLER.details.api-endpoints | yq -r '. | join(",")')
export JUJU_USERNAME="$(cat ~/.local/share/juju/accounts.yaml | yq .controllers.$CONTROLLER.user|tr -d '"')"
export JUJU_PASSWORD="$(cat ~/.local/share/juju/accounts.yaml | yq .controllers.$CONTROLLER.password|tr -d '"')"
export JUJU_CA_CERT="$(juju show-controller $(echo $CONTROLLER|tr -d '"') | yq '.[$CONTROLLER]'.details.\"ca-cert\"|tr -d '"'|sed 's/\\n/\n/g')"
```

Finally, download the Terraform plan and apply it:

```
mkdir msm-deployment
cd msm-deployment
curl https://git.launchpad.net/maas-site-manager/plain/deploy-msm.tf -o deploy-msm.tf
terraform apply -auto-approve
```

# MAAS Site Manager Deployment

The preferred way of installing MAAS Site Manager is by deploying it as a Kubernetes charm. Using Terraform, we can deploy the charm and necessary dependencies, as well as provide integrations between them easily.

## Installing the Juju Controller

Installing the MAAS Site manager charm requires a running Kubernetes (k8s) Juju controller.

There is more than one way to create this setup, e.g.

- Use a charm development environment generator: run `multipass launch --cpus 4 --memory 8G --disk 80G --name charm-dev-vm charm-dev`
- [Getting started on MicroK8s](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s#heading--configure-microk8s)

To ensure you have everything set up properly, check the output of `juju clouds` and ensure that the `microk8s` cloud is listed with type `k8s`:

```bash
$ juju clouds

Clouds available on the controller:
Cloud     Regions  Default    Type
microk8s  1        localhost  k8s
```

## Object Storage
MAAS Site Manager requires an object storage service, such as Ceph. For a development environment, follow [this](https://canonical-microceph.readthedocs-hosted.com/en/squid-stable/tutorial/get-started/) guide to set up microceph.

If you are installing microceph in the same `charm-dev-vm` as where you are deploying MAAS Site Manager, use a different port than the default (80) when enabling `rgw`. The default port will conflict with the `traefik-k8s` ingress charm.

```
sudo microceph enable rgw --port 8080
```

Finally, take note of the IP address shown by `sudo microceph status` and the port you set above for `rgw`.

Before deploying with Terraform, you need to create an RGW user and S3 access keys. This allows the `s3-integrator` charm to connect to your MicroCeph RGW instance.

Create an RGW user:

```bash
sudo radosgw-admin user create --uid=user --display-name=user
```

Create S3 access keys for the user:

```bash
sudo radosgw-admin key create --uid=user --key-type=s3 --access-key=foo --secret-key=bar
```

Create a bucket for MSM to use:

```bash
sudo apt-get install s3cmd
s3cmd --host <IP>:8080 --host-bucket="http://<IP>/msm-images" \
  --access_key=foo --secret_key=bar --no-ssl mb -P s3://msm-images
```

Replace `<IP>` with the IP address from `sudo microceph status`.

Use these credentials (`foo`/`bar`) and bucket name (`msm-images`) in your `terraform.tfvars` file.

## Install Terraform

To install Terraform, simply run:

```bash
sudo snap install terraform --classic
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

Next, download the Terraform plan:

```
mkdir msm-deployment
cd msm-deployment
curl https://git.launchpad.net/maas-site-manager/plain/deployment/terraform/main.tf -O
curl https://git.launchpad.net/maas-site-manager/plain/deployment/terraform/provider.tf -O
curl https://git.launchpad.net/maas-site-manager/plain/deployment/terraform/temporal.tf -O
curl https://git.launchpad.net/maas-site-manager/plain/deployment/terraform/variables.tf -O
```

The MAAS Site Manager Terraform plan can take various input variables. Make sure to create a file called `terraform.tfvars` inside the `msm-deployment` directory with the entries below, or see the [sample](https://git.launchpad.net/maas-site-manager/plain/deployment/config/terraform.tfvars.sample) file.

```
# Use the IP address from `sudo microceph status` and the port specified with `sudo microceph enable rgw` as shown above
s3_endpoint = "http://10.207.11.185:8080"
s3_access_key = "my_access_key"
s3_secret_key = "my_secret_key"
s3_bucket = "my_s3_bucket"
```


Finally, apply the Terraform plan:
```
terraform init
terraform apply -auto-approve
```

## Create admin account and log in

Once the Terraform plan has been applied, create an admin account in MAAS Site Manager:

```bash
juju run -m msm maas-site-manager-k8s/0 create-admin username=admin password=admin email=admin@example.com
```

Then, you can access MAAS Site Manager at `http://<MULTIPASS_VM_IP>/msm-maas-site-manager-k8s`

## Configure deployment to use pre-existing Juju offers

Some charms do not need to be deployed by the MSM Terraform plan if you have already deployed them previously. For instance, if you have already deployed postgresql-k8s, you may forgo deploying it again and instead use a Juju offer to integrate with MAAS Site Manager. To do so, include the Juju offer URL under the variable name `postgresql_offer_url` within the `terraform.tfvars` file.

Offers for other relation interfaces can be consumed; see `variables.tf`.

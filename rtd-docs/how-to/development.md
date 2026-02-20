# MAAS Site Manager Development

## Testing Code in Development Environment

To test code changes in your development environment, you can build and deploy a new "rock" (container image) without waiting for a new release.

You can either clone the repository inside the VM (requires SSH key setup), or transfer it from your local machine:

```bash
# Option 1: Transfer from local machine
multipass transfer -r ./maas-site-manager charm-dev-vm:/home/ubuntu/

# Option 2: Clone inside VM (requires SSH key with repo access)
git clone git+ssh://git.launchpad.net/~maas-committers/maas-site-manager
```

Navigate to the source directory and build the rock:

```bash
cd maas-site-manager
rockcraft pack
```

This will produce a file like `maas-site-manager_0.1_amd64.rock`.

Upload the rock to the local MicroK8s registry (accessible on port 32000):

```bash
rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
  oci-archive:maas-site-manager_0.1_amd64.rock \
  docker://localhost:32000/maas-site-manager:0.1
```

Update the MAAS Site Manager charm to use the new image:

```bash
juju refresh maas-site-manager-k8s --resource site-manager-image=localhost:32000/maas-site-manager:0.1
```

Also update the temporal-worker charm (which uses the same rock):

```bash
juju switch temporal-worker
juju refresh temporal-worker-k8s --resource temporal-worker-image=localhost:32000/maas-site-manager:0.1
```

After refreshing, check the status with `juju status` and wait for the applications to become `active/idle`. The changes should be visible in the MSM webpage.

## Attaching Site Manager to MAAS

Assuming you have installed MAAS using the [maas-dev-setup](https://github.com/canonical/maas-dev-setup/) Github repository, you should have an LXD instance running your MAAS instance.
To allow the `charm-dev-vm` created previously in [deployment](/how-to/deployment.md) to communicate with MAAS and vice versa, take the following steps:

Confirm the existence of the multipass bridge:

```bash
ip a
```

You should see an interface 'mpqemubr0'

Add this interface to your maas-dev lxd instance, adjusting eth2 as necessary to not conflict with existing interfaces:

```bash
lxc config device add maas-dev <eth2> nic nictype=bridged parent=mpqemubr0
```

Check the IP address of the charm-dev-vm:

```bash
multipass list
```

You should see an output like

```
Name                    State             IPv4             Image
charm-dev-vm            Running           10.135.87.254    Ubuntu 24.04 LTS
                                          10.177.123.1
                                          10.1.64.128
```

We care only about the IP address that site manager is being hosted on, in this case 10.135.87.254
We now need to give the maas-dev instance an IP address on the same subnet.

```bash
lxc shell maas-dev
# Then inside the instance
cat << EOF | sudo tee /etc/netplan/90-custom-eth2.yaml > /dev/null
network:
  version: 2
  ethernets:
    eth2:
      addresses:
        - 10.135.87.XX/24
EOF
sudo netplan apply
```

The XX may be replaced with any number that isn't the same as the charm-dev-vm.
You can confirm this is correctly set up, by pinging the charm-dev-vm IP found using the `multipass list` command.
You can now enroll your MAAS instance with site manager.

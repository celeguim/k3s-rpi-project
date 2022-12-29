## Goal

Build a light-weight bare metal kubernetes cluster with k3sup / k3s
https://github.com/alexellis/k3sup

The k3s cluster will have a load balancer (MetalLB) and ingress controller (NGINX) working together

## Inventory

Bare metal setup

<img src="images/devices.png" alt="drawing" width="200"/>

| role   |      ip       |   user   |           device | cpu | mem |        proc |
| :----- | :-----------: | :------: | ---------------: | :-: | :-: | ----------: |
| master | 192.168.1.180 | celeghin | OKDO-RASPBERRYPI |  4  | 4GB | arm aarch64 |
| node   | 192.168.1.182 | celeghin |     NIPOGI-J4125 |  4  | 6GB | intel j4125 |
| node   | 192.168.1.183 | celeghin | MINISFORUM-N4020 |  2  | 4GB | intel n4020 |

## Pre-reqs

[](./pre-reqs.txt)

- set hostname
- install curl k3sup net-tools
- ssh passwordless
- disable ipv6 and swap
- permanent ipv4 / nmplan

## K3s installation

As we don't want to have the default integrated traefik, but instead we want to have MetalLB as load balancer and NGINX as ingress controller, so we must disable it on the installation, like:

- Just wait a bit and your cluster will be kicking up, at this point you just have the master

```
USER=celeghin
MASTER=192.168.1.180
CLUSTER=k3s-cluster

k3sup install --cluster --k3s-extra-args '--disable traefik,servicelb,metrics-server' \
 --ip ${MASTER} --user ${USER} --merge --local-path $HOME/.kube/config \
 --context ${CLUSTER} --k3s-channel stable

export KUBECONFIG=~/.kube/config

kubectl config use-context ${CLUSTER}
kubectl get node -o wide
kubectl get all -n kube-system
```

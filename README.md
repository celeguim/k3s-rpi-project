## Goal

Build a light-weight bare metal kubernetes cluster with k3sup and k3s (https://github.com/alexellis/k3sup)

The k3s cluster will have a load balancer (MetalLB) and ingress controller (NGINX) working together

## Inventory

Bare metal setup

<center><img src="images/devices.png" width="400" /></center>

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

### create master

As we don't want to have the default integrated traefik, but instead we want to have MetalLB as load balancer and NGINX as ingress controller, so we must disable it on the installation, like:

```
USER=celeghin
MASTER=192.168.1.180
CLUSTER=k3s-cluster

k3sup install --cluster --k3s-extra-args '--disable traefik,servicelb,metrics-server' \
 --ip ${MASTER} --user ${USER} --merge --local-path $HOME/.kube/config \
 --context ${CLUSTER} --k3s-channel stable

```

Just wait a bit and your cluster will be kicking up, at this point you just have the master

```
export KUBECONFIG=~/.kube/config
kubectl config use-context ${CLUSTER}
kubectl get node -o wide
kubectl get all -n kube-system

NAME               STATUS   ROLES                       AGE   VERSION        INTERNAL-IP     EXTERNAL-IP   OS-IMAGE                           KERNEL-VERSION   CONTAINER-RUNTIME
okdo-raspberrypi   Ready    control-plane,etcd,master   13m   v1.25.4+k3s1   192.168.1.180   <none>        Raspbian GNU/Linux 11 (bullseye)   5.15.76-v8+      containerd://1.6.8-k3s1
```

<img src="images/master.png"/>

![](images/master.png)

<br>
<br>

### Join the nodes

Repeat for node1 and node2

```
USER=celeghin
MASTER=192.168.1.180
NODE=192.168.1.183
CLUSTER=k3s-cluster
k3sup join --host ${NODE} --user ${USER} --server-host ${MASTER} --k3s-channel stable


NAME               STATUS   ROLES                       AGE   VERSION        INTERNAL-IP     EXTERNAL-IP   OS-IMAGE                           KERNEL-VERSION      CONTAINER-RUNTIME
minisforum-n4020   Ready    <none>                      14s   v1.25.4+k3s1   192.168.1.183   <none>        Ubuntu 22.04.1 LTS                 5.15.0-56-generic   containerd://1.6.8-k3s1
nipogi-j4125       Ready    <none>                      46s   v1.25.4+k3s1   192.168.1.182   <none>        Ubuntu 20.04.5 LTS                 5.4.0-135-generic   containerd://1.6.8-k3s1
okdo-raspberrypi   Ready    control-plane,etcd,master   16m   v1.25.4+k3s1   192.168.1.180   <none>        Raspbian GNU/Linux 11 (bullseye)   5.15.76-v8+         containerd://1.6.8-k3s1


```

## Install MetalLB Load Balancer

https://metallb.universe.tf/

```
kubectl apply -f metallb-native-0.13.7.yaml
kubectl get all -n metallb-system
```

Wait for until MetalLB is completed and create a pool of IPs, check metallb-pool.yaml:

```
kubectl apply -f metallb-pool.yaml
```

## Test MetalLB Load Balancer

```
kubectl create deployment nginx --image nginx
kubectl expose deployment nginx --type LoadBalancer --port 80 --name nginx
kubectl get service/mytest
kubectl run jvminfo --image celeguim/jvminfo:latest
kubectl expose pod/jvminfo --port 80 --target-port=8080 --type LoadBalancer
```

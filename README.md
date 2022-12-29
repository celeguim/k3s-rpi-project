## Goal

Build a light-weight bare metal kubernetes cluster with k3sup and k3s (https://github.com/alexellis/k3sup)

The k3s cluster will have a load balancer (MetalLB) and ingress controller (NGINX) working together

## Inventory

Bare metal setup

<img src="images/devices.png" width="400" />
<br>

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
```

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
```

![](images/all_nodes.png)
<br>
<br>

## Install MetalLB Load Balancer

https://metallb.universe.tf/

Current version: 0.13.7

```
kubectl apply -f metallb-native-0.13.7.yaml
kubectl get all -n metallb-system
```

Wait until MetalLB is completed (all resources) and create a pool of IPs (MetalLB needs a range of free IPs), check metallb-pool.yaml:

![](images/metallb-install.png)
<br>
<br>

```
kubectl apply -f metallb-pool.yaml
```

## Test MetalLB Load Balancer

**Test1**

```
kubectl create deployment nginx --image nginx
kubectl expose deployment nginx --type LoadBalancer --port 80 --name nginx

kubectl get services
NAME         TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
kubernetes   ClusterIP      10.43.0.1       <none>          443/TCP        35m
nginx        LoadBalancer   10.43.155.102   192.168.1.148   80:31611/TCP   57s

# The test1 service was exposed with the first external IP in the pool

```

http://192.168.1.148/
<img src="images/metallb-test1.png" width="400" />
<br>
<br>

**Test2**

```
kubectl run jvminfo --image celeguim/jvminfo:latest
kubectl expose pod/jvminfo --port 80 --target-port=8080 --type LoadBalancer
kubectl get services

NAME         TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
jvminfo      LoadBalancer   10.43.86.184    192.168.1.149   80:32494/TCP   27s
kubernetes   ClusterIP      10.43.0.1       <none>          443/TCP        41m
nginx        LoadBalancer   10.43.155.102   192.168.1.148   80:31611/TCP   7m15s

# The test2 service was exposed with the second external IP in the pool

```

http://192.168.1.149/jvminfo/
<img src="images/metallb-test2.png" width="400" />
<br>
<br>

Manual steps from validation POC stage to launch stuff using kops and kubectl.

Table of Contents
=================

  * [Table of Contents](#table-of-contents)
  * [kops quick notes](#kops-quick-notes)
    * [Installing kops](#installing-kops)
    * [Other deps: kubernetes\-cli and awscli](#other-deps-kubernetes-cli-and-awscli)
    * [Setup your AWS environment](#setup-your-aws-environment)
    * [Which DNS option to choose?](#which-dns-option-to-choose)
    * [Cluster state storage in S3](#cluster-state-storage-in-s3)
    * [Creating your first cluster](#creating-your-first-cluster)
    * [Howto save $$$ by stopping the cluster](#howto-save--by-stopping-the-cluster)
    * [Get cluster info](#get-cluster-info)
    * [Install the dashboard UI](#install-the-dashboard-ui)
    * [Invoking kops in a new shell](#invoking-kops-in-a-new-shell)
    * [Resizing an instance group](#resizing-an-instance-group)
  * [Starting a ceph deployment](#starting-a-ceph-deployment)
    * [TODOS for storage cluster deployment](#todos-for-storage-cluster-deployment)
    * [Override the default network settings](#override-the-default-network-settings)
    * [Generate keys and configuration](#generate-keys-and-configuration)
    * [Deploy Ceph Components](#deploy-ceph-components)
    * [Verify from a mon node if ceph status is OK](#verify-from-a-mon-node-if-ceph-status-is-ok)
    * [Test cephfs](#test-cephfs)
    * [Test RDB](#test-rdb)
  * [Run zibootstrapper](#run-zibootstrapper)
  * [Docker stuff](#docker-stuff)
    * [Create a snapshot image of the container](#create-a-snapshot-image-of-the-container)
    * [Tag (latest) and push your image](#tag-latest-and-push-your-image)
    * [Build an image from your Dockerfile](#build-an-image-from-your-dockerfile)
    * [Support private container registry](#support-private-container-registry)
    * [Resources](#resources)
  * [Miscellaneous stuff](#miscellaneous-stuff)
    * [Generate TOC](#generate-toc)


kops quick notes
=================

Upload this note to: https://github.com/cascadeo/ops/blob/prem/tmp/prem/kops.md

Notes for https://github.com/kubernetes/kops/blob/master/docs/aws.md

## Installing kops

Install https://github.com/kubernetes/kops/blob/master/docs/install.md

`brew update && brew install --HEAD kops`

Possible issues:

* Slow ==> Checking out branch master

Fix:

Said, woman, take it slow

It'll work itself out fine

All we need is just a ...


* Makefile:76: *** "sha1sum command is not available (on MacOS try 'brew install md5sha1sum')".  Stop.


Fix: https://github.com/kubernetes/kops/issues/1999

---

## Other deps: kubernetes-cli and awscli

I came from installing kube-aws so I think you still need to install:

* brew install kubernetes-cli

* pip install awscli

From: https://github.com/kubernetes/kops/blob/master/docs/install.md

---

## Setup your AWS environment

https://github.com/kubernetes/kops/blob/master/docs/aws.md#setup-your-environment

You should already be a member of a group called synacor-kops so you will have access to the following:

* AmazonEC2FullAccess
* AmazonRoute53FullAccess
* AmazonS3FullAccess
* IAMFullAccess
* AmazonVPCFullAccess

---

## Which DNS option to choose?

For DNS option you can have something similar to my hosted zone: https://console.aws.amazon.com/route53/home?region=us-west-2#resource-record-sets:Z2NY0C45HLICXZ

Notice this is a subdomain of cascadeo.info but it is its own Hosted Zone.

synacor-prem.cascadeo.info. 

We are executing scenario 1b. I did it manually in AWS Console.

Hints:

* In cascadeo.info hosted zone https://console.aws.amazon.com/route53/home?region=us-west-2#resource-record-sets:Z2FAMKDAVJAH2C

I have this record:

```
synacor-prem.cascadeo.info.
NS
ns-1505.awsdns-60.org. 
ns-1552.awsdns-02.co.uk. 
ns-958.awsdns-55.net. 
ns-184.awsdns-23.com.
```

The values for NS come from when I create the Hosted Zone for synacor-prem.cascadeo.info.

Dig hints:

```
Prems-MacBook-Pro:synacor fortran01$ dig synacor-prem.cascadeo.info NS

;; QUESTION SECTION:
;synacor-prem.cascadeo.info.	IN	NS

;; ANSWER SECTION:
synacor-prem.cascadeo.info. 86399 IN	NS	ns-1505.awsdns-60.org.
synacor-prem.cascadeo.info. 86399 IN	NS	ns-1552.awsdns-02.co.uk.
synacor-prem.cascadeo.info. 86399 IN	NS	ns-184.awsdns-23.com.
synacor-prem.cascadeo.info. 86399 IN	NS	ns-958.awsdns-55.net.
```

---

## Cluster state storage in S3

Followed https://github.com/kubernetes/kops/blob/master/docs/aws.md#cluster-state-storage

I am located in us-west-2.

I did not do this: https://github.com/kubernetes/kops/blob/master/docs/aws.md#sharing-an-s3-bucket-across-multiple-accounts

---

## Creating your first cluster

I did this: https://github.com/kubernetes/kops/blob/master/docs/aws.md#creating-your-first-cluster

---

## Howto save `$$$` by stopping the cluster

Hints taken from: https://github.com/kubernetes/kops/issues/1132

I set the Desired and Min of scaling groups related to Master and Nodes to 0.

To get back to the original state just execute again:

`kops update cluster --yes`

---

## Get cluster info

```
Prems-MacBook-Pro:~ fortran01$ kubectl get nodes
NAME                                          STATUS         AGE
ip-172-20-39-166.us-west-2.compute.internal   Ready,master   7m
ip-172-20-43-191.us-west-2.compute.internal   Ready          5m
ip-172-20-51-111.us-west-2.compute.internal   Ready          4m
```

```
Prems-MacBook-Pro:~ fortran01$ kops validate cluster
Using cluster from kubectl context: synacor-prem.cascadeo.info

Validating cluster synacor-prem.cascadeo.info

INSTANCE GROUPS
NAME			ROLE	MACHINETYPE	MIN	MAX	SUBNETS
master-us-west-2a	Master	m3.medium	1	1	us-west-2a
nodes			Node	t2.medium	2	2	us-west-2a

NODE STATUS
NAME						ROLE	READY
ip-172-20-39-166.us-west-2.compute.internal	master	True
ip-172-20-43-191.us-west-2.compute.internal	node	True
ip-172-20-51-111.us-west-2.compute.internal	node	True

Your cluster synacor-prem.cascadeo.info is ready
```

```
Prems-MacBook-Pro:~ fortran01$ kubectl -n kube-system get po
NAME                                                                  READY     STATUS    RESTARTS   AGE
dns-controller-2363591598-0sln2                                       1/1       Running   0          10m
etcd-server-events-ip-172-20-39-166.us-west-2.compute.internal        1/1       Running   0          10m
etcd-server-ip-172-20-39-166.us-west-2.compute.internal               1/1       Running   0          10m
kube-apiserver-ip-172-20-39-166.us-west-2.compute.internal            1/1       Running   0          11m
kube-controller-manager-ip-172-20-39-166.us-west-2.compute.internal   1/1       Running   0          11m
kube-dns-782804071-3xtt7                                              4/4       Running   0          10m
kube-dns-782804071-4f98g                                              4/4       Running   0          8m
kube-dns-autoscaler-2813114833-ns5qk                                  1/1       Running   0          10m
kube-proxy-ip-172-20-39-166.us-west-2.compute.internal                1/1       Running   0          10m
kube-proxy-ip-172-20-43-191.us-west-2.compute.internal                1/1       Running   0          8m
kube-proxy-ip-172-20-51-111.us-west-2.compute.internal                1/1       Running   0          8m
kube-scheduler-ip-172-20-39-166.us-west-2.compute.internal            1/1       Running   0          9m
```

---

## Install the dashboard UI

https://github.com/kubernetes/kops/blob/master/docs/addons.md#dashboard

---

## Invoking kops in a new shell

Recall the cluster state is stored in S3.

```
Prems-MacBook-Pro:~ fortran01$ export KOPS_STATE_STORE=s3://synacor-prem-2017030201
Prems-MacBook-Pro:~ fortran01$ kops validate cluster
```

---

## Resizing an instance group

Resizing an instance group from https://github.com/kubernetes/kops/blob/master/docs/instance_groups.md#resize-an-instance-group


```
Prems-MacBook-Pro:kubernetes fortran01$ kops get instancegroups
Using cluster from kubectl context: synacor-prem.cascadeo.info

NAME			ROLE	MACHINETYPE	MIN	MAX	SUBNETS
master-us-west-2a	Master	m3.medium	1	1	us-west-2a
nodes			Node	t2.medium	2	2	us-west-2a
```


```
Prems-MacBook-Pro:kubernetes fortran01$ kops edit ig nodes
Using cluster from kubectl context: synacor-prem.cascadeo.info
```

```
Prems-MacBook-Pro:kubernetes fortran01$ kops update cluster
Using cluster from kubectl context: synacor-prem.cascadeo.info

I0303 17:59:15.035763    5741 executor.go:91] Tasks: 0 done / 56 total; 27 can run
I0303 17:59:18.604594    5741 executor.go:91] Tasks: 27 done / 56 total; 12 can run
I0303 17:59:19.759307    5741 executor.go:91] Tasks: 39 done / 56 total; 15 can run
I0303 17:59:22.978368    5741 executor.go:91] Tasks: 54 done / 56 total; 2 can run
I0303 17:59:23.248406    5741 executor.go:91] Tasks: 56 done / 56 total; 0 can run
Will modify resources:
  AutoscalingGroup/master-us-west-2a.masters.synacor-prem.cascadeo.info
  	Tags                	 {Env: prod, KubernetesCluster: synacor-prem.cascadeo.info, Name: master-us-west-2a.masters.synacor-prem.cascadeo.info, Project: GO, Team: GO, k8s.io/role/master: 1, AutoTag_Creator: arn:aws:iam::092658368226:user/prem, BusinessUnit: Marketplace} -> {k8s.io/role/master: 1, Name: master-us-west-2a.masters.synacor-prem.cascadeo.info, KubernetesCluster: synacor-prem.cascadeo.info}

  AutoscalingGroup/nodes.synacor-prem.cascadeo.info
  	MinSize             	 2 -> 4
  	MaxSize             	 2 -> 4
  	Tags                	 {Env: prod, KubernetesCluster: synacor-prem.cascadeo.info, Name: nodes.synacor-prem.cascadeo.info, Project: GO, Team: GO, k8s.io/role/node: 1, AutoTag_Creator: arn:aws:iam::092658368226:user/prem, BusinessUnit: Marketplace} -> {k8s.io/role/node: 1, Name: nodes.synacor-prem.cascadeo.info, KubernetesCluster: synacor-prem.cascadeo.info}

  EBSVolume/a.etcd-events.synacor-prem.cascadeo.info
  	Tags                	 {Name: a.etcd-events.synacor-prem.cascadeo.info, BusinessUnit: Marketplace, Project: GO, KubernetesCluster: synacor-prem.cascadeo.info, Env: prod, AutoTag_Creator: arn:aws:iam::092658368226:user/prem, k8s.io/etcd/events: a/a, k8s.io/role/master: 1, Team: GO} -> {k8s.io/etcd/events: a/a, k8s.io/role/master: 1, Name: a.etcd-events.synacor-prem.cascadeo.info, KubernetesCluster: synacor-prem.cascadeo.info}

  EBSVolume/a.etcd-main.synacor-prem.cascadeo.info
  	Tags                	 {k8s.io/etcd/main: a/a, Env: prod, AutoTag_Creator: arn:aws:iam::092658368226:user/prem, k8s.io/role/master: 1, Team: GO, KubernetesCluster: synacor-prem.cascadeo.info, Project: GO, BusinessUnit: Marketplace, Name: a.etcd-main.synacor-prem.cascadeo.info} -> {k8s.io/etcd/main: a/a, k8s.io/role/master: 1, Name: a.etcd-main.synacor-prem.cascadeo.info, KubernetesCluster: synacor-prem.cascadeo.info}

Must specify --yes to apply changes
```

```
Prems-MacBook-Pro:kubernetes fortran01$ kops update cluster --yes
```


# Starting a ceph deployment

## TODOS for storage cluster deployment

* Make SkyDNS resolution work: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#skydns-resolution
* This example does not survive Kubernetes cluster restart! The Monitors need persistent storage. This is not covered here. https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#warning
* k8s nodes should already have the following installed `ceph-fs-common ceph-common`: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#ceph-and-rbd-utilities-installed-on-the-nodes
* 

The directory below is from https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes

## Override the default network settings

From: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#override-the-default-network-settings

The network values below I got from looking at the Pod IPs (when I first launched a non-working deployment). I think there is a way to get the Pod network CIDR allocation.

```
Prems-MacBook-Pro:kubernetes fortran01$ export osd_cluster_network=100.96.0.0/16
Prems-MacBook-Pro:kubernetes fortran01$ export osd_public_network=100.96.0.0/16
```

## Generate keys and configuration

From: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#generate-keys-and-configuration

```
Prems-MacBook-Pro:kubernetes fortran01$ cd generator
Prems-MacBook-Pro:generator fortran01$ ./generate_secrets.sh all `./generate_secrets.sh fsid`
Prems-MacBook-Pro:generator fortran01$ kubectl create namespace ceph
namespace "ceph" created
Prems-MacBook-Pro:generator fortran01$ kubectl create secret generic ceph-conf-combined --from-file=ceph.conf --from-file=ceph.client.admin.keyring --from-file=ceph.mon.keyring --namespace=ceph
secret "ceph-conf-combined" created
Prems-MacBook-Pro:generator fortran01$ kubectl create secret generic ceph-bootstrap-rgw-keyring --from-file=ceph.keyring=ceph.rgw.keyring --namespace=ceph
secret "ceph-bootstrap-rgw-keyring" created
Prems-MacBook-Pro:generator fortran01$ kubectl create secret generic ceph-bootstrap-mds-keyring --from-file=ceph.keyring=ceph.mds.keyring --namespace=ceph
secret "ceph-bootstrap-mds-keyring" created
Prems-MacBook-Pro:generator fortran01$ kubectl create secret generic ceph-bootstrap-osd-keyring --from-file=ceph.keyring=ceph.osd.keyring --namespace=ceph
secret "ceph-bootstrap-osd-keyring" created
Prems-MacBook-Pro:generator fortran01$ kubectl create secret generic ceph-client-key --from-file=ceph-client-key --namespace=ceph
secret "ceph-client-key" created
Prems-MacBook-Pro:generator fortran01$ cd ..
```

## Deploy Ceph Components

From: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#deploy-ceph-components

```
Prems-MacBook-Pro:kubernetes fortran01$ kubectl create \
> -f ceph-mds-v1-dp.yaml \
> -f ceph-mon-v1-svc.yaml \
> -f ceph-mon-v1-dp.yaml \
> -f ceph-mon-check-v1-dp.yaml \
> -f ceph-osd-v1-ds.yaml \
> --namespace=ceph
deployment "ceph-mds" created
service "ceph-mon" created
deployment "ceph-mon" created
deployment "ceph-mon-check" created
daemonset "ceph-osd" created

Prems-MacBook-Pro:kubernetes fortran01$ kubectl get all --namespace=ceph
NAME                                 READY     STATUS    RESTARTS   AGE
po/ceph-mds-2743106415-5958n         0/1       Running   2          30s
po/ceph-mon-2416973846-27zs1         1/1       Running   0          29s
po/ceph-mon-2416973846-6hwf1         1/1       Running   0          29s
po/ceph-mon-2416973846-tvl8j         1/1       Running   0          29s
po/ceph-mon-check-1896585268-qc54k   1/1       Running   0          28s
po/ceph-osd-497v8                    0/1       Running   2          28s
po/ceph-osd-l0gm7                    0/1       Running   2          28s
po/ceph-osd-phzpb                    0/1       Running   2          28s

NAME           CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
svc/ceph-mon   None         <none>        6789/TCP   29s

NAME                    DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/ceph-mds         1         1         1            0           30s
deploy/ceph-mon         3         3         3            3           29s
deploy/ceph-mon-check   1         1         1            1           29s

NAME                           DESIRED   CURRENT   READY     AGE
rs/ceph-mds-2743106415         1         1         0         30s
rs/ceph-mon-2416973846         3         3         3         29s
rs/ceph-mon-check-1896585268   1         1         1         29s
Prems-MacBook-Pro:kubernetes fortran01$ kubectl get all --namespace=ceph
NAME                                 READY     STATUS    RESTARTS   AGE
po/ceph-mds-2743106415-5958n         1/1       Running   2          1m
po/ceph-mon-2416973846-27zs1         1/1       Running   0          1m
po/ceph-mon-2416973846-6hwf1         1/1       Running   0          1m
po/ceph-mon-2416973846-tvl8j         1/1       Running   0          1m
po/ceph-mon-check-1896585268-qc54k   1/1       Running   0          1m
po/ceph-osd-497v8                    1/1       Running   2          1m
po/ceph-osd-l0gm7                    1/1       Running   2          1m
po/ceph-osd-phzpb                    1/1       Running   2          1m

NAME           CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
svc/ceph-mon   None         <none>        6789/TCP   1m

NAME                    DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deploy/ceph-mds         1         1         1            1           1m
deploy/ceph-mon         3         3         3            3           1m
deploy/ceph-mon-check   1         1         1            1           1m

NAME                           DESIRED   CURRENT   READY     AGE
rs/ceph-mds-2743106415         1         1         1         1m
rs/ceph-mon-2416973846         3         3         3         1m
rs/ceph-mon-check-1896585268   1         1         1         1m
```


## Verify from a mon node if ceph status is OK

Notice HEALTH_OK below.

```
Prems-MacBook-Pro:kubernetes fortran01$ kubectl exec -it --namespace=ceph ceph-mon-2416973846-27zs1 -- /bin/bash
root@ceph-mon-2416973846-27zs1:/# ceph status
    cluster 69d40a98-3ce9-4732-8685-f0789bb09ab0
     health HEALTH_OK
     monmap e2: 3 mons at {ceph-mon-2416973846-27zs1=100.96.14.9:6789/0,ceph-mon-2416973846-6hwf1=100.96.18.7:6789/0,ceph-mon-2416973846-tvl8j=100.96.17.5:6789/0}
            election epoch 8, quorum 0,1,2 ceph-mon-2416973846-27zs1,ceph-mon-2416973846-tvl8j,ceph-mon-2416973846-6hwf1
      fsmap e5: 1/1/1 up {0=mds-ceph-mds-2743106415-5958n=up:active}
        mgr no daemons active
     osdmap e9: 3 osds: 3 up, 3 in
            flags sortbitwise,require_jewel_osds,require_kraken_osds
      pgmap v32: 80 pgs, 3 pools, 2148 bytes data, 20 objects
            30294 MB used, 26891 MB / 57186 MB avail
                  80 active+clean
root@ceph-mon-2416973846-27zs1:/# exit
exit
```

Under Workloads > Deployments in the dashboard (example: https://api.synacor-prem.cascadeo.info/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard/#/deployment?namespace=ceph), you should see at least the following abstractions.

https://github.com/cascadeo/ops/tree/prem/tmp/prem/screenshots/ceph-k8s-0332 (if you see the ceph-cephfs-test pod error, most probably your `ceph status` health is NOT OK. Most probably you have not overriden the default network settings. See above)

## Test cephfs

The test below does not use SkyDNS resolution so modify the ceph-mon.ceph host to match the IP address of one of your ceph-mon pods.

```
Prems-MacBook-Pro:kubernetes fortran01$ kubectl create -f ceph-cephfs-test.yaml --namespace=ceph
pod "ceph-cephfs-test" created

Prems-MacBook-Pro:kubernetes fortran01$ kubectl exec -it --namespace=ceph ceph-cephfs-test df
Filesystem           1K-blocks      Used Available Use% Mounted on
overlay               19519572   4017524  14563380  22% /
tmpfs                  2024668         0   2024668   0% /dev
tmpfs                  2024668         0   2024668   0% /sys/fs/cgroup
/dev/xvda1            19519572   4017524  14563380  22% /dev/termination-log
100.96.14.9:6789,100.96.18.7:6789,100.96.17.5:6789:/
                      58556416  31023104  27533312  53% /mnt/cephfs
/dev/xvda1            19519572   4017524  14563380  22% /etc/resolv.conf
/dev/xvda1            19519572   4017524  14563380  22% /etc/hostname
/dev/xvda1            19519572   4017524  14563380  22% /etc/hosts
shm                      65536         0     65536   0% /dev/shm
tmpfs                  2024668        12   2024656   0% /var/run/secrets/kubernetes.io/serviceaccount
tmpfs                  2024668         0   2024668   0% /proc/kcore
tmpfs                  2024668         0   2024668   0% /proc/timer_list
tmpfs                  2024668         0   2024668   0% /proc/timer_stats
tmpfs                  2024668         0   2024668   0% /proc/sched_debug
```

## Test RDB

From: https://github.com/cascadeo/ceph-docker/tree/master/examples/kubernetes#mounting-a-ceph-rbd-in-a-pod

```
Prems-MacBook-Pro:kubernetes fortran01$ export PODNAME=`kubectl get pods --selector="app=ceph,daemon=mon" --output=template --template="{{with index .items 0}}{{.metadata.name}}{{end}}" --namespace=ceph`
Prems-MacBook-Pro:kubernetes fortran01$ kubectl exec -it $PODNAME --namespace=ceph -- rbd create ceph-rbd-test --size 10M
Prems-MacBook-Pro:kubernetes fortran01$ kubectl exec -it $PODNAME --namespace=ceph -- rbd info ceph-rbd-test
rbd image 'ceph-rbd-test':
	size 10240 kB in 3 objects
	order 22 (4096 kB objects)
	block_name_prefix: rbd_data.10ab2ae8944a
	format: 2
	features: layering
	flags:
```

# Run zibootstrapper

`$ docker run -i -t --env-file ./env.list cascadeo/zibootstrapper /bin/bash`

# Docker stuff

## Create a snapshot image of the container

`$ docker commit <CONTAINER ID> cascadeo/kops:<TIMESTAMP LIKE 2017031400>`

## Tag (latest) and push your image

```
$ docker images
... get the container image ID of the snapshot image from above

$ docker tag <CONTAINER IMAGE ID> cascadeo/kops:latest

$ docker login
Login with your Docker ID to push and pull images from Docker Hub. If you don't have a Docker ID, head over to https://hub.docker.com to create one.
Username: fortran01
Password:
Login Succeeded

$ docker push cascadeo/kops
The push refers to a repository [docker.io/cascadeo/kops]
7ea37f72f1ab: Pushed
62f62f75eaa2: Layer already exists
d17d48b2382a: Layer already exists
2017031400: digest: sha256:ad8043df5703c8dd95b92c787c2308157fbacccbfafeb45cb5a91359dee5fabf size: 954
7ea37f72f1ab: Layer already exists
62f62f75eaa2: Layer already exists
d17d48b2382a: Layer already exists
latest: digest: sha256:ad8043df5703c8dd95b92c787c2308157fbacccbfafeb45cb5a91359dee5fabf size: 954
```

Verify tags in https://hub.docker.com/r/cascadeo/kops/tags/.

## Build an image from your Dockerfile

```
$ cd <where Dockerfile is>
$ docker build -t cascadeo/zibootstrapper .
```

## Support private container registry

* http://stackoverflow.com/a/36974280/422842 (did _not_ add this line `command: [ "echo", "SUCCESS" ]`)

## Resources

* https://docs.docker.com/engine/reference/commandline/commit/#examples
* https://docs.docker.com/engine/getstarted/step_six/
* https://docs.docker.com/engine/getstarted/step_four/#step-2-build-an-image-from-your-dockerfile

# Miscellaneous stuff

## Generate TOC
`$ gh-md-toc ~/Dropbox/notes/kops.md`

## Docker images in https://console.aws.amazon.com/ecs/home?region=us-east-1#/repositories
1. zimbra-ldap -> 092658368226.dkr.ecr.us-east-1.amazonaws.com/synacor/zimbra-ldap
2. zimbra-mailbox -> 092658368226.dkr.ecr.us-east-1.amazonaws.com/synacor/zimbra-mailbox
3. zimbra-mta -> 092658368226.dkr.ecr.us-east-1.amazonaws.com/synacor/zimbra-mta
4. zimbra-proxy -> 092658368226.dkr.ecr.us-east-1.amazonaws.com/synacor/zimbra-proxy

## Assumption: There is already a running cluster

## Order of installation:
	1. zimbra-ldap
	2. zimbra-mail box
	3. zimbra-mta
	4. zimbra-proxy

## Installation: (with kubectl create -f <yaml file>)
  1. Run 'aws ecr get-login | sh -' to set ~/.docker/config.json
	2. create registry key - kubectl create -f myregistry.yaml
  3. create configmaps (ldap, mailbox, mta, proxy) and PersistentVolumes (see readme in PersistentVolumes folder)
	4. create the headless/internal services first per installation
	5. create the stateful sets
	6. crate the loadbalancers/external services

## Issues:
	1. provided domain in the installation is being deleted after the complete installation
	  1. Run the following on mailbox pod as workaround
		```
		zmprov cd test.local
		zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
		```
	2. mta is not yet configured to send email to test domain provided
	3. run the following to force 'open' ports for http/https (mailbox and proxy)
	```
	/opt/zimbra/libexec/zmproxyconfig -e -w -o -H <hostname>
	```

## NOTE: issues 1 and 3 will be included in the installation

For now, please do the following:

1. ssh in to mailbox-{number of pod} and proxy-{number of pod}

2. run /opt/zimbra/libexec/zmproxyconfig -e -w -o -H <hostname> (e.g of hostname - mailbox-0.mailbox-service.default.svc.cluster.local and proxy-0.proxy-service.default.svc.cluster.local)

Example in mailbox:

```
# kubectl exec -it mailbox-0 -- /bin/bash
[root@mailbox-0 /]# su - zimbra
[zimbra@mailbox-0 ~]$  /opt/zimbra/libexec/zmproxyconfig -e -w -o -H mailbox-0.mailbox-service.default.svc.cluster.local
```

Example in proxy:

```
# kubectl exec -it proxy-0 -- /bin/bash
[root@proxy-0 /]# su - zimbra
[zimbra@proxy-0 ~]$ /opt/zimbra/libexec/zmproxyconfig -e -w -o -H proxy-0.proxy-service.default.svc.cluster.local
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found

# Not sure if we need to iterate for other proxy pods?? -Prem

# kubectl exec -it proxy-1 -- /bin/bash
[root@proxy-1 /]# su - zimbra
[zimbra@proxy-1 ~]$ /opt/zimbra/libexec/zmproxyconfig -e -w -o -H proxy-1.proxy-service.default.svc.cluster.local
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
[] INFO: keystore not present
[] WARN: backup keystore not found
```

3. ssh to mailbox-{number of pod}
4. run the following

```
zmprov cd test.local
zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
```

Example:

```
# kubectl exec -it mailbox-0 -- /bin/bash
[root@mailbox-0 /]# su - zimbra
[zimbra@mailbox-0 ~]$ zmprov cd test.local
671e8c56-1427-46c6-93c7-daa5561192c6
[zimbra@mailbox-0 ~]$ zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
a6845dbc-cf3a-401b-ac68-aabdaf64c80e
```

## Testing
After doing extra steps above
1. get the load balancer endpoint of proxy (describe the service) then browse to https://<lb-endpoint> for client
2. get the load balancer endpoint of mailbox (describe the service) then browse to https://<lb-endpoint>:7071 for admin
3. login using testadmin@test.local test1234 credentials

## Testing sending email outside
1. register domain in zimbra admin
2. make CNAME record for elb endpoint of MTA
3. make mx record pointing to the CNAME of step number 2

## Step by Step installation
1. aws configure (enter your account access and secret keys)
2. Generate AWS myregistrykey
2.1 aws ecr get-login | sh -
2.2 cat ~/.docker/config.json | base64 -w 0
2.3 copy paste the above output to zimbra/myregistry.yaml (.dockerconfigjson field)
2.4 kubectl create -f myregistry.yaml (to create secret)
2.5 kubectl get secrets (to check)
3. create configmaps and persistent volumes (for mailbox)
3.1 kubectl create -f zimbra/configmap/zimbra-ldap.yaml
3.2 kubectl create -f zimbra/configmap/zimbra-mailbox.yaml
3.3 kubectl create -f zimbra/configmap/zimbra-mta.yaml
3.4 kubectl create -f zimbra/configmap/zimbra-proxy.yaml
3.5 kubectl get configmaps
3.6 kubectl create -f zimbra/persistentvolumes/pv.yaml
3.7 kubectl create -f zimbra/persistentvolumes/pvc.yaml
3.8 kubectl get pv
4. create zimbra-ldap service
4.1 kubectl create -f zimbra/zimbra-ldap/yaml/internal-ldap-service.yaml
4.2 kubectl create -f zimbra/zimbra-ldap/yaml/statefulset.yaml
4.3 kubectl logs -f ldap-0 (wait until it is finished)
4.4 kubectl create -f zimbra/zimbra-ldap/yaml/external-ldap-service.yaml
4.5 kubectl get services
5. create zimbra-mailbox service
5.1 kubectl create -f zimbra/zimbra-mailbox/yaml/internal-mailbox-service.yaml
5.2 kubectl create -f zimbra/zimbra-mailbox/yaml/statefulset.yaml
5.3 kubectl logs -f mailbox-0 (wait until it is finished)
5.4 kubectl create -f zimbra/zimbra-mailbox/yaml/external-mailbox-service.yaml
5.5 kubectl create -f zimbra/zimbra-mailbox/yaml/client-service.yaml
5.6 kubectl create -f zimbra/zimbra-mailbox/yaml/loadbalancer.yaml
5.7 kubectl get services
6. create zimbra-mta service
6.1 kubectl create -f zimbra/zimbra-mta/yaml/internal-mta-service.yaml
6.2 kubectl create -f zimbra/zimbra-mta/yaml/statefulset.yaml
6.3 kubectl logs -f mta-0 (wait until it is finished)
6.4 kubectl create -f zimbra/zimbra-mta/yaml/external-mta-service.yaml
6.5 kubectl get services
7. create zimbra-proxy service
7.1 kubectl create -f zimbra/zimbra-proxy/yaml/internal-proxy-service.yaml
7.2 kubectl create -f zimbra/zimbra-proxy/yaml/statefulset.yaml
7.3 kubectl logs -f proxy-0 (wait until it is finished)
7.4 kubectl create -f zimbra/zimbra-proxy/yaml/external-proxy-service.yaml
7.5 kubectl get services
8. create domain and admin account, open service ports
8.1 kubectl exec -it mailbox-0 -- /bin/bash
8.2 sudo su zimbra
8.3 zmprov cd test.local
8.4 zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
8.5 /opt/zimbra/libexec/zmproxyconfig -e -w -o -H mailbox-0.mailbox-service.default.svc.cluster.local
8.6 exit on mailbox pod
8.7 kubectl exec -it proxy-0 -- /bin/bash
8.8 sudo su zimbra
8.9 /opt/zimbra/libexec/zmproxyconfig -e -w -o -H proxy-0.mailbox-service.default.svc.cluster.local
9. create MX record
9.1 kubectl describe service mta-service-external
9.2 create CNAME record in route 53 under the cluster hosted zone, for LoadBalancer endpoint at 9.1
9.3 in the same hosted zone, create MX record pointing to the CNAME at 9.2
10. Test
10.1 kubectl describe service mb-service-2
10.2 browse the LoadBalancer endpoint for admin
10.3 kubectl describe service external-proxy-service
10.4 browse the LoadBalancer endpoint for user

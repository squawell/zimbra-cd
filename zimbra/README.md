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
1. setup
	1. Install prereqs
		1. apt-get update && apt-get upgrade
		2. apt-get install python-pip
		3. pip install awscli
		4. wget -qO- https://get.docker.com/ | sh
		5. pull repo - git clone https://<git-user>@github.com/cascadeo/synacor.git
		6. cd synacor/
	2. aws configure (enter your account access and secret keys)
2. Generate AWS myregistrykey
	1. aws ecr get-login | sh -
	2. cat ~/.docker/config.json | base64 -w 0
	3. copy paste the above output to zimbra/myregistry.yaml (.dockerconfigjson field)
	4. kubectl create -f zimbra/myregistry.yaml (to create secret)
	5. kubectl get secrets (to check)
3. create configmaps and persistent volumes (for mailbox)
	1. kubectl create -f zimbra/configmap/zimbra-ldap.yaml
	2. kubectl create -f zimbra/configmap/zimbra-mailbox.yaml
	3. kubectl create -f zimbra/configmap/zimbra-mta.yaml
	4. kubectl create -f zimbra/configmap/zimbra-proxy.yaml
	5. wait untill AGE is no longer <invalid> then - kubectl get configmaps
	6. create EBS volumes in availability zone that match the region on aws configure - aws ec2 create-volume --size 10 --availability-zone us-west-2a
	7. note volume ID from the last command and edit zimbra/persistentvolumes/pv.yaml volumeID value
	8. kubectl create -f zimbra/persistentvolumes/pv.yaml
	9. kubectl create -f zimbra/persistentvolumes/pvc.yaml
	10. kubectl get pv
4. create zimbra-ldap service
	1. kubectl create -f zimbra/zimbra-ldap/yaml/internal-ldap-service.yaml
	2. kubectl create -f zimbra/zimbra-ldap/yaml/statefulset.yaml
	3. kubectl logs -f ldap-0 (Wait until "Server is ready" appears in the log)
	4. kubectl create -f zimbra/zimbra-ldap/yaml/external-ldap-service.yaml
	5. Wait until AGE is no longer <invalid> then - kubectl get services
5. create zimbra-mailbox service
	1. kubectl create -f zimbra/zimbra-mailbox/yaml/internal-mailbox-service.yaml
	2. kubectl create -f zimbra/zimbra-mailbox/yaml/statefulset.yaml
	3. kubectl logs -f mailbox-0 (Wait until "Server is ready" appears in the log)
	4. kubectl create -f zimbra/zimbra-mailbox/yaml/external-mailbox-service.yaml
	5. kubectl create -f zimbra/zimbra-mailbox/yaml/client-service.yaml
	6. kubectl create -f zimbra/zimbra-mailbox/yaml/loadbalancer.yaml
	7. Wait until AGE is no longer <invalid> then - kubectl get services
6. create zimbra-mta service
	1. kubectl create -f zimbra/zimbra-mta/yaml/internal-mta-service.yaml
	2. kubectl create -f zimbra/zimbra-mta/yaml/statefulset.yaml
	3. kubectl logs -f mta-0 (Wait until "Server is ready" appears in the log)
	4. kubectl create -f zimbra/zimbra-mta/yaml/external-mta-service.yaml
	5. Wait until AGE is no longer <invalid> then - kubectl get services
7. create zimbra-proxy service
	1. kubectl create -f zimbra/zimbra-proxy/yaml/internal-proxy-service.yaml
	2. kubectl create -f zimbra/zimbra-proxy/yaml/statefulset.yaml
	3. kubectl logs -f proxy-0 (Wait until "Server is ready" appears in the log)
	4. kubectl create -f zimbra/zimbra-proxy/yaml/external-proxy-service.yaml
	5. Wait until AGE is no longer <invalid> then - kubectl get services
8. create domain and admin account, open service ports
	1. kubectl exec -it mailbox-0 -- /bin/bash
	2. sudo su zimbra
	3. zmprov cd test.local
	4. zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
	5. /opt/zimbra/libexec/zmproxyconfig -e -w -o -H mailbox-0.mailbox-service.default.svc.cluster.local
	6. exit on mailbox pod
	7. kubectl exec -it proxy-0 -- /bin/bash
	8. sudo su zimbra
	9. /opt/zimbra/libexec/zmproxyconfig -e -w -o -H proxy-0.proxy-service.default.svc.cluster.local
	10. Exit proxy pod
9. create MX record
	1. kubectl describe service mta-service-external (note ELB endpoint)
	2. create CNAME record in route 53 under the cluster hosted zone, for LoadBalancer endpoint at 9.1
	3. in the same hosted zone, create MX record pointing to the CNAME at 9.2
	```
	aws route53 list-hosted-zones
        {
            "ResourceRecordSetCount": 6,
            "CallerReference": "2E785FA4-58CB-1360-85AF-03B8389CC8BD",
            "Config": {
                "PrivateZone": false
            },
            "Id": "/hostedzone/ZSUPABGIX9RM5",
            "Name": "synacor-leo.cascadeo.info."
        }
	-> get zone ID
	zone1=ZSUPABGIX9RM5
	-> test retrieve
	aws route53 get-hosted-zone --id $zone1
	-> create route53 json
	vi zimbra-route53.json
	{
	  "Changes": [
	    {
	      "Action": "CREATE",
	      "ResourceRecordSet": {
	        "Name": "zimbra.synacor-leo.cascadeo.info",
	        "Type": "CNAME",
	        "TTL": 60,
	        "ResourceRecords": [
	          {
	            "Value": "ac934e06c28df11e7acbf02f03ad12d8-1260158492.us-west-2.elb.amazonaws.com"
	          }
	        ]
	      }
	    },
	    {
	      "Action": "CREATE",
	      "ResourceRecordSet": {
	        "Name": "mail.synacor-leo.cascadeo.info",
	        "Type": "MX",
	        "TTL": 60,
	        "ResourceRecords": [
	          {
	            "Value": "10 zimbra.synacor-leo.cascadeo.info."
	          },
	          {
	            "Value": "20 zimbra.synacor-leo.cascadeo.info."
	          }
	        ]
	      }
	    }
	  ]
	}
	-> update record sets
	aws route53 change-resource-record-sets --hosted-zone-id $zone1 --change-batch file://zimbra-route53.json
	{
	    "ChangeInfo": {
	        "Status": "PENDING",
	        "SubmittedAt": "2017-04-24T12:21:40.743Z",
	        "Id": "/change/C22U6VR1ETME69"
	    }
	}
	-> query change and wait until status=INSYNC
	aws route53 get-change --id /change/C22U6VR1ETME69
	```
10. Test
	1. kubectl describe service mb-service-2
	2. browse the LoadBalancer endpoint for admin - from ELB endpoint and port (7071) in 10.1
	3. kubectl describe service proxy-service-external
	4. browse the LoadBalancer endpoint for user - from ELB endpoint and port (443/https) in 10.3
	5. register your domain on zimbra
		1. kubectl exec -it mailbox-0 -- /bin/bash
		2. sudo su zimbra
		3. zmprov cd synacor-leo.cascadeo.info (zmprov cd domain)
		4. zmprov ca admin@synacor-leo.cascadeo.info test1234 zimbraIsAdminAccount TRUE (zmprov ca admin@domain password zimbraIsAdminAccount TRUE)
		5. browse to the Load Balancer endpoint on step 10.4 and login using the account on 10.5.4
		6. send and receive email

# Zimbra 8.7.7

## Docker images in https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/repositories
1. zimbra-ldap -> 294256424338.dkr.ecr.us-west-2.amazonaws.com/zimbra-ldap
2. zimbra-mailbox -> 294256424338.dkr.ecr.us-west-2.amazonaws.com/zimbra-mailbox
3. zimbra-mta -> 294256424338.dkr.ecr.us-west-2.amazonaws.com/zimbra-mta
4. zimbra-proxy -> 294256424338.dkr.ecr.us-west-2.amazonaws.com/zimbra-proxy

## Building image:
0) docker is setup on your machine & aws-cli is installed
    - aws configure //NOT NEEDED IF BUILD HOST HAS IAM ROLE TO ALLOW PUSH TO REGISTRY
	- aws ecr get-login --no-include-email //output is docker login command, copy the output and execute it
1) for each folder [zimbra-ldap, zimbra-mailbox, zimbra-mta, zimbra-proxy]
    - cd $folder
	- export REGISTRY=294256424338.dkr.ecr.us-west-2.amazonaws.com
	- docker build -t $REGISTRY/$folder:latest .
	- docker push $REGISTRY/$folder:latest

## Assumption: There is already a running cluster

## Order of installation:
	1. zimbra-ldap
	2. zimbra-mailbox
	3. zimbra-mta
	4. zimbra-proxy


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
	1. kubectl describe service proxy-service-external
	2. browse the LoadBalancer endpoint for user - from ELB endpoint and port (443/https) in 10.1
	3. browse the LoadBalancer endpoint for user - from ELB endpoint and port (9071/https) in 10.1
	4. register your domain on zimbra
		1. kubectl exec -it mailbox-0 -- /bin/bash
		2. sudo su zimbra
		3. zmprov cd synacor-leo.cascadeo.info (zmprov cd domain)
		4. zmprov ca admin@synacor-leo.cascadeo.info test1234 zimbraIsAdminAccount TRUE (zmprov ca admin@domain password zimbraIsAdminAccount TRUE)
		5. browse to the Load Balancer endpoint on step 10.2 and login using the account on 10.4.4
		6. send and receive email

		
TODO:
- cleanup of unnecessary files
- template the yamls (in progress)

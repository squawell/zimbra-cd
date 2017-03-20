

## Assumption: There is already a running cluster

## Order of installation:
	1. zimbra-ldap
	2. zimbra-mail box
	3. zimbra-mta
	4. zimbra-proxy

## Installation:
	1. create the headless services first per installation
	2. create the stateful sets
	3. crate the loadbalancers services

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
For now, please do the following
1. ssh in to mailbox-{number of pod} and proxy-{number of pod}
2. run /opt/zimbra/libexec/zmproxyconfig -e -w -o -H <hostname> (e.g of hostname - mailbox-0.mailbox-service.default.svc.cluster.local and proxy-0.proxy-service.default.svc.cluster.local)
3. ssh to mailbox-{number of pod}
4. run the following
```
zmprov cd test.local
zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
```

current dockerhub repos
1. zimbra-ldap -> cascadeo/zimbra-ldap:v1
2. zimbra-mailbox -> cascadeo/zimbra-mailbox:v1
3. zimbra-mta -> cascadeo/zimbra-mta:v1
4. zimbra-proxy -> cascadeo/zimbra-proxy:v1

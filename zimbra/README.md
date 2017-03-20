

# Assumption: There is already a running cluster

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

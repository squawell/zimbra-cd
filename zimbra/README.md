Assumption: There is already a running cluster

Order of installation:
	a. zimbra-ldap
	b. zimbra-mail box
	c. zimbra-mta
	d. zimbra-proxy

Installation:
	a. create the headless services first per installation
	b. create the stateful sets
	c. crate the loadbalancers services

Issues:
	a. provided domain in the installation is being deleted after the complete installation
		a.1 Run the following on mailbox pod as workaround
		```
		zmprov cd test.local
		zmprov ca testadmin@test.local test1234 zimbraIsAdminAccount TRUE
		```
	b. mta is not yet configured to send email to test domain provided


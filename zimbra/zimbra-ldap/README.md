# zimbra-ldap MMR mode - 2 master set-up

Create the ldap statefulset.
Wait until first master is created (ldap-0) then scale the ldap statefulset to replica=2  (eg kubectl scale statefulsets ldap --replicas=2)

# zimbra-ldap MMR mode - 2 master set-up

On the lowest master pod (ldap-0)
```
$ ./libexec/zmldapenable-mmr -s 1 -m ldap://ldap-1.ldap-service.default.svc.cluster.local:389/
$ zmlocalconfig -e ldap_master_url="ldap://ldap-0.ldap-service.default.svc.cluster.local:389 ldap://ldap-1.ldap-service.default.svc.cluster.local:389"
$ zmlocalconfig -e ldap_url="ldap://ldap-0.ldap-service.default.svc.cluster.local:389 ldap://ldap-1.ldap-service.default.svc.cluster.local:389"
$ zmcontrol restart
```

Manual commands after 2nd ldap master is installed
(tbd)

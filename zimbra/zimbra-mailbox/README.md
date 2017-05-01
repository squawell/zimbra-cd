# zimbra-mailbox

## Scaling-up Zimbra Mailbox
  1. “New” users can be assigned to newly spinned pod
  2. Dynamic assignment

## Scaling-down Zimbra Mailbox
  1. Users in existing mailbox need to be assigned to “existing” mailboxes pod
  2. To determine users on existing mailbox - all_accounts=`zmprov -l gaa`;
  3. run movemailbox.sh on zimbra/zimbra-mailbox/ as zimbra user to migrate from one mailbox to another
  4. On scaling down, users will be migrated from high to low stateful pod addressing scheme (e.g from mailbox-2 to mailbox-1)

## Testing (Assumption: There is already a running cluster with all zimbra pods running)
  1. Create domain and user on mailbox pod (1 or 2) and send receive email
  2. kubectl exec -it mailbox-0 -- bash
  3. sudo su zimbra
  4. zmprov cd zimbra-k8s.cascadeo.info
  5. zmprov ca arvin@zimbra-k8s.cascadeo.info test1234 zimbraIsAdminAccount TRUE
  6. exit from pod (exit)
  7. kubectl describe service proxy-service-external (run from workstation)
  8. browse the LoadBalancer endpoint for user from step 1.6 using ssl (https/:443) (e.g. ae6a1ba792bcb11e798cc06d81d932b9-1863829251.us-west-1.elb.amazonaws.com)
  9. send/receive email from the web interface provided
  10. know what mailbox pod is the user created
  11. back to workstation - kubectl describe service mb-service-2
  12. browse the LoadBalancer endpoint for admin - from ELB endpoint and port (7071) in 1.9
  13. login the created account on 1.4
  14. manage -> accounts then double click the account created on 1.4 and note what mailbox
  15. Migrate to another mailbox
  16. in the current set-up - we have mailbox-0 and mailbox-1 pods
  17. ssh to the mailbox of the user created on 1.4 - kubectl exec -it mailbox-1 -- bash
  18. sudo su zimbra
  19. check if the user exist -> zmprov -l gaa
  20. yum install nano
  21. export TERM=xterm
  22. nano mailboxmove.sh
  23. paste the content of synacor/zimbra/zimbra-mailbox/movemailbox.sh
  24. ctrl + o, then ctrl + x (to save and exit)
  25. chmod +x mailboxmove.sh
  26. ./mailboxmove.sh
  27. follow the migration script
  28. Check if the emails still remains and it has changed mailbox
  29. browse to admin (all from step 11-14)
  30. check if the mailbox of the user changed
  31. login to client (steps 7 - 8)
  32. check if the emails are still present

## Conclusion:
  1. From the very start, we can define the number of mailboxes
  2. On scaling down, we can run movemailbox.sh

## Notes
  1. Commands zmmboxmove and zmpurgeoldmbox are only available on Zimbra Network Edition (with support)
  2. The script provided was from https://github.com/evil/movembox/blob/master/movembox.sh (just edited and debugged some part) and not officially from zimbra

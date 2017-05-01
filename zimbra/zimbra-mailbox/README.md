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
    1. kubectl exec -it mailbox-0 -- bash
    2. sudo su zimbra
    3. zmprov cd zimbra-k8s.cascadeo.info
    4. zmprov ca arvin@zimbra-k8s.cascadeo.info test1234 zimbraIsAdminAccount TRUE
    5. exit from pod (exit)
    6. kubectl describe service proxy-service-external (run from workstation)
    7. browse the LoadBalancer endpoint for user from step 1.6 using ssl (https/:443) (e.g. ae6a1ba792bcb11e798cc06d81d932b9-1863829251.us-west-1.elb.amazonaws.com)
    8. send/receive email from the web interface provided
2. know what mailbox pod is the user created
  1. back to workstation - kubectl describe service mb-service-2
  2. browse the LoadBalancer endpoint for admin - from ELB endpoint and port (7071) in 1.9
  3. login the created account on 1.4
  4. manage -> accounts then double click the account created on 1.4 and note what mailbox
3. Migrate to another mailbox
  1. in the current set-up - we have mailbox-0 and mailbox-1 pods
  2. ssh to the mailbox of the user created on 1.4 - kubectl exec -it mailbox-1 -- bash
  3. sudo su zimbra
  4. check if the user exist -> zmprov -l gaa
  5. yum install nano
  6. export TERM=xterm
  7. nano mailboxmove.sh
  8. paste the content of synacor/zimbra/zimbra-mailbox/movemailbox.sh
  9. ctrl + o, then ctrl + x (to save and exit)
  10. chmod +x mailboxmove.sh
  11. ./mailboxmove.sh
  12. follow the migration script
4. Check if the emails still remains and it has changed mailbox
  1. browse to admin (all from step 2)
  2. check if the mailbox of the user changed
  3. login to client (steps 1.6 - 1.8)
  4. check if the emails are still present

## Conclusion:
  1. From the very start, we can define the number of mailboxes
  2. On scaling down, we can run movemailbox.sh

## Notes
  1. Commands zmmboxmove and zmpurgeoldmbox are only available on Zimbra Network Edition (with support)
  2. The script provided was from https://github.com/evil/movembox/blob/master/movembox.sh (just edited and debugged some part) and not officially from zimbra

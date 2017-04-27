# zimbra-mailbox

1. Scaling-up Zimbra Mailbox
  1. “New” users can be assigned to newly spinned pod
  2. Dynamic assignment
2. Scaling-down Zimbra Mailbox
  1. Users in existing mailbox need to be assigned to “existing” mailboxes pod
  2. zmmboxmove -a <email@address> --from <servername> --to <servername>
  3. Purge old mailbox - zmpurgeoldmbox -a <email@address> -s <oldservername>
  4. To determine users on existing mailbox - all_accounts=`zmprov -l gaa`; for account in $all_accounts; do mbox_size=`zmmailbox -z -m $account gms`; echo "Mailbox size of $account = $mbox_size"; done ;
  5. On scaling down, users will be migrated from high to low stateful pod addressing scheme (e.g from mailbox-2 to mailbox-1)

Conclusion:
  1. From the very start, we can set number of mailboxes
  2. On scaling down, we can manually trigger the above commands

Limitations:
  1. AWS EBS can only be mounted on one node (ReadWriteOnce)

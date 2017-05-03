#!/bin/sh

# environment variables

HOSTNAME=$(hostname -s)
DOMAIN=$(hostname -d)
FQDN="${HOSTNAME}.${DOMAIN}"
SERVER_IP=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
REV_IP=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'|awk -F. '{print $3"."$2"."$1}')
REV_LAST=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/'|awk -F. '{print $4}')

# Display variables for debugging

echo hostname - $HOSTNAME
echo domain - $DOMAIN
echo fqdn - $FQDN
echo server IP - $SERVER_IP
echo arp - $REV_IP

echo "Enable/disable other services"
# Disable SMTP
service postfix stop
service sendmail stop
service sshd start
service crond start
service rsyslog start

echo "Host file"
cat /etc/hosts

# echo "Configure DNS for ${HOSTNAME}.${DOMAIN}"
# /setup_dns.sh


INST_FILE=zcs-8.7.7_GA_1787.RHEL6_64.20170410133400.tgz
echo "Checking zimbra installer for CentOS...${INST_FILE}"
if [ ! -f /${INST_FILE} ]; then
	echo "Downloading from source..."
	wget -O /${INST_FILE} http://files2.zimbra.com/downloads/8.7.7_GA/${INST_FILE}
fi

if [ -f /${INST_FILE} ]; then
	echo "Extracting installer...${INST_FILE}"
	tar -xzvf /${INST_FILE} -C /
else
	echo "Zimbra installer not found!"
	exit 1
fi


echo "Host file"
cat /etc/hosts

echo "Install ZIMBRA"
echo "========================"
cd /zcs-* && ./install.sh --platform-override < /install_override
echo "========================"

echo "Create zimbra config from configmap"
envsubst < /etc/config/zimbra.conf > /zimbra_config_generated

echo "Zimbra config dump"
cat /zimbra_config_generated

echo "Configure Zimbra"
/opt/zimbra/libexec/zmsetup.pl -c /zimbra_config_generated

echo "Fix rsyslog"
cat <<EOF >> /etc/rsyslog.conf
\$ModLoad imudp
\$UDPServerRun 514
EOF
service rsyslog restart

echo "Fix RED status"
/opt/zimbra/libexec/zmsyslogsetup

echo "Run zmupdatekeys as zimbra"
su -c /opt/zimbra/bin/zmupdateauthkeys zimbra

echo "Restart Zimbra"
service zimbra restart

echo "Restart CROND"
service crond restart

echo "Open PROXY Ports"
sudo su -c "/opt/zimbra/libexec/zmproxyconfig -e -w -o -H ${HOSTNAME}.mailbox-service.default.svc.cluster.local" -s /bin/sh zimbra

# echo "Register domain zimbra-k8s.cascadeo.info"
# /opt/zimbra/bin/zmprov cd zimbra-k8s.cascadeo.info
#
# echo "Register user admin@zimbra-k8s.cascadeo.info"
# /opt/zimbra/bin/zmprov ca admin@zimbra-k8s.cascadeo.info test1234 zimbraIsAdminAccount TRUE

echo "Server is ready..."
if [[ $1 == "-d" ]]; then
  while true; do sleep 1000; done
fi

if [[ $1 == "-bash" ]]; then
  /bin/bash
fi

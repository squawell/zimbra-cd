import os
import sys
import yaml
import glob
import boto3
import time

def build_registry():
    print "Building Registry..."

    os.system('aws ecr get-login | sh -')
    hashed_auth = os.system('cat ~/.docker/config.json | base64 -w 0')

    with open("myregistry.yaml", 'rw') as f:
        doc = yaml.load(f)
        doc['data']['.dockerconfigjson'] = hashed_auth
        yaml.dump(f)

    os.system('kubectl delete secret myregistrykey')
    secrets = os.system('kubectl create -f myregistry.yaml')
    print secrets
    print "Registry Build Done!"

def create_configmaps():
    print "Creating Configmaps..."

    for file in glob.glob("configmap/*.yaml"):
        cmd = 'kubectl create -f ' + str(file)
        os.system(cmd)

    configmaps = os.system("kubectl get configmaps")
    print configmaps
    print "Configmaps Created"

def create_ldap():
    print "Creating LDAP service..."

    os.system('kubectl create -f zimbra-ldap/yaml/internal-ldap-service.yaml')
    print "Internal LDAP service created..."
    os.system('kubectl create -f zimbra-ldap/yaml/statefulset.yaml')

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs ldap-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system('kubectl create -f zimbra-ldap/yaml/external-ldap-service.yaml')
    print "External LDAP service created..."

def create_mailbox():
    print "Creating MAILBOX service..."

    os.system('kubectl create -f zimbra-mailbox/yaml/internal-mailbox-service.yaml')
    print "Internal MAILBOX service created..."
    os.system('kubectl create -f zimbra-mailbox/yaml/statefulset.yaml')

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs mailbox-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system('kubectl create -f zimbra-mailbox/yaml/external-mailbox-service.yaml')
    print "External mailbox service created..."
    os.system('kubectl create -f zimbra-mailbox/yaml/client-service.yaml')
    os.system('kubectl create -f zimbra-mailbox/yaml/loadbalancer.yaml')
    print "loadbalancer service created..."

def create_mta():
    print "Creating MTA service..."

    os.system('kubectl create -f zimbra-mta/yaml/internal-mta-service.yaml')
    print "Internal MTA service created..."
    os.system('kubectl create -f zimbra-mta/yaml/statefulset.yaml')

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs mta-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system('kubectl create -f zimbra-mta/yaml/external-mta-service.yaml')
    print "External MTA service created..."

def create_proxy():
    print "Creating PROXY service..."

    os.system('kubectl create -f zimbra-proxy/yaml/internal-proxy-service.yaml')
    print "Internal PROXY service created..."
    os.system('kubectl create -f zimbra-proxy/yaml/statefulset.yaml')

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs proxy-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system('kubectl create -f zimbra-proxy/yaml/external-proxy-service.yaml')
    print "External PROXY service created..."

def create_dns_settings(cluster):
    client = boto3.client('route53')

    response = client.list_hosted_zones()
    print response
	# try:
	# 	response = client.change_resource_record_sets(
	# 	HostedZoneId='<hosted zone id>',
	# 	ChangeBatch= {
	# 					'Comment': 'add %s -> %s' % (source, target),
	# 					'Changes': [
	# 						{
	# 						 'Action': 'UPSERT',
	# 						 'ResourceRecordSet': {
	# 							 'Name': source,
	# 							 'Type': 'CNAME',
	# 							 'TTL': 300,
	# 							 'ResourceRecords': [{'Value': target}]
	# 						}
	# 					}]
	# 	})
	# except Exception as e:
	# 	print e

def main(cluster):
    # build_registry()
    # create_configmaps()
    # create_ldap()
    # create_mailbox()
    # create_mta()
    # create_proxy()
    create_dns_settings(cluster)


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [availabilityzone]
    """
    if len(sys.argv) < 2:
        raise SystemExit
    cluster = sys.argv[1]
    main(cluster)

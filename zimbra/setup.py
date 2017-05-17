import os
import sys
import yaml
import glob
import boto3
import time

path = os.path.dirname(__file__)

def build_registry():
    print "Building Registry..."

    os.system('aws ecr get-login | sh -')
    hashed_auth = os.system('cat ~/.docker/config.json | base64 -w 0')

    reg_path = "%s/myregistry.yaml" % path

    with open(reg_path, 'rw') as f:
        doc = yaml.load(f)
        doc['data']['.dockerconfigjson'] = hashed_auth
        yaml.dump(f)

    os.system('kubectl delete secret myregistrykey')
    secrets = os.system("kubectl create -f %s" % reg_path)
    print secrets
    print "Registry Build Done!"

def create_configmaps():
    print "Creating Configmaps..."

    for file in glob.glob("%s/configmap/*.yaml" % path):
        cmd = 'kubectl create -f ' + str(file)
        os.system(cmd)

    configmaps = os.system("kubectl get configmaps")
    print configmaps
    print "Configmaps Created"

def create_ldap():
    print "Creating LDAP service..."

    ldap_path = "%s/zimbra-ldap/yaml" % path

    os.system("kubectl create -f %s/internal-ldap-service.yaml" % ldap_path)
    print "Internal LDAP service created..."
    os.system("kubectl create -f %s/statefulset.yaml" % ldap_path)

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs ldap-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -f %s/external-ldap-service.yaml" % ldap_path)
    print "External LDAP service created..."

def create_mailbox():
    print "Creating MAILBOX service..."

    mailbox_path = "%s/zimbra-mailbox/yaml" % path

    os.system("kubectl create -f %s/internal-mailbox-service.yaml" % mailbox_path)
    print "Internal MAILBOX service created..."
    os.system("kubectl create -f %s/statefulset.yaml" % mailbox_path)

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs mailbox-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -f %s/external-mailbox-service.yaml" % mailbox_path)
    print "External mailbox service created..."
    os.system("kubectl create -f %s/client-service.yaml" % mailbox_path)
    os.system("kubectl create -f %s/loadbalancer.yaml" % mailbox_path)
    print "loadbalancer service created..."

def create_mta():
    print "Creating MTA service..."

    mta_path = "%s/zimbra-mta/yaml" % path

    os.system("kubectl create -f %s/internal-mta-service.yaml" % mta_path)
    print "Internal MTA service created..."
    os.system("kubectl create -f %s/statefulset.yaml" % mta_path)

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs mta-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -f %s/external-mta-service.yaml" % mta_path)
    print "External MTA service created..."

def create_proxy():
    print "Creating PROXY service..."

    proxy_path = "%s/zimbra-proxy/yaml" % path

    os.system("kubectl create -f %s/internal-proxy-service.yaml" % proxy_path)
    print "Internal PROXY service created..."
    os.system("kubectl create -f %s/statefulset.yaml" % proxy_path)

    is_ready = False
    while not is_ready:
        grep = os.system('kubectl logs proxy-0 | grep "Server is ready"')
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -f %s/external-proxy-service.yaml" % proxy_path)
    print "External PROXY service created..."

def create_dns_settings(cluster):
    client = boto3.client('route53')

    response = client.list_hosted_zones_by_name(DNSName='zimbra-k8s.cascadeo.info')
    if len(response['HostedZones']) > 0:
        dns = response['HostedZones'].pop()
        zone = dns['Id'].split('/')[2]
    	try:
    		response = client.change_resource_record_sets(
    		HostedZoneId=zone,
    		ChangeBatch= {
    						'Comment': 'add %s -> %s' % (source, target),
    						'Changes': [
    							{
    							 'Action': 'UPSERT',
    							 'ResourceRecordSet': {
    								 'Name': source,
    								 'Type': 'CNAME',
    								 'TTL': 300,
    								 'ResourceRecords': [{'Value': target}]
    							}
    						}]
    		})
    	except Exception as e:
    		print e

def main(cluster):
    build_registry()
    create_configmaps()
    create_ldap()
    create_mailbox()
    create_mta()
    create_proxy()
    # create_dns_settings(cluster)


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [availabilityzone]
    """
    if len(sys.argv) < 2:
        raise SystemExit
    cluster = sys.argv[1]
    main(cluster)

import os
import sys
import yaml
import glob
import boto3
import time

path = os.path.dirname(__file__)

def update_yaml_release(release):
    print "Updating yaml files for release %s..." % release

    yfiles = ['zimbra-ldap', 'zimbra-mailbox', 'zimbra-mta', 'zimbra-proxy']
      
    for yf in yfiles:
        for y in glob.glob("%s/%s/yaml/*.yaml" %(path, yf)):
            with open(y, 'r+') as f:
              doc = yaml.load(f)
              doc['metadata']['name'] += "-%s" % release

            outdir = "%s/%s/yaml/%s" %(path, yf, release)
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            outy = str(y).replace("yaml/", "yaml/%s/" % release)
            print "Creating " + outy
            with open(outy, 'w') as of:
              yaml.dump(doc, of)


def build_registry():
    print "Building Registry..."

    os.system('aws ecr get-login | sh -')
    hashed_auth = os.system('cat ~/.docker/config.json | base64 -w 0')

    reg_path = "%s/myregistry.yaml" % path

    with open(reg_path, 'r+') as f:
        doc = yaml.load(f)
        doc['data']['.dockerconfigjson'] = hashed_auth
        yaml.dump(doc, f)

    os.system('kubectl delete secret myregistrykey')
    secrets = os.system("kubectl create -f %s" % reg_path)
    print secrets
    print "Registry Build Done!"

def create_configmaps():
    print "Creating Configmaps..."

    for f in glob.glob("%s/configmap/*.yaml" % path):
        cmd = 'kubectl create -f ' + str(f)
        os.system(cmd)

    configmaps = os.system("kubectl get configmaps")
    print configmaps
    print "Configmaps Created"

def create_ldap(release):
    print "Creating LDAP service..."

    ldap_path = "%s/zimbra-ldap/yaml/%s" %(path, release)

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

def create_mailbox(release):
    print "Creating MAILBOX service..."

    mailbox_path = "%s/zimbra-mailbox/yaml/%s" %(path, release)

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

def create_mta(release):
    print "Creating MTA service..."

    mta_path = "%s/zimbra-mta/yaml/%s" %(path, release)

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

def create_proxy(release):
    print "Creating PROXY service..."

    proxy_path = "%s/zimbra-proxy/yaml/%s" %(path, release)

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

def main(cluster, release):
    update_yaml_release(release)
    build_registry()
    create_configmaps()
    create_ldap(release)
    create_mailbox(release)
    create_mta(release)
    create_proxy(release)
    # create_dns_settings(cluster)


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [availabilityzone] [releasename]
    """
    if len(sys.argv) < 3:
        print "Usage: python setup.py [availabilityzone] [releasename]"
        raise SystemExit

    cluster = sys.argv[1]
    release = sys.argv[2]
    main(cluster, release)

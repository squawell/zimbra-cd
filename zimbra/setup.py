import os
import sys
import yaml
import glob
import boto3
import time

path = os.path.dirname(__file__)

def update_yaml_release(namespace, releasename):
    print "Updating yaml files for release %s..." %(namespace)
    yfiles = ['zimbra-ldap', 'zimbra-mailbox', 'zimbra-mta', 'zimbra-proxy']
      
    for yf in yfiles:
        for y in glob.glob("%s/%s/yaml/*.yaml" %(path, yf)):
            with open(y, 'r+') as f:
              print "Checking %s..." % y
              doc = yaml.load(f)

              if 'labels' not in doc['metadata']:
                doc['metadata']['labels'] = {}

              doc['metadata']['labels']['cluster'] = namespace
              doc['metadata']['labels']['release'] = releasename

            outdir = "%s/%s/yaml/%s" %(path, yf, namespace)
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            outy = str(y).replace("yaml/", "yaml/%s/" %(namespace))
            print "Creating " + outy
            with open(outy, 'w') as of:
              yaml.dump(doc, of)


def build_registry(namespace):
    print "Building Registry..."

    os.system('aws ecr get-login | sh -')
    hashed_auth = os.system('cat ~/.docker/config.json | base64 -w 0')

    reg_path = "%s/myregistry.yaml" % path

    with open(reg_path, 'r+') as f:
        doc = yaml.load(f)
        doc['data']['.dockerconfigjson'] = hashed_auth
        #yaml.dump(doc, f)

    os.system('kubectl delete secret myregistrykey')
    secrets = os.system("kubectl create -n %s -f %s" %(namespace, reg_path))
    print secrets
    print "Registry Build Done!"


def create_namespace(namespace):
    os.system("kubectl create ns %s 2> /dev/null" % namespace)
    print os.system("kubectl describe ns %s" % namespace)


def create_configmaps(namespace):
    print "Creating Configmaps..."

    for f in glob.glob("%s/configmap/*.yaml" % path):
        cmd = "kubectl create -n %s -f %s" %(namespace,  str(f))
        os.system(cmd)

    configmaps = os.system("kubectl get configmaps")
    print configmaps
    print "Configmaps Created"

def create_ldap(namespace):
    print "Creating LDAP service..."

    ldap_path = "%s/zimbra-ldap/yaml/%s" %(path, namespace)

    os.system("kubectl create -n %s -f %s/internal-ldap-service.yaml" %(namespace, ldap_path))
    print "Internal LDAP service created..."
    os.system("kubectl create -n %s  -f %s/statefulset.yaml" %(namespace, ldap_path))

    is_ready = False
    while not is_ready:
        grep = os.system("kubectl logs -n %s ldap-0 | grep 'Server is ready'" % namespace)
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -n %s -f %s/external-ldap-service.yaml" %(namespace, ldap_path))
    print "External LDAP service created..."

def create_mailbox(namespace):
    print "Creating MAILBOX service..."

    mailbox_path = "%s/zimbra-mailbox/yaml/%s" %(path, namespace)

    os.system("kubectl create -n %s -f %s/internal-mailbox-service.yaml" %(namespace, mailbox_path))
    print "Internal MAILBOX service created..."
    os.system("kubectl create -n %s -f %s/statefulset.yaml" %(namespace, mailbox_path))

    is_ready = False
    while not is_ready:
        grep = os.system("kubectl logs -n %s mailbox-0 | grep 'Server is ready'" % namespace)
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -n %s -f %s/external-mailbox-service.yaml" %(namespace, mailbox_path))
    print "External mailbox service created..."
    os.system("kubectl create -n %s -f %s/client-service.yaml" %(namespace, mailbox_path))
    os.system("kubectl create -n %s -f %s/loadbalancer.yaml" %(namespace, mailbox_path))
    print "loadbalancer service created..."

def create_mta(namespace):
    print "Creating MTA service..."

    mta_path = "%s/zimbra-mta/yaml/%s" %(path, namespace)

    os.system("kubectl create -n %s -f %s/internal-mta-service.yaml" %(namespace, mta_path))
    print "Internal MTA service created..."
    os.system("kubectl create -n %s -f %s/statefulset.yaml" %(namespace, mta_path))

    is_ready = False
    while not is_ready:
        grep = os.system("kubectl logs -n %s mta-0 | grep 'Server is ready'" % namespace)
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -n %s -f %s/external-mta-service.yaml" %(namespace, mta_path))
    print "External MTA service created..."

def create_proxy(namespace):
    print "Creating PROXY service..."

    proxy_path = "%s/zimbra-proxy/yaml/%s" %(path, namespace)

    os.system("kubectl create -n %s -f %s/internal-proxy-service.yaml" %(namespace, proxy_path))
    print "Internal PROXY service created..."
    os.system("kubectl create -n %s -f %s/statefulset.yaml" %(namespace, proxy_path))

    is_ready = False
    while not is_ready:
        grep = os.system("kubectl logs -n %s proxy-0 | grep 'Server is ready'" % namespace)
        if grep == 0:
            is_ready = True
        else:
            time.sleep(10)

    print "Statefulset service created..."
    os.system("kubectl create -n %s -f %s/external-proxy-service.yaml" %(namespace, proxy_path))
    print "External PROXY service created..."

def create_dns_settings():
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

def main(namespace, releasename):
    update_yaml_release(namespace, releasename)
    create_namespace(namespace)

    build_registry(namespace)
    create_configmaps(namespace)
    create_ldap(namespace)
    create_mailbox(namespace)
    create_mta(namespace)
    create_proxy(namespace)
    # create_dns_settings()


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [clustername] [releasename]
    """
    if len(sys.argv) < 3:
        print "Usage: python setup.py [clustername] [releasename]"
        raise SystemExit

    clustername = sys.argv[1]
    releasename = sys.argv[2]

    main(clustername, releasename)

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

def create_volume(az):
    print "Creating Volume..."

    client = boto3.client('ec2')
    response = client.create_volume(
        AvailabilityZone=az,
        Size=80,
        VolumeType='gp2',
    )

    volume_id = response['VolumeId']
    print volume_id
    print "Volume Created!"

    print "Creating PV and PVC"

    with open("persistentvolumes/pv.yaml", 'rw') as f:
        doc = yaml.load(f)
        doc['spec']['awsElasticBlockStore']['volumeID'] = volume_id
        yaml.dump(f)

    for file in glob.glob("persistentvolumes/*.yaml"):
        cmd = 'kubectl create -f ' + str(file)
        os.system(cmd)

    pv = os.system("kubectl get pv")
    print pv
    print "PV and PVC Created!"

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

def main(az):
    build_registry()
    create_configmaps()
    create_volume(az)
    create_ldap()
    create_mailbox()
    create_mta()
    create_proxy()


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [availabilityzone]
    """
    if len(sys.argv) < 2:
        raise SystemExit
    az = sys.argv[1]
    main(az)

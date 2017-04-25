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

def main(az):
    #build_registry()
    #create_configmaps()
    #create_volume(az)
    create_ldap()


if __name__ == "__main__":
    """
    Setup.py arguments
    python setup.py [availabilityzone]
    """
    if len(sys.argv) < 2:
        raise SystemExit
    az = sys.argv[1]
    main(az)

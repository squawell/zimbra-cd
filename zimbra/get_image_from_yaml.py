#!/usr/bin/env python
import sys
import yaml
import glob
import os

def update_yaml_release(component):
    path = os.path.dirname(os.path.abspath(__file__))
    for y in glob.glob("%s/zimbra-%s/yaml/statefulset.yaml" %(path, component)):
            with open(y, 'r+') as f:
              doc = yaml.load(f)
              print doc['spec']['template']['spec']['containers'][0]['image']

if __name__ == "__main__":
    """
    get_image_from_yaml.py arguments
    python get_image_from_yaml.py [mta|mailbox|proxy|ldap]
    """
    if len(sys.argv) < 2:
        print "Usage: python setup.py [mta|mailbox|proxy|ldap]"
        raise SystemExit

    component = sys.argv[1]
    update_yaml_release(component)

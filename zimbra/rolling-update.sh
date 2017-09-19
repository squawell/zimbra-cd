#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: rolling-update.sh [namespace]"
    exit
fi

SCRIPT_PATH=$(dirname $0)
NAMESPACE=$1
kubectl describe ns $NAMESPACE
if [ $? -eq 1 ]; then
    exit 
fi

for i in mta mailbox proxy ldap
do 
    IMAGE=$(python ${SCRIPT_PATH}/get_image_from_yaml.py $i)
    if [[ $IMAGE == *"amazonaws"* ]]; then
        echo "Deploying $IMAGE to $i statefulset.."
        kubectl patch statefulset $i -n ${NAMESPACE} -p '{"spec":{"updateStrategy":{"type":"RollingUpdate"}}}'
        kubectl patch statefulset $i -n ${NAMESPACE} --type='json' -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value":"'${IMAGE}'"}]'
        kubectl rollout status sts/$i -n ${NAMESPACE}
    fi
done

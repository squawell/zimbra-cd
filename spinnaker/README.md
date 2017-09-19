# Spinnaker Chart

Based on the official Spinnaker helm chart - https://github.com/kubernetes/charts/tree/master/stable/spinnaker

## Chart Details
This chart is modified to use S3 instead of Minio, the local storage that comes with the default chart.

## Installing the Chart

Prerequisites:

- Working K8s cluster
- AWS access credentials

1. Create S3 bucket for Spinnaker via AWS API or console. Create a directory named front50.

```bash
export S3_BUCKET=spinnaker.kubernetes.zimbra.org

aws s3api create-bucket --bucket ${S3_BUCKET}  --create-bucket-configuration LocationConstraint=us-west-2
aws s3api put-object --bucket ${S3_BUCKET} --key front50/
aws s3 ls s3://${S3_BUCKET}
```

2. Install helm

```bash
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.2.1-linux-amd64.tar.gz
tar -zxvf helm-v2.2.1-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm

helm init
# wait until helm version outputs both client and server
helm version
Client: &version.Version{SemVer:"v2.2.1", GitCommit:"db531fd75fb2a1fb0841a98d9e55c58c21f70f4c", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.2.1", GitCommit:"db531fd75fb2a1fb0841a98d9e55c58c21f70f4c", GitTreeState:"clean"}
```

3. Clone this repo and install the modified Spinnaker chart

```bash
export SPIN_NAME=zimbra
export S3_BUCKET=spinnaker.kubernetes.zimbra.org

cd synacor/

# edit values.yaml and update s3.AccessKey, s3.SecretKey and storageBucket to match step #1
vi spinnaker/values.yaml

# get GitHub key from Leo and save into a file
kubectl create secret generic git-repo --from-file=ssh-privatekey=/path/to/key

# sync front50
aws s3 sync spinnaker/data/front50/ s3://${S3_BUCKET}/front50/

# workaround for missing kubectl in nodes
# make sure to have SSH access to nodes
kops delete secret sshpublickey admin
kops create secret sshpublickey admin -i /path/to/your/public/key
kops update cluster  --yes
kops rolling-update cluster --yes
kops validate cluster
# copy kubectl from workstation to nodes via SCP

helm install --name ${SPIN_NAME} spinnaker/
helm status ${SPIN_NAME}

kubectl get po
# wait untill all pods are ready and in RUNNING status
NAME                                                  READY     STATUS    RESTARTS   AGE
zimbra-redis-1133920672-slp1v                 1/1       Running   0          3d
zimbra-spinnaker-clouddriver-13592141-ldz3m   1/1       Running   0          3d
zimbra-spinnaker-deck-4018278025-x77ch        1/1       Running   0          3d
zimbra-spinnaker-echo-4149434125-kjkxm        1/1       Running   0          3d
zimbra-spinnaker-front50-1285571732-ztq72     1/1       Running   0          3d
zimbra-spinnaker-gate-3292944141-jd361        1/1       Running   7          3d
zimbra-spinnaker-igor-383944194-rl672         2/2       Running   0          3d
zimbra-spinnaker-orca-1623283476-qcg1x        1/1       Running   5          3d
zimbra-spinnaker-rosco-916311256-vr1bg        1/1       Running   0          3d
```

4. Port forward 9000 and 8084 to access the Spinnaker GUI. Also port forward 8080 to access Jenkins.

```bash
## from the workstation - port forward deck and gate

export GATE_POD=$(kubectl get pods --namespace default -l "component=gate,app=${SPIN_NAME}-spinnaker" -o jsonpath="{.items[0].metadata.name}")
export DECK_POD=$(kubectl get pods --namespace default -l "component=deck,app=${SPIN_NAME}-spinnaker" -o jsonpath="{.items[0].metadata.name}")

kubectl port-forward --namespace default $GATE_POD 8084 &
kubectl port-forward --namespace default $DECK_POD 9000 &

export IGOR_POD=$(kubectl get pods --namespace default -l "component=igor,app=${SPIN_NAME}-spinnaker" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward --namespace default $IGOR_POD 8080 &
```

```bash
# if you are accessing K8s on a separate workstation, forward the ports on a new SSH tunnel
ssh -i .ssh/zimbra-20170529.pem -L 9000:127.0.0.1:9000 -L 8084:127.0.0.1:8084 -L 8080:127.0.0.1:8080 ubuntu@35.161.227.109

```

5. Access Jenkins in http://127.0.0.1:8080/. Ensure that runs-script-local Jenkins job is present. If not run the following:

```bash
# from the workstation - execute
kubectl exec -it $IGOR_POD -c jenkins-master -- /bin/bash

# inside the Jenkins container - execute
curl -X POST -H "Content-Type: application/xml" --retry "20" --retry-delay "10" --max-time "3" --data-binary "@/jobs/run-script-local.xml" "http://127.0.0.1:8080/createItem?name=run-script-local"

# refresh http://127.0.0.1:8080/ to see the job
```

5. Access the Spinnaker GUI in http://localhost:9000/. The pipelines are located unnder http://127.0.0.1:9000/#/applications/zimbra/executions


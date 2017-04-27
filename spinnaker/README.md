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
S3_BUCKET=synacor-leo.spinnaker

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
export SPIN_NAME=synacor-leo

cd synacor/

# edit values.yaml and update s3.AccessKey, s3.SecretKey and storageBucket to match step #1
vi spinnaker/values.yaml

helm install --name ${SPIN_NAME} spinnaker/
helm status ${SPIN_NAME}

kubectl get po
# wait untill all pods are ready and in RUNNING status
NAME                                                  READY     STATUS    RESTARTS   AGE
synacor-leo4-redis-3548858892-l09ns                   1/1       Running   0          2m
synacor-leo4-spinnaker-clouddriver-3526782649-lx7tt   1/1       Running   0          2m
synacor-leo4-spinnaker-deck-2312115957-5rb1t          1/1       Running   0          2m
synacor-leo4-spinnaker-echo-2240175993-4hpjj          1/1       Running   0          2m
synacor-leo4-spinnaker-front50-1775784785-mr5zw       1/1       Running   0          2m
synacor-leo4-spinnaker-gate-1386831737-vs528          1/1       Running   2          2m
synacor-leo4-spinnaker-igor-2958287750-tsqh3          2/2       Running   0          2m
synacor-leo4-spinnaker-orca-4017840000-qb85b          1/1       Running   0          2m
synacor-leo4-spinnaker-rosco-2666648900-8rj8b         1/1       Running   0          2m
```

4. Port forward 9000 and 8084 to access the GUI

```bash
## port forward deck and gate

export GATE_POD=$(kubectl get pods --namespace default -l "component=gate,app=${SPIN_NAME}-spinnaker" -o jsonpath="{.items[0].metadata.name}")
export DECK_POD=$(kubectl get pods --namespace default -l "component=deck,app=${SPIN_NAME}-spinnaker" -o jsonpath="{.items[0].metadata.name}")

kubectl port-forward --namespace default $GATE_POD 8084 &
kubectl port-forward --namespace default $DECK_POD 9000 &
```

5. Access the GUI in http://localhost:9000/ 

```bash
# if you are accessing K8s on a separate workstation, forward the ports on a new SSH tunnel
ssh -i .ssh/cascadeo20160514-stg.pem -L 9000:127.0.0.1:9000 -L 8084:127.0.0.1:8084 ubuntu@34.209.216.170
```

Synacor Kubernetes + Zimbra Deployment


Requires:

- IAM access and secret keys with EC2, S3 and Route53 admin privileges


I. Setup workstation. Launch t2.micro instance from Ubuntu 14.04 (Trusty) AMI.


ssh -i .ssh/zimbra-20170529.pem ubuntu@35.161.227.109

## run as root
## update hostname
sudo su
hostname zimbra-workstation
echo zimbra-workstation > /etc/hostname
vi /etc/hosts

127.0.0.1 localhost
127.0.1.1 zimbra-workstation

## update and install packages
apt-get update && apt-get upgrade
apt-get install python-pip

## setup aws cli
pip install awscli

export ACCESS_KEY=AKIAJJLxxxxxxxxxxxxxx
export SECRET_KEY=oMCfz4MsWc7qqc7exxxxxxxxxxxxxx

aws configure
$ACCESS_KEY
$SECRET_KEY
us-west-2

## install docker cli
wget -qO- https://get.docker.com/ | sh

## get kubectl
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl

chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

## get kops
wget https://github.com/kubernetes/kops/releases/download/1.5.1/kops-linux-amd64
chmod +x kops-linux-amd64

mv kops-linux-amd64 /usr/local/bin/kops

2. Create AWS resources to be used by zimbra app

## create r53 sub domain from aws console
create hosted zone synacor-leo.cascadeo.info.
create record set under cascadeo.info and copy NS for synacor-leo.cascadeo.info.

dig NS synacor-leo.cascadeo.info

## create s3 bucket via aws cli
aws s3api create-bucket --bucket synacor-leo.cascadeo.info --create-bucket-configuration LocationConstraint=us-west-2
aws s3api put-bucket-versioning --bucket synacor-leo.cascadeo.info  --versioning-configuration Status=Enabled


II. Setup Kubernetes cluster


## run from the workstation
## build cluster
export NAME=synacor-leo.cascadeo.info
export KOPS_STATE_STORE=s3://synacor-leo.cascadeo.info

aws ec2 describe-availability-zones --region us-west-2

ssh-keygen
kops create cluster --zones=us-west-2a ${NAME}
kops update cluster ${NAME} --yes

## verify cluster
kops validate cluster
kubectl -n kube-system get po
kubectl get no

## scale
kops edit ig nodes
# t2.large; max=4

kops update cluster --yes
kops rolling-update cluster --yes

## get helm client
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.2.1-linux-amd64.tar.gz
tar -zxvf helm-v2.2.1-linux-amd64.tar.gz
mv linux-amd64/helm /usr/local/bin/helm

## install tiller
helm init
helm version
kubectl get po -n kube-system

III. Setup Spinnaker

https://github.com/cascadeo/synacor/blob/master/spinnaker/README.md

IV. Deploy Zimbra app

From spinnaker, go to zimbra application then pipeline. Start execution of various pipeline entries.


Miscellaneous

* https://github.com/prem-cascadeo/zibootstrapper - bootstrapper / workstation

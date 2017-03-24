At least for our POC the flow goes like this:

* the zibootstrapper (aka the dev workstation container) will:
	* launch the initial k8s cluster/s that will host spinnaker and zi-pods
	* `docker run`-ning this container will give you the kubectl and kops context to manage the previously launched k8s cluster

* spinnaker spins the CD pipeline. The CD pipeline stages are:

	* trigger: git Pull Request merge (Dockerfile and its dependencies update or k8s YAML files)
	* (optional if no auto-build) trigger 'container image building' in Docker Hub (source: Dockerfiles in a github repo)
	* generate configuration for zi-pods
		* generate configuration (Example: https://git.io/vSUjp)
		* upload to k8's built-in etcd (HA k/v store) [Example: https://git.io/vSTvD]
		* write confd (https://github.com/kelseyhightower/confd) TOMLs
		* confd does it magic when container is up (Dockerfile example: https://git.io/vSTU4). Notice: `ENTRYPOINT ["/entrypoint.sh"]` (Bootstrap script: https://git.io/vSTU1)
	* Deploy the new zi-pods cluster/s (`kubectl create`)
	* Red/Black promotion


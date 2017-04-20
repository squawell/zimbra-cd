At least for our POC the flow goes like this:

* the zibootstrapper (aka the dev workstation container) will:
	* launch the initial k8s cluster/s that will host spinnaker and zi-pods
	* `docker run`-ning this container will give you the kubectl and kops context to manage the previously launched k8s cluster

* spinnaker spins the CD pipeline. The CD pipeline stages are:

	* trigger: git Pull Request merge (Dockerfile and its dependencies update or k8s YAML files)
	* (optional if no auto-build) trigger 'container image building' in Docker Hub (source: Dockerfiles in a github repo)
	* generate configuration for zi-pods
		* jinja2 or sigil generate configuration (Example: https://git.io/vSUjp)
		* upload as k8s ConfigMaps via volume plugin [key=file,value=actual config generated from the previous step]
	* Deploy the new zi-pods cluster/s (`kubectl create`)
	* Red/Black promotion

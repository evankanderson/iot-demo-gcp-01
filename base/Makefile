SHELL=/bin/bash

BASE_VERSION = `cat VERSION`
BASE_TMP_VERSION = `cat VERSION.tmp`
DOCKER_REGISTRY=`krules-py profile get-value docker_registry`
NAMESPACE=`krules-py profile get-value namespace`
DEPLOYED_VERSION=`krules-py rulesset check-version iot-demo-gcp-01-base --less-than ${BASE_VERSION}`

.PHONY: clean

all: .lastResources

VERSION: Dockerfile app/*.py
	cp VERSION VERSION.tmp && \
	bumpversion --current-version ${BASE_VERSION}  patch VERSION.tmp --allow-dirty && \
	docker build -t  ${DOCKER_REGISTRY}/iot-demo-gcp-01-base:${BASE_TMP_VERSION}  -t ${DOCKER_REGISTRY}/iot-demo-gcp-01-base:latest . && \
	cp VERSION.tmp VERSION && rm VERSION.tmp

push: VERSION
	docker push ${DOCKER_REGISTRY}/iot-demo-gcp-01-base:${BASE_VERSION}

.lastResources: VERSION k8s/*
	krules-py rulesset check-version iot-demo-gcp-01-base --less-than `cat VERSION` > .UPDATE_NEEDED
	if [[ `cat .UPDATE_NEEDED` = 1 ]]; then \
		make push; \
	fi && \
	kustomize build k8s  | kubectl apply -n ${NAMESPACE}  -f - \
	&& echo `date` > ".lastResources" && \
	rm .UPDATE_NEEDED

clean:
	rm -f VERSION.tmp .lastResources .UPDATE_NEEDED
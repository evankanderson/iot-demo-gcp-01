SHELL=/bin/bash

RULESSET_VERSION = `cat VERSION`
RULESSET_TMP_VERSION = `cat VERSION.tmp`
DOCKER_REGISTRY=`krules-py profile get-value docker_registry`
NAMESPACE=`krules-py profile get-value namespace`
DEPLOYED_VERSION=`krules-py rulesset check-version iot-demo-gcp-01-pubsub-source-subscription --less-than ${RULESSET_VERSION}`

.PHONY: clean

all: .lastResources

Dockerfile: Dockerfile.origin
	krules-py rulesset build-dockerfile;


VERSION: Dockerfile app/*.py
	cp VERSION VERSION.tmp && \
	bumpversion --current-version ${RULESSET_VERSION} patch VERSION.tmp --allow-dirty && \
	docker build -t ${DOCKER_REGISTRY}/iot-demo-gcp-01-pubsub-source-subscription:${RULESSET_TMP_VERSION} -t ${DOCKER_REGISTRY}/iot-demo-gcp-01-pubsub-source-subscription:latest . &&\
	cp VERSION.tmp VERSION && rm VERSION.tmp

push: VERSION
	docker push ${DOCKER_REGISTRY}/iot-demo-gcp-01-pubsub-source-subscription:${RULESSET_VERSION}

.lastResources: VERSION k8s/*
	krules-py rulesset check-version iot-demo-gcp-01-pubsub-source-subscription --less-than `cat VERSION` > .UPDATE_NEEDED
	if [[ `cat .UPDATE_NEEDED` = 1 ]]; then \
		make push; \
	fi && \
	krules-py rulesset patch --set-image rulesset=${DOCKER_REGISTRY}/iot-demo-gcp-01-pubsub-source-subscription:${RULESSET_VERSION} | kubectl apply -n ${NAMESPACE}  -f - && \
	echo `date` > ".lastResources" && \
	rm .UPDATE_NEEDED

clean:
	rm -f Dockerfile VERSION.tmp .lastResources .UPDATE_NEEDED
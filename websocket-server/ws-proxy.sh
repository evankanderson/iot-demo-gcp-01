#!/usr/bin/env sh

kubectl port-forward --namespace iot-demo-gcp-01 svc/ws-server 5678:80

#!/bin/bash
set -exu

# Setup test environment variables
export ZENKO_NAME=${1:-"end2end"}
# Getting kafka host from backbeat's config
KAFKA_HOST_PORT=$(kubectl get secret -l app.kubernetes.io/name=backbeat-config,app.kubernetes.io/instance=end2end \
    -o jsonpath='{.items[0].data.config\.json}' | base64 -di | jq .kafka.hosts)
KAFKA_HOST_PORT=${KAFKA_HOST_PORT:1:-1}
# Removing the port
export NOTIF_KAFKA_HOST=${KAFKA_HOST_PORT%:*}
export NOTIF_KAFKA_PORT=${KAFKA_HOST_PORT#*:}

UUID=$(kubectl get secret -l app.kubernetes.io/name=backbeat-config,app.kubernetes.io/instance=end2end \
    -o jsonpath='{.items[0].data.config\.json}' | base64 -di | jq .extensions.replication.topic)
UUID=${UUID%.*}
UUID=${UUID:1}
OPLOG_TOPIC="${UUID}.backbeat-oplog"
NOTIFICATION_TOPIC="${UUID}.backbeat-notification"

echo "127.0.0.1 iam.zenko.local ui.zenko.local s3-local-file.zenko.local keycloak.zenko.local \
    sts.zenko.local management.zenko.local s3.zenko.local" | sudo tee -a /etc/hosts

# Add bucket notification target
envsubst < ./configs/notification_destinations.yaml | kubectl apply -f -
# Wait for service stabilization
kubectl wait --for condition=DeploymentInProgress=true --timeout 10m zenko/${ZENKO_NAME}
kubectl wait --for condition=DeploymentFailure=false --timeout 10m zenko/${ZENKO_NAME}
kubectl wait --for condition=DeploymentInProgress=false --timeout 10m zenko/${ZENKO_NAME}

# Get kafka image name and tag
KAFKA_REGISTRY_NAME=$(yq eval ".kafka.sourceRegistry" ../../../solution/deps.yaml)
KAFKA_IMAGE_NAME=$(yq eval ".kafka.image" ../../../solution/deps.yaml)
KAFKA_IMAGE_TAG=$(yq eval ".kafka.tag" ../../../solution/deps.yaml)
KAFKA_IMAGE=$KAFKA_REGISTRY_NAME/$KAFKA_IMAGE_NAME:$KAFKA_IMAGE_TAG

# Creating bucket notification topic in kafka
kubectl run kafka-topics \
    --image=$KAFKA_IMAGE \
    --pod-running-timeout=5m \
    --rm \
    --restart=Never \
    --attach=True \
    --command -- bash -c \
    "kafka-topics.sh --create --topic $NOTIF_DEST_TOPIC --bootstrap-server $KAFKA_HOST_PORT ; \
        kafka-topics.sh --create --topic $NOTIF_ALT_DEST_TOPIC --bootstrap-server $KAFKA_HOST_PORT ; \
        kafka-topics.sh --create --topic $OPLOG_TOPIC --bootstrap-server $KAFKA_HOST_PORT ; \
        kafka-topics.sh --create --topic $NOTIFICATION_TOPIC --bootstrap-server $KAFKA_HOST_PORT"
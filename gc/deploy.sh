#!/bin/sh
# FILESTORE_IP=`gcloud filestore instances describe audioid \
#     --zone us-central1-c --format="value(networks.ipAddresses[0])"`
# sed "s/FILESTORE_IP/${FILESTORE_IP}/g" storage/pvc-gc.yaml | kubectl apply -f -

sed "s#\$TARGET#\'/home/tsukimayaayu/tmpStorage\'#g" components/storage/pvc.yaml | kubectl apply -f -

kubectl apply -f components/rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f components/rabbitmq/rabbitmq-service.yaml

kubectl apply -f components/cassandra/cassandra-deployment.yaml
kubectl apply -f components/cassandra/cassandra-service.yaml
# kubectl apply -f https://k8s.io/examples/application/cassandra/cassandra-service.yaml
# kubectl apply -f https://k8s.io/examples/application/cassandra/cassandra-statefulset.yaml

kubectl apply -f components/rest/rest-deployment.yaml
kubectl apply -f components/rest/rest-service.yaml
# kubectl expose deployment rest-server --name=rest-service \
#         --type=LoadBalancer --port 80 --target-port 5000

kubectl apply -f components/logs/logs-deployment.yaml

# sleep 60

kubectl apply -f components/worker/worker-deployment.yaml



# deploy on gc
# image mush be pulled
# address is dynamics, need to check using kubectl get service





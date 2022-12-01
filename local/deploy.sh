kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.4/deploy/static/provider/cloud/deploy.yaml

kubectl apply -f components/ingress/ingress.yaml

# kubectl apply -f storage/pvc.yaml
sed "s#\$TARGET#\'/Users/ayu/Study/Projects/Web/shazam/local/tmpStorage\'#g" components/storage/pvc.yaml | kubectl apply -f -

kubectl apply -f components/rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f components/rabbitmq/rabbitmq-service.yaml

kubectl apply -f components/rest/rest-deployment.yaml
kubectl apply -f components/rest/rest-service.yaml

kubectl apply -f components/cassandra/cassandra-deployment.yaml
kubectl apply -f components/cassandra/cassandra-service.yaml

kubectl apply -f components/logs/logs-deployment.yaml

kubectl apply -f components/worker/worker-deployment.yaml

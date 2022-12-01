# Google
kubectl create deployment nginx --image=nginx:1.10.0
kubectl get pods
kubectl expose deployment nginx --port 80 --type LoadBalancer
kubectl get services

kubectl create -f pods/monolith.yaml
kubectl describe pods monolith

kubectl port-forward monolith 10080:80

kubectl exec monolith --stdin --tty -c monolith /bin/sh

kubectl logs monolith


kubectl create secret generic tls-certs --from-file tls/
kubectl create configmap nginx-proxy-conf --from-file nginx/proxy.conf
kubectl create -f pods/secure-monolith.yaml
kubectl create -f services/monolith.yaml

# Grunwald
kubectl delete pods busybox2
kubectl exec busybox4 -- tail /tmp/example.log

kubectl delete --all deployments



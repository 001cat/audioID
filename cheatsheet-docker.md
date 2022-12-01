docker image

docker run hello-world

docker ps
docker ps -a

docker build -t node-app:0.1 .
docker build -f Dockerfile-nginx -t tutorial-nginx hello-world

docker pull rabbitmq

docker history tutorial-hello

docker run -p 4000:80 --name my-app node-app:0.1
docker stop my-app && docker rm my-app

docker run -p 4000:80 --name my-app -d node-app:0.1
docker ps
docker logs c4e5a3983cff[container_id]
docker stop my-app && docker rm my-app

docker run -it --rm --name hello -p 8888:80 -v $(pwd)/hello-world/subdir:/var/www/html/dir tutorial-hello
docker kill hello

docker exec -it [container_id] bash

docker inspect [container_id]
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [container_id]




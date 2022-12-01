VERSION=v1
DOCKERUSER=001cat

build:
	docker build -f Dockerfile-Worker -t audioid-worker .

push:
	docker tag audioid-worker $(DOCKERUSER)/audioid-worker:$(VERSION)
	docker push $(DOCKERUSER)/audioid-worker:$(VERSION)
	docker tag audioid-worker $(DOCKERUSER)/audioid-worker:latest
	docker push $(DOCKERUSER)/audioid-worker:latest

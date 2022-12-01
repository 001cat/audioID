VERSION=v1
DOCKERUSER=001cat

build:
	docker build -f Dockerfile-rest -t audioid-rest .

push:
	docker tag audioid-rest $(DOCKERUSER)/audioid-rest:$(VERSION)
	docker push $(DOCKERUSER)/audioid-rest:$(VERSION)
	docker tag audioid-rest $(DOCKERUSER)/audioid-rest:latest
	docker push $(DOCKERUSER)/audioid-rest:latest

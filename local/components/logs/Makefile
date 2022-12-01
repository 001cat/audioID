VERSION=v1
DOCKERUSER=001cat

build:
	docker build -f Dockerfile -t audioid-logs  .
# tag:
# 	docker tag sentiment-logs  $(DOCKERUSER)/sentiment-logs:$(VERSION)
# 	docker tag sentiment-logs  $(DOCKERUSER)/sentiment-logs:latest
push:
	docker tag audioid-logs $(DOCKERUSER)/audioid-logs:$(VERSION)
	docker push $(DOCKERUSER)/audioid-logs:$(VERSION)
	docker tag audioid-logs $(DOCKERUSER)/audioid-logs:latest
	docker push $(DOCKERUSER)/audioid-logs:latest
gcloud config set compute/zone us-central1-c
# gcloud container clusters create audioid --machine-type=e2-standard-4 --num-nodes=2
gcloud container clusters create audioid-n1 --machine-type=n1-standard-2 --num-nodes=1

gcloud container clusters get-credentials audioid-n1 --zone us-central1-c

# gcloud filestore instances create audioid \
#   --zone=us-central1-c \
#   --tier=standard \
#   --file-share=name="audiofs",capacity=5GB \
#   --network=name="default"

# gcloud compute disks create audioid-disk \
#   --size 10GB \
#   --type pd-standard

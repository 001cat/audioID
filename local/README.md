# Audio Identify Service -- Class Project of CSCI5253 Fall 2021 in CU

This is an service to identify you uploaded music recordings and give the matched item in database.

## sub directories


| directory | Description|
|---|---|
|cassandra| script and settings to deploy cassandra database|
| logs | script and settings to deploy logger pod|
| rest | flask REST server, client and test script|
| worker | audioID package and necessary files to deploy worker pod
| storage | yaml for deploying persistent volumn |
| mp3 | mp3 test files uploaded to build database |
|mp3-recording | mp3 test files used to test recognizing |



## Deploy
To deploy in google cloud platform, please run create_cluster.sh first to create a cluster ready for kubernetes and then run deploy-all-gc.sh to deploy every parts of this service. You could also run deploy-all.sh to deploy it locally. The delete-all-gc.sh and delete-all.sh could be used to delete this service if you need.

## Adding New Songs
Add your favorite songs in mp3 file, and then run 
```
uploadAll.py [service address]
```
under rest directory. Check result by visiting [service address]/songs in browser.

## Recognizing songs
Add your favorite songs in mp3 file, and then run 
```
recogAll.py [service address]
```
under rest directory. Check result by visiting [service address]/recogs in browser.

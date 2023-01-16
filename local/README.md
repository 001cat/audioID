# Audio Identify Service

This is an service to identify you uploaded music recordings and give the matched item in database.

## Architecture
| directory | Description|
|---|---|
|cassandra| Scripts to deploy cassandra database|
| logs | Scripts to deploy logger pod|
| rest | flask REST server, client and test script|
| worker | audioID package and necessary files to deploy worker pod
| storage | yaml for deploying persistent volumn |
| rabbitmq | Message queue server to manage communication between other components


## Deploy
You can run deploy-all.sh to deploy it locally, and run delete-all.sh to delete this service.

## Testing
Preparing some known music files and some "unknown" recordings. Run uploadAll to make the test. You can also check the result by visiting[service address]/songs and [service address]/recogs in browser


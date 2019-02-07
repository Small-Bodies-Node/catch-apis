#! /bin/bash

### Load vars defined in .env 
eval $(cat .env | sed 's/^/export /')       

### Build URI
URI='mysql+pymysql://'$DB_USERNAME':'$DB_PASSWORD'@'$DB_HOST'/'$DB_DATABASE
echo $URI

### Output generated models
sqlacodegen $URI > ./generated-models/gen-models.txt
#! /bin/bash

### This is a script to simply call some routes and print out result:

printf "\n"
printf "\n"
printf "============================"
printf "\n"
printf "\n"

### 1. GET ROOT
curl localhost:5001/

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 2. GET ZTF
curl localhost:5001/ztf

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 3. POST test-post
curl -X POST -H "Content-Type:application/json" -d "{\"username\": \"Magnus\",\"password\": \"TheDude\"}" 'localhost:5001/post-test'

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 4. GET moving-object-search
curl 'localhost:5001/moving-object-search?start=0&end=10'

printf "\n"
printf "\n"
printf "============================"
printf "\n"
printf "\n"
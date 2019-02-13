#! /bin/bash

eval $(cat .env | sed 's/^/export /')       ### Load vars defined in .env 

### This is a script to simply call some routes and print out result:

printf "\n"
printf "\n"
printf "============================"
printf "\n"
printf "\n"

### 1. GET ROOT
curl -k $TEST_URL_BASE

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 2. GET ZTF
curl -k $TEST_URL_BASE'/ztf'

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 3. POST test-post
curl -k $TEST_URL_BASE'/post-test' -X POST -H "Content-Type:application/json" -d "{\"username\": \"UMD\",\"password\": \"TheDude\"}"

printf "\n"
printf "\n"
printf '++++++++++++++++++'
printf "\n"
printf "\n"

### 4. GET moving-object-search
curl -k $TEST_URL_BASE'/moving-object-search?start=0&end=10&objid=909'

printf "\n"
printf "\n"
printf "============================"
printf "\n"
printf "\n"
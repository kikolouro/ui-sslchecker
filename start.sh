#!/bin/sh

VERSION=v2.0
if ! [ -f $(pwd)/"hosts.json" ]; then
    #Doesn't Exist
    cp hosts_template.json hosts.json
fi
if ! [ -f $(pwd)/"data.json" ]; then
    #Doesn't Exist
    cp data_template.json data.json
fi

if ! [ -f $(pwd)/"config.yaml" ]; then
    #Doesn't Exist
    echo "Error: Missing config file"  
    exit
fi

#docker build -t flouro.azurecr.io/sslchecker:$VERSION

docker-compose up
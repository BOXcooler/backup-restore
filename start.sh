#!/bin/bash

if [ -n $1 ]; then

    # Check docker-compose
    if [ -x "$(command -v docker-compose)" ]; then
        echo "docker-compose installed"
        
        # Remove old result.txt
        if [ -f ./result/result.txt ]; then
            rm -f ./result/result.txt
        fi

        # Add acccess token value
        sed -i'' "s/ACCESS_TOKEN=.*/ACCESS_TOKEN=$1/g" .env

        echo "Starting docker compose"    
        docker-compose -f ./docker-compose.yml up -d --build
        
        # Waiting result and add to file
        COUNTER=0
        echo "Waiting results"
        while [  $COUNTER -lt 10 ]; do
            if [ -f ./result/result.txt ];then
                COUNTER=10
            else
               echo "$COUNTER -- waiting 2 seconds"
               sleep 2
               let COUNTER=COUNTER+1
            fi
        done

        if [ -f ./result/result.txt ]; then
        echo -e "Result is -->"
            cat ./result/result.txt | xargs -0 echo
            echo "Shutting down docker containers"
            docker-compose down
            sed'' -i "s/ACCESS_TOKEN=.*/ACCESS_TOKEN=/g" .env
        else
            echo "Something went wrong (("
            echo "Shutting down docker containers"
            docker-compose down
            sed'' -i "s/ACCESS_TOKEN=.*/ACCESS_TOKEN=/g" .env
            exit 1
        fi
    else    
        echo "Docker compose not installed"
        exit 1
    fi
else
    echo "Provide token as a first positional argument"
    exit 1
fi

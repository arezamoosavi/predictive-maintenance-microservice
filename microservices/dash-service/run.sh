#!/bin/bash

until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

until nc -z ${REDIS_HOST} ${REDIS_PORT}; do
    echo "$(date) - waiting for redis..."
    sleep 1
done

n=15

while [ $n -gt 0 ]
do
	echo "Wait for kafka  $n more times."
	n=$(( n-1 ))
    sleep 10
done

while python check_kafka.py; do echo 'connecting to kafka...'; sleep 10; done;

nameko run --config config.yml services

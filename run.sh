#!/bin/bash
while true; do
	python3 trading.py 
   	if [ $? -ne 0 ]; then
       		echo "Error occurred, but continuing..."
	fi
    	sleep 2
done
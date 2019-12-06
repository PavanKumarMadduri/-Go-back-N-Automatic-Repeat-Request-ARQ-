#!/usr/bin/bash

for i in {1..105}
	do
		python3 server.py destination 0.05
	done
echo "Task 3"
for i in {1..10}
	do
		echo "Probability `awk \"BEGIN {print ($i)/100}\"`"
		count=5
		while [ $count -gt 0 ]
			do
				python3 server.py destination `awk "BEGIN {print ($i)/100}"`
				count=$((count-1))
		
			done
	done

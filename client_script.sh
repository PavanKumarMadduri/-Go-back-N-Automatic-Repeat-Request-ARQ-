#!/usr/bin/bash

server_ip=$1
filename=$2

for i in 1 2 4 8 16 32 64 128 256 512 1024
	do
		echo "Task 1 Window Size $i"	
		count=5
		while [ $count -gt 0 ]
			do
				python3 client.py $server_ip 7735 $filename $i 500 | tail -n 1
				count=$((count-1))
			done
	done

for i in {100..1000..100}
        do
                echo "Task 2 MSS $i"    
                count=5
                while [ $count -gt 0 ]
                        do
                                python3 client.py $server_ip 7735 $filename 64 $i | tail -n 1
                                count=$((count-1))
                        done
        done

for i in {1..10}
        do
                echo "Task 3 Probability `awk \"BEGIN {print ($i)/100}\"`"
                count=5
                while [ $count -gt 0 ]
                        do
                                python3 client.py $server_ip 7735 $filename 64 500 | tail -n 1
                                count=$((count-1))
                        done
        done

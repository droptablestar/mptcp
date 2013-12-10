#!/bin/bash

# number of switches
for (( i=2; i<6; i++ ))
do
    # number of tests per switch
    for (( j=0; j<2; j++))
    do
	echo "Testing $i switches TCP # $j"
	sudo ./test_switch.py -n $i
	for (( k=1; k<$i+1; k++ ))
	do
	    echo "Testing $i switches MTCP # $j FLOWS $k"
	    sudo ./test_switch.py -n $i --mptcp --ndiffports $k
	done
    done
done
#!/bin/bash

for (( k=4; k<9; k+=2 ))
do
    for (( i=1; i<13; i++ ))
    do
	for (( j=1; j<5; j++ ))
	do
	    echo "Testing k=$k s=$i r=$j TCP..."
	    sudo ./test0.py -k=$k -ns $i -nr $j
	    for (( m=2; m<9; m++ ))
	    do 
		echo "Testing k=$k s=$i r=$j MPTCP flows=$m..."
		sudo ./test0.py -k=$k -ns $i -nr $j -nflows $m 
	    done
	done
    done
done

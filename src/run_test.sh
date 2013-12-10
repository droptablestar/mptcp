#!/bin/bash

for (( s=1; s<8; s++ ))
do
    for (( r=1; r<8; r++ ))
    do
        echo "Testing s=$s r=$r TCP..."
        sudo ./test_ft.py -ns $s -nr $r
        for (( f=2; f<7; f++ ))
        do
            echo "Testing s=$s r=$r MPTCP flows=$f..."
            sudo ./test_ft.py -ns $s -nr $r -nflows $f --mptcp
        done
    done 
done  

mptcp
=====
To get things up and running first clone the repository:
```
git clone https://github.com/jreeseue/mptcp.git 
git submodule init 
git submodule update
```
From here mptcp will need to be setup inside of Mininet. To do this first
follow the instructions from http://github.com/bocon13/mptcp_setup. The code
for this will already be in mptcp_setup, as it is a submodule of this
project. Lastly, create copies of the test files with:
```
./createFiles.sh
```
At this point tests can be run from the src/ directory. To run the Fat Tree
test with 1 sender and 1 receiver use:
```
sudo ./test_ft.py
```
If more senders or receivers are desired this can be accomplished with the
-ns and -nr arguments. For 2 senders and 3 receivers use:
```
sudo ./test_ft.py -ns 2 -nr 3
```
If MPTCP is desired this can be accomplished with the -nflows argument. For
2 flows, 2 senders and 3 receivers use:
```
sudo ./test_ft.py -ns 2 -nr 3 -nflows 2
```
The N-switch tests can be run with:
```
sudo ./test_switch.py
```
If more switches are desired this can be accomplished with the -n argument. For
3 switches use:
```
sudo ./test_switch.py -n 3
```


Enjoy.

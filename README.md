mptcp
=====
To get things up and running the first time is to clone the project:
git clone https://github.com/jreeseue/mptcp.git
git submodule init
git submodule update

From here mptcp will need to be setup inside of Mininet. To do this first
follow the instructions from http://github.com/bocon13/mptcp_setup. The code
for this will already be in mptcp_setup, as it is a submodule of this
project. Lastly, create copies of the test files with ./createFiles.sh. At
this point tests can be run. To run the Fat Tree tests use:
sudo ./test_ft.py from the src/ directory. The N-switch tests can be run with
sudo ./test_switch.py.

Enjoy.

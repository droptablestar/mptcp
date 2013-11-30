mptcp
=====
Problems right noe:
- sockets are taking a uncontrollable amout of time.
- ping between hosts is working (intra-pod and inner-pod)
- some useful commands:

tcpdump -XX -n -i HOST-ethPORT
	e.g. (host 0_0_3, port 0) tcpdump -XX -n -i 0_0_3-eth0

sudo cp dcptopo.py ~/ripl/ripl/dcptopo.py

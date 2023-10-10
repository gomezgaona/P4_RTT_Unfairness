import json
import os

from mininet.net import Mininet
from mininet.node import Host
from mininet.link import TCLink
from mininet.topo import Topo
import threading
import time
import sys

def main():
    h = '/home/gomezgaj/mininet/util/m  h'
    os.system('sudo ovs-vsctl add-port s3 ens192')

    num_hosts = 100
    
    for i in range(1, int(num_hosts + 1)):
        os.system(f'{h}{i} ip route add 20.0.0.0/24 via 10.0.0.254  &> /dev/null')
        os.system(f'{h}{i} ip route change 20.0.0.0/24 via 10.0.0.254 proto static initcwnd 100000  &> /dev/null')
    
    '''
    for i in range(1, 26):
        os.system(f'{h}{i} tc qdisc add dev h{i}-eth0 root netem delay 20ms')

    for i in range(26, 51):
        os.system(f'{h}{i} tc qdisc add dev h{i}-eth0 root netem delay 50ms')

    for i in range(51, 76):
        os.system(f'{h}{i} tc qdisc add dev h{i}-eth0 root netem delay 70ms')   

    for i in range(76, 101):
        os.system(f'{h}{i} tc qdisc add dev h{i}-eth0 root netem delay 100ms') 
    '''

    time.sleep(2)

    print("Test started")
    print("Starting HTTP requests")
    cmd = f'{h}1 ./short_flows.sh long_buffer & >/dev/null'
    os.system(cmd)
    cmd = f'{h}1 ./ping_01.sh & >/dev/null'
    os.system(cmd)

    for i in range(2, 101):
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 250 -J -C cubic  -P 10 > results/out{i}.json &'
        os.system(cmd)
    print("Flows 1-100 joined")
    time.sleep(250)    
    print("Test is done!")

    cmd = f'{h}1 pkill ping'
    os.system(cmd)

    
if __name__ == '__main__':
    main()

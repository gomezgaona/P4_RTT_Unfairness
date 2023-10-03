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
        #os.system(f'{h}{i} ip route change 20.0.0.0/24 via 10.0.0.254 proto static initcwnd 5000000  &> /dev/null')
    
    time.sleep(2)

    print("Test started")
    for i in range(1, 26):
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 720 -J -C cubic -P 20 > results/out{i}.json &'
        os.system(cmd)
    print("Flows 1-25 joined")
    time.sleep(180)    

    for i in range(26, 51):
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 540 -J -C cubic -P 20 > results/out{i}.json &'
        os.system(cmd)
    print("Flows 26-50 joined")
    time.sleep(180)   

    for i in range(51, 76):
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 360 -J -C cubic -P 20 > results/out{i}.json &'
        os.system(cmd)
    print("Flows 51-75 joined")    
    time.sleep(180)   

    for i in range(76, num_hosts + 1):
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 180 -J -C cubic -P 20 > results/out{i}.json &'
        os.system(cmd)
    print("Flows 76-100 joined")

if __name__ == '__main__':
    main()

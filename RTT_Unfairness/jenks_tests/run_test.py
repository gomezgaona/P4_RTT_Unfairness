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

    for i in range(1, int(num_hosts)):
        #os.system(f'{h}{i} ip route add 20.0.0.0/24 via 10.0.0.254  &> /dev/null')
        os.system(f'{h}{i} ip route change 20.0.0.0/24 via 10.0.0.254 proto static initcwnd 500000  &> /dev/null')
    
    time.sleep(2)
    #Two flows
    
    cmd = f'{h}1 iperf3 -c 20.0.0.1 -t 120 -J -C bbr > results/out1.json &'
    os.system(cmd)
    time.sleep(30)
    cmd = f'{h}2 iperf3 -c 20.0.0.2 -t 90 -J -C bbr > results/out2.json &'
    os.system(cmd)
    
    '''
    for i in range(1, 3): #int(num_hosts)
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -n 1G -J -C bbr > results/out{i}.json &'
        os.system(cmd)
        #time.sleep(1)
    '''
if __name__ == '__main__':
    main()

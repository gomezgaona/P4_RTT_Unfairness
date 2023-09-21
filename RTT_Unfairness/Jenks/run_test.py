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
        os.system(f'{h}{i} ip route add 20.0.0.0/24 via 10.0.0.254  &> /dev/null')

    time.sleep(2)
    for i in range(1, 11): #int(num_hosts)
        cmd = f'{h}{i} iperf3 -c 20.0.0.{i} -t 120 -J -C cubic -P 8 > jenks_results/out{i}.json &'
        os.system(cmd)
        #time.sleep(1)
        
if __name__ == '__main__':
    main()

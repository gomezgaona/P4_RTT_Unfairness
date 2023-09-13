import json
import os

from mininet.net import Mininet
from mininet.node import Host
from mininet.link import TCLink
from mininet.topo import Topo
import threading
import time
import sys

def run_iperf_test(host, flow, dst_IP, duration, cc, BDP, i):
    
    cmd = f'{host} iperf3 -c {dst_IP} -t {duration}  -C {cc} -J > json_files/h{flow}_{cc}_{BDP}BDP_out_{i}.json &'
    os.system(cmd)

def change_BDP(BDP):
    btlbw = 1e9
    delay = 20e-3
    burst = int(btlbw/250/8)
    limit = int(BDP*btlbw*delay*(1.024**2)/8) # Setting the limit to BDP
    sys.stdout.write(f"\rCurrent BDP: {BDP}\n" )

    tbf_cmd = f'tc qdisc change dev s1-eth1 parent 1: handle 2: tbf rate {btlbw} burst {burst} limit {limit}'
    os.system(tbf_cmd)

def main():
    h = '/home/admin/mininet/util/m h'
    os.system('sudo ovs-vsctl add-port s3 ens192')
    #os.system('sudo ovs-vsctl add-port s2 ens192')
    '''
    for i in range(1, Runs + 1):
        for bdp in BDP:

            change_BDP(bdp)
        
            flow = 1
            run_iperf_test(f"{h}{flow}", flow, f"10.0.1.{flow}", duration, "cubic", bdp, i)
            flow = 2
            run_iperf_test(f"{h}{flow}", flow, f"10.0.1.{flow}", duration, "bbr", bdp, i)

            time.sleep(duration + 3)

    sys.stdout.write("\rTest is done\n")
    '''
if __name__ == '__main__':
    main()

    
    
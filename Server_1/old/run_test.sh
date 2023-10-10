#!/bin/bash

# Bridge to the HW interface
sudo ifconfig ens192 0
sudo ifconfig ens192 up
sudo ovs-vsctl add-port s1 ens192

# Hosts
h1="/home/gomezgaj/mininet/util/m h1"
h2="/home/gomezgaj/mininet/util/m h2"
h3="/home/gomezgaj/mininet/util/m h3"
h4="/home/gomezgaj/mininet/util/m h4"
h5="/home/gomezgaj/mininet/util/m h5"
h6="/home/gomezgaj/mininet/util/m h6"
h7="/home/gomezgaj/mininet/util/m h7"
h8="/home/gomezgaj/mininet/util/m h8"

# Route to receivers
$h1 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h2 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h3 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h4 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 120000"
$h5 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h6 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h7 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"
$h8 "ip route add 20.0.0.0/24 via 10.0.0.254 proto static initvwnd initcwnd 12000"

# TCP buffer size
$h1 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h1 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h2 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h2 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h3 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h3 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h4 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h4 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h5 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h5 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h6 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h6 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h7 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h7 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

$h8 "sudo sysctl -w net.ipv4.tcp_wmem='10240 87380 2000000000'"
$h8 "sudo sysctl -w net.ipv4.tcp_rmem='10240 87380 2000000000'"

# Set RTT Unfairness
#$h2 'tc qdisc del dev h2-eth0 root'
#$h2 'tc qdisc add dev h2-eth0 root netem delay 30ms'

#Run iperf3
$h1 "iperf3 -c 20.0.0.1 -t 300 -J -C cubic -P 4 > out1.json &"
sleep 60
$h2 "iperf3 -c 20.0.0.2 -t 240 -J -C cubic -P 4 > out2.json &"
sleep 60
$h3 "iperf3 -c 20.0.0.3 -t 180 -J -C cubic -P 4 > out3.json &"
sleep 60
$h4 "iperf3 -c 20.0.0.4 -t 120 -J -C cubic -P 10 > out4.json"

#sleep 40
#$h4 "iperf3 -c 20.0.0.4 -t 200 -J -C bbr  > out4.json &"
#sleep 40
#$h5 "iperf3 -c 20.0.0.5 -t 160 -J -C bbr   > out5.json &"
#sleep 40
#$h6 "iperf3 -c 20.0.0.6 -t 120 -J -C bbr   > out6.json &"
#sleep 40
#$h7 "iperf3 -c 20.0.0.7 -t 80 -J -C bbr   > out7.json &"
#sleep 40
#$h8 "iperf3 -c 20.0.0.8 -t 40 -J -C bbr   > out8.json &"

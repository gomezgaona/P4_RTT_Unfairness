import threading
import Listening_socket
import ipaddress
import warnings
import multiprocessing
######Juniper packages#######
import sys
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.start_shell import StartShell
from ncclient import manager
import paramiko
import time
import os
import jenkspy

class Measurements:
    def __init__(self):
        self.N = 0
        self.stat_LOSS = 0
        self.stat_SRTT = 0
        self.stat_Q = 0
        self.stat_link = 0
        self.IP_addr = 0

        # Initiate the socket
        self.Socket = Listening_socket.Socket(port=60002).get_Listener()
        
        # Start measurement collection
        self.start_measurements_thread()

    def start_measurements_thread(self):
        # Start the measurement collection thread
        collect_measurements_thread = threading.Thread(target=self.collect_measurements, name="collect_measurements")
        collect_measurements_thread.start()

    def collect_measurements(self):
       
        # Receive measurements from the P4 switch
        measurements = self.Socket.recv(1024)
        measurements = measurements.decode()
        
        # Extract individual measurements and convert them to floats
        self.IP_addr, self.stat_SRTT, self.N, *_ = map(float, measurements.split('_'))#, self.stat_LOSS, self.stat_Q, self.stat_link 
        
        IP =  str(ipaddress.ip_address(int(self.IP_addr)))
        RTT = int(self.stat_SRTT)/1e9
        N = int(self.N)

        return IP, RTT,N 

    def available_traffic(self):
        return self.N != 0


def open_ssh_J3():
    #Credentials
    device = {
        'hostname': '10.173.85.40',     # IP address of the router
        'port': 22,                   # SSH port (default: 22)
        'username': 'gomezgaj',       # SSH username
        'password': 'juniper3_2023',       # SSH password
    }

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**device)

    # Start an interactive shell session
    shell = ssh.invoke_shell()

    # Wait for the shell prompt
    time.sleep(1)
    output = shell.recv(65535).decode('utf-8')
    while '>' not in output:
        output = shell.recv(65535).decode('utf-8')

    # Set the CLI in configuration mode
    shell.send("edit" + '\n')

    return ssh, shell

def close_ssh_J3(ssh, shell):
    # Close the SSH connection
    shell.close()
    ssh.close()

def send_cmds_J3(shell, *junos_cmds):
    
    # Send configuration commands
    for command in junos_cmds:
        shell.send(command + '\n')
        #time.sleep(0.75)
        
        cmd_output = shell.recv(65535).decode('utf-8')
        #print(cmd_output)
  
    return cmd_output
 
def add_IP_queue(shell, IP, N, queue):
    result = 0
    # Redirect flows to a specific queue
    redirect_q1 = "set firewall family inet filter source_IP_filter term criteria_1 from source-address "
    redirect_q2 = "set firewall family inet filter source_IP_filter term criteria_2 from source-address "
    redirect_q3 = "set firewall family inet filter source_IP_filter term criteria_3 from source-address "
    redirect_q4 = "set firewall family inet filter source_IP_filter term criteria_4 from source-address "

    if (N <= 4 and N != 0):
        rate = str(int(10/N))
    else:
        rate = str(int(10/4))
   
        print("Current rate: ", rate)
        if (queue == "q1"):
            result = send_cmds_J3(shell,
                                  #remove_IP_q2 + IP, 
                                  redirect_q1 + IP,
                                  "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                  "commit",
                                  )
        elif (queue == "q2"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   redirect_q2 + IP,
                                   "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
        elif (queue == "q3"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   redirect_q3 + IP,
                                   "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
        elif (queue == "q4"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   redirect_q4 + IP,
                                   "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
        
    return result

def load_initial_conf_J3():
     ssh, shell = open_ssh_J3()
     send_cmds_J3(shell,
                 "load update base-config",
                 "commit")
     print("Clearing the configuration")
 
def Jenks_classifier(RTT_flows):
    if len(RTT_flows) > 3:
        limits = jenkspy.jenks_breaks(RTT_flows, n_classes=4)
        return limits
    else:
        limits = jenkspy.jenks_breaks(RTT_flows, n_classes=len(RTT_flows))

        return limits
    
def update_queues(RTTs, IP, N):
    q1 = []
    q2 = []
    q3 = []
    q4 = []

    IP_q1 = []
    IP_q2 = []
    IP_q3 = []
    IP_q4 = []

    redirect_q1 = "set firewall family inet filter source_IP_filter term criteria_1 from source-address "
    redirect_q2 = "set firewall family inet filter source_IP_filter term criteria_2 from source-address "
    redirect_q3 = "set firewall family inet filter source_IP_filter term criteria_3 from source-address "
    redirect_q4 = "set firewall family inet filter source_IP_filter term criteria_4 from source-address "

    limits = Jenks_classifier(RTTs)
    ssh, shell = open_ssh_J3()
    
    print("Loading base configuration")
    send_cmds_J3(shell, "load update base-config")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_1 transmit-rate 2g exact")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_2 transmit-rate 2g exact")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_3 transmit-rate 2g exact")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_4 transmit-rate 2g exact")

    temporal_1 = str(int( 1e3 * (limits[0] + limits[1])/2) )
    temporal_2 = str(int( 1e3 * (limits[1] + limits[2])/2) )
    temporal_3 = str(int( 1e3 * (limits[2] + limits[3])/2) )
    temporal_4 = str(int( 1e3 * (limits[3] + limits[4])/2) )

    print("Temporal 1: ",temporal_1)
    print("Temporal 2: ",temporal_2)
    print("Temporal 3: ",temporal_3)
    print("Temporal 4: ",temporal_4)

    send_cmds_J3(shell,"set class-of-service schedulers scheduler_1 buffer-size temporal "+temporal_1+"k")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_2 buffer-size temporal "+temporal_2+"k")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_3 buffer-size temporal "+temporal_3+"k")
    send_cmds_J3(shell,"set class-of-service schedulers scheduler_4 buffer-size temporal "+temporal_4+"k")

    print("Updating queue assignment")

    for i in range(0, len(RTTs) ):
        if(limits[0] <= RTTs[i] <= limits[1]):
            q1.append(RTTs[i])
            IP_q1.append(IP[i])
            #add_IP_queue(shell, IP[i], N, "q1")
            result =  send_cmds_J3(shell, redirect_q1 + IP[i])  
        elif(limits[1] <= RTTs[i] <= limits[2]):
            q2.append(RTTs[i])
            IP_q2.append(IP[i])
            #add_IP_queue(shell, IP[i], N, "q2")
            result =  send_cmds_J3(shell, redirect_q2 + IP[i])  
        elif(limits[2] <= RTTs[i] <= limits[3]):
            q3.append(RTTs[i])
            IP_q3.append(IP[i])
            #add_IP_queue(shell, IP[i], N, "q3")
            result =  send_cmds_J3(shell, redirect_q3 + IP[i])  
        elif(limits[3] <= RTTs[i] <= limits[4]):
            q4.append(RTTs[i])
            IP_q4.append(IP[i])
            #add_IP_queue(shell, IP[i], N, "q4")
            result =  send_cmds_J3(shell, redirect_q4 + IP[i])  

   
    print("Updated queue")
    print("Queue 1:", q1)
    print("Queue 2:", q2)
    print("Queue 3:", q3)
    print("Queue 4:", q4)

    print("Configuration commited")
    send_cmds_J3(shell, "commit")

    with open("q1.dat", "w") as file:
        for item1, item2 in zip(IP_q1, q1):
            #file.write(str(item1) +" "+str(item2) + "\n")
            file.write(str(item2) + ",")
    
    with open("q2.dat", "w") as file:
        for item1, item2 in zip(IP_q2, q2):
            #file.write(str(item1) +" "+str(item2) + "\n")
            file.write(str(item2) + ",")

    with open("q3.dat", "w") as file:
        for item1, item2 in zip(IP_q3, q3):
            #file.write(str(item1) +" "+str(item2) + "\n")
            file.write(str(item2) + ",")

    with open("q4.dat", "w") as file:
        for item1, item2 in zip(IP_q4, q4):
            #file.write(str(item1) +" "+str(item2) + "\n")
            file.write(str(item2) + ",")

    return q1, q2, q3, q4

def main():   
    IPs = []
    RTTs = []
    N_flows = 0
    q1 = []
    q2 = []
    q3 = []
    q4 = [] 

    limits = [-1, -1, -1, -1]
    flag = False

    ssh, shell = open_ssh_J3()
    time.sleep(1)
    load_initial_conf_J3()
    measurements = Measurements()
    measurements.start_measurements_thread()

    while True:    
        IP, RTT, N = measurements.collect_measurements()
        #print("IP: ", IP, "RTT: ", RTT, "# Flows: ", N)
        
        if (IP != "0.0.0.0" and IP not in IPs):
            IPs.append(IP)
            RTTs.append(RTT)
            print("IPs:", IPs)
            print("RTTs:", RTTs)
            N_flows = len(IPs)
            limits = Jenks_classifier(RTTs)
        
            if(limits[0] <= RTT <= limits[1]):
                print("Redirected to q2")
                #result = add_IP_queue(shell, IP, N_flows, "q2")
                q1.append(RTT)
            elif(limits[1] <= RTT <= limits[2]):
                print("Redirected to q3")
                #result = add_IP_queue(shell, IP, N_flows, "q3")
                q2.append(RTT)
            elif(limits[2] <= RTT <= limits[3]):
                print("Redirected to q4")
                #result = add_IP_queue(shell, IP, N_flows, "q4")
                q3.append(RTT)
            elif(limits[3] <= RTT <= limits[4]):
                print("Redirected to q1")
                #result = add_IP_queue(shell, IP, N_flows, "q1")
                q4.append(RTT)
        
        #print("Queue 1:", q1)
        #print("Queue 2:", q2)
        #print("Queue 3:", q3)
        #print("Queue 4:", q4)
        #print("\n")
        print("Number of flows: ", N_flows)

        if N_flows >= 98 and flag == False :
            q1, q2, q3, q4 = update_queues(RTTs, IPs, N_flows)    
            flag = True
            
if __name__ == "__main__": 
    main()

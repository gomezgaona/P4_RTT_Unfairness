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
    #time.sleep(1)
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
    # Remove IP from a queue
    remove_IP_q1 = "delete firewall family inet filter source_IP_filter term criteria_1 from source-address "
    remove_IP_q2 = "delete firewall family inet filter source_IP_filter term criteria_2 from source-address "
    remove_IP_q3 = "delete firewall family inet filter source_IP_filter term criteria_3 from source-address "
    remove_IP_q4 = "delete firewall family inet filter source_IP_filter term criteria_4 from source-address "
    remove_IP_q5 = "delete firewall family inet filter source_IP_filter term criteria_5 from source-address "
    remove_IP_q6 = "delete firewall family inet filter source_IP_filter term criteria_6 from source-address "
    remove_IP_q7 = "delete firewall family inet filter source_IP_filter term criteria_7 from source-address "
    remove_IP_q8 = "delete firewall family inet filter source_IP_filter term criteria_8 from source-address "
    
    # Redirect flows to a specific queue
    redirect_q1 = "set firewall family inet filter source_IP_filter term criteria_1 from source-address "
    redirect_q2 = "set firewall family inet filter source_IP_filter term criteria_2 from source-address "
    redirect_q3 = "set firewall family inet filter source_IP_filter term criteria_3 from source-address "
    redirect_q4 = "set firewall family inet filter source_IP_filter term criteria_4 from source-address "
    #redirect_q5 = "set firewall family inet filter source_IP_filter term criteria_5 from source-address "
    #redirect_q6 = "set firewall family inet filter source_IP_filter term criteria_6 from source-address "
    #redirect_q7 = "set firewall family inet filter source_IP_filter term criteria_7 from source-address "
    #redirect_q8 = "set firewall family inet filter source_IP_filter term criteria_8 from source-address "
    group_1 = ["10.0.0.1","10.0.0.2","10.0.0.3","10.0.0.4","10.0.0.5","10.0.0.6","10.0.0.7",
               "10.0.0.8","10.0.0.9","10.0.0.10","10.0.0.11","10.0.0.12","10.0.0.13","10.0.0.14",
               "10.0.0.15","10.0.0.16","10.0.0.17","10.0.0.18","10.0.0.19","10.0.0.20",
               "10.0.0.21","10.0.0.22","10.0.0.23","10.0.0.24","10.0.0.25"]
    group_2 = ["10.0.0.26","10.0.0.27","10.0.0.28","10.0.0.29","10.0.0.30","10.0.0.31","10.0.0.32",
               "10.0.0.33","10.0.0.34","10.0.0.35","10.0.0.36","10.0.0.37","10.0.0.38","10.0.0.39",
               "10.0.0.40","10.0.0.41","10.0.0.42","10.0.0.43","10.0.0.44","10.0.0.45",
               "10.0.0.46","10.0.0.47","10.0.0.48","10.0.0.49","10.0.0.50"]
    group_3 = ["10.0.0.51","10.0.0.52","10.0.0.53","10.0.0.54","10.0.0.55","10.0.0.56","10.0.0.57",
               "10.0.0.58","10.0.0.59","10.0.0.60","10.0.0.61","10.0.0.62","10.0.0.63","10.0.0.64",
               "10.0.0.65","10.0.0.66","10.0.0.67","10.0.0.68","10.0.0.69","10.0.0.70",
               "10.0.0.71","10.0.0.72","10.0.0.73","10.0.0.74","10.0.0.75"]
    group_4 = ["10.0.0.76","10.0.0.77","10.0.0.78","10.0.0.79","10.0.0.80","10.0.0.81","10.0.0.82",
               "10.0.0.83","10.0.0.84","10.0.0.85","10.0.0.86","10.0.0.87","10.0.0.88","10.0.0.89",
               "10.0.0.90","10.0.0.91","10.0.0.92","10.0.0.93","10.0.0.94","10.0.0.95",
               "10.0.0.96","10.0.0.97","10.0.0.98","10.0.0.99","10.0.0.100"]
    
    result = 0
    
    if (IP != "0.0.0.0"): 
        if (IP in group_1):      
            rate = str(int(10/1))
        elif  (IP in group_2):
            rate = str(int(10/2))
        elif  (IP in group_3):
            rate = str(int(10/3))
        elif  (IP in group_4):
            rate = str(int(10/4))

        print("Current rate: ", rate)
        if (queue == "q1"):
            result = send_cmds_J3(shell,
                                  #remove_IP_q2 + IP, 
                                  #redirect_q1 + IP,
                                  "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                  "set class-of-service schedulers scheduler_4 transmit-rate "+rate+"g exact",
                                  "set class-of-service schedulers scheduler_2 transmit-rate "+rate+"g exact",
                                  "set class-of-service schedulers scheduler_3 transmit-rate "+rate+"g exact",
                                  "commit",
                                  )
        elif (queue == "q2"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   #redirect_q2 + IP,
                                   "set class-of-service schedulers scheduler_2 transmit-rate "+rate+"g exact",
                                   #"set class-of-service schedulers scheduler_3 transmit-rate "+rate+"g exact",
                                   #"set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
        elif (queue == "q3"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   #redirect_q3 + IP,
                                   "set class-of-service schedulers scheduler_3 transmit-rate "+rate+"g exact",
                                   "set class-of-service schedulers scheduler_1 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
        elif (queue == "q4"):  
            result =  send_cmds_J3(shell,
                                   #remove_IP_q1 + IP, 
                                   #redirect_q4 + IP,
                                   "set class-of-service schedulers scheduler_4 transmit-rate "+rate+"g exact",
                                   "set class-of-service schedulers scheduler_2 transmit-rate "+rate+"g exact",
                                   "set class-of-service schedulers scheduler_3 transmit-rate "+rate+"g exact",
                                   "commit",
                                   )  
       
       
    return result

def load_initial_conf_J3():
     ssh, shell = open_ssh_J3()
     send_cmds_J3(shell,
                 "load update four-groups",
                 "commit")
     print("Clearing the configuration")
 

def main():   
    threshold = [20e-3, 40e-3, 60e-3, 80e-3]
    flow_info = {}
    IPs = []
    current_q = 0

    ssh, shell = open_ssh_J3()
    time.sleep(1)
    load_initial_conf_J3()
    measurements = Measurements()
    measurements.start_measurements_thread()

    group_1 = ["10.0.0.1","10.0.0.2","10.0.0.3","10.0.0.4","10.0.0.5","10.0.0.6","10.0.0.7",
               "10.0.0.8","10.0.0.9","10.0.0.10","10.0.0.11","10.0.0.12","10.0.0.13","10.0.0.14",
               "10.0.0.15","10.0.0.16","10.0.0.17","10.0.0.18","10.0.0.19","10.0.0.20",
               "10.0.0.21","10.0.0.22","10.0.0.23","10.0.0.24","10.0.0.25"]
    group_2 = ["10.0.0.26","10.0.0.27","10.0.0.28","10.0.0.29","10.0.0.30","10.0.0.31","10.0.0.32",
               "10.0.0.33","10.0.0.34","10.0.0.35","10.0.0.36","10.0.0.37","10.0.0.38","10.0.0.39",
               "10.0.0.40","10.0.0.41","10.0.0.42","10.0.0.43","10.0.0.44","10.0.0.45",
               "10.0.0.46","10.0.0.47","10.0.0.48","10.0.0.49","10.0.0.50"]
    group_3 = ["10.0.0.51","10.0.0.52","10.0.0.53","10.0.0.54","10.0.0.55","10.0.0.56","10.0.0.57",
               "10.0.0.58","10.0.0.59","10.0.0.60","10.0.0.61","10.0.0.62","10.0.0.63","10.0.0.64",
               "10.0.0.65","10.0.0.66","10.0.0.67","10.0.0.68","10.0.0.69","10.0.0.70",
               "10.0.0.71","10.0.0.72","10.0.0.73","10.0.0.74","10.0.0.75"]
    group_4 = ["10.0.0.76","10.0.0.77","10.0.0.78","10.0.0.79","10.0.0.80","10.0.0.81","10.0.0.82",
               "10.0.0.83","10.0.0.84","10.0.0.85","10.0.0.86","10.0.0.87","10.0.0.88","10.0.0.89",
               "10.0.0.90","10.0.0.91","10.0.0.92","10.0.0.93","10.0.0.94","10.0.0.95",
               "10.0.0.96","10.0.0.97","10.0.0.98","10.0.0.99","10.0.0.100"]
    
    while True:    
        IP, RTT, N = measurements.collect_measurements()
        print("IP: ", IP, "RTT: ", RTT, "# Flows: ", N)
        
        if (IP != "0.0.0.0" and IP not in IPs):
            if (IP in group_1):
                #print("Redirect "+ IP + " to queue 2 (Low latency queue)")
                result = add_IP_queue(shell, IP, N, "q2")
                current_q = "q2"
                flag = 1

            elif (IP in group_2):
               # print("Redirect "+ IP + " to queue 3 ([20-40ms])")
                result = add_IP_queue(shell, IP, N, "q3")
                current_q = "q3"
                flag = 2

            elif (IP in group_3):
                #print("Redirect "+ IP + " to queue 4 ([40-60ms])")
                result = add_IP_queue(shell, IP, N, "q4")
                current_q = "q4"
                flag = 3

            elif (IP in group_4):
                #print("Redirect "+ IP + " to queue 1 ([60-80ms])")
                result = add_IP_queue(shell, IP, N, "q1")
                current_q = "q1"
                flag = 4

            IPs.append(IP)
            print("IPs already enqueued: ", IPs)
            print("Redirected IP: ", IP)
            print("Current # flows: ", N)
            print("Current queue: ", current_q)

if __name__ == "__main__":
    
    main()

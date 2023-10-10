import threading
#import Database
import Listening_socket
import ipaddress

class Measurements:
    def __init__(self):
        self.N = 0
        self.stat_LOSS = 0
        self.stat_SRTT = 0
        self.stat_Q = 0
        self.stat_link = 0
        self.IP_addr = 0
        # Initiate database instance
        #self.DB = Database.database()

        # Initiate the socket
        self.Socket = Listening_socket.Socket(port=60002).get_Listener()
        
        # Start measurement collection
        self.start_measurements_thread()

    def start_measurements_thread(self):
        # Start the measurement collection thread
        collect_measurements_thread = threading.Thread(target=self.collect_measurements, name="collect_measurements")
        collect_measurements_thread.start()

    def collect_measurements(self):
        while True:
            # Receive measurements from the P4 switch
            measurements = self.Socket.recv(1024)
            measurements = measurements.decode()
            #print(measurements)
            # Extract individual measurements and convert them to floats
            self.IP_addr, self.N, self.stat_SRTT, self.stat_LOSS, self.stat_Q, self.stat_link = map(float, measurements.split('_'))
            print(ipaddress.ip_address(int(self.IP_addr)), self.stat_SRTT )#, self.stat_LOSS, self.stat_Q, self.stat_link)ipaddress.ip_address()
            # Write measurements to InfluxDB
            #self.DB.write_measurement("losses", "loss", self.stat_LOSS)
            #self.DB.write_measurement("rtts", "rtt", self.stat_SRTT)
            #self.DB.write_measurement("queues", "queue", self.stat_Q)
            #self.DB.write_measurement("links", "link", self.stat_link)
            #self.DB.write_measurement("Ns", "N", self.N)

    def available_traffic(self):
        return self.N != 0
    
measurements = Measurements()

import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS    

"""
    This file declares the database class. The class initiate the necessary connections with an InfluxDB database. 
"""

class database():
    def __init__(self):    
    # InfluxDB configuration
        self.bucket = "p4bs"
        self.org = "cilab"
        self.token = "1bxmgQrw9B5WIEtiGciEvBW1ou_X0tfUwv3l8Rp9EiwoLbaIju2bCup2HyEIrVee3WbiC-q6QY7APGImIridng=="
        self.url = "http://10.173.85.43:8086"
        
        # Initialize InfluxDB client and write API
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # Delteting then creating the bucket
        os.system("influx bucket delete -n "+self.bucket +" -o "+self.org)
        os.system("influx bucket create -n "+self.bucket +" -o "+self.org)

    def get_writer(self):
        return self.write_api
    
    def write_measurement(self, measurement, field, value):
        # Create a Point and write the measurement to InfluxDB
        point = (
            Point(measurement)
            .tag("tagname1", "tagvalue1")
            .field(field, value)
        )
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
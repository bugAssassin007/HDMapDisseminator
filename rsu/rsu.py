
import zmq.asyncio
import asyncio
import threading
import time
from threading import *
import time
from tabulate import tabulate
import csv
import math


delays_logs_csv="delay_logs.csv"
# Create a new CSV file with headers
def create_csv_file(file_path, headers):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    print(f"CSV file '{file_path}' created with headers: {headers}")

# Add a new row to the CSV file
def add_row_to_csv(file_path, row_data):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row_data)
    print(f"Row added to CSV file '{file_path}': {row_data}")

def reverse_mapping(original_dict):
    reverse_dict = {}

    # Iterate over the original dictionary
    for key, value in original_dict.items():
        # Check if the value already exists in the reverse dictionary
        if value in reverse_dict:
            # Append the key to the existing list in the reverse dictionary
            reverse_dict[value].append(key)
        else:
            # Create a new list in the reverse dictionary with the key
            reverse_dict[value] = [key]


    return reverse_dict



def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2 = float(lat2)
    lat2_rad = math.radians(lat2)
    lon2 = float(lon2)
    lon2_rad = math.radians(lon2)

    # Difference between latitudes and longitudes
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Calculate the distance
    distance = earth_radius * c

    return distance*1000

class RSU:
    def __init__(self,id,  sip,sport,algo,pattern):
        self.sip=sip
        self.sport=sport
        self.id=id
        #self.input_file=input_file
        self.algo=algo
        self.pattern=pattern
        self.table=[]
        self.data_transposed=[]
        self.global_min_ts=-1
        self.broadcast_channel={}
        self.tile_to_slot = {}
        self.bandwidth=10 #Given in MHz
        self.mcs=14
        num_elements = 10

        self.delays=[None] * num_elements #need to initialise array before assigning values
        self.rsu_pos=[36.906882,-1.185770]
        self.tile_props={"osm":[1,5],"pcd":[2,0.3],"pcd_mid":[2,2]}
        self.tile_schedule={}
        self._loop = asyncio.get_event_loop()
        self._context = zmq.asyncio.Context()
        self._socket = self._context.socket(zmq.REP)
        #self._socket.bind("tcp://*:5555")
        self._socket.bind('tcp://%s:%s'%(self.sip,self.sport))
        # Start the daemon thread to print "Hello"
        self._hello_thread = threading.Thread(target=self._print_broadcast, daemon=True)
        self._hello_thread.start()

    
    
    def initialise_broadcast_channel_with_segment(self):
        #broadcast_channel={}
        input_file = 'tobroadcast.csv'  # Replace with the actual file name
        with open(input_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                slot_number = int(row[0])
                tile_name = row[1]
                self.broadcast_channel[slot_number] = tile_name

            # Create empty lists to store the data
            column1 = []
            column2 = []
                    
        # Loop through the dictionary items
        for slot_number, tile_name in self.broadcast_channel.items():
            # Add the slot number to the first list
            column1.append(str(slot_number))

            # Add the tile name to the second list
            column2.append(tile_name)
        self.table.append(column1)
        self.table.append(column2)
        self.data_transposed = list(map(list, zip(*self.table)))
        #print(self.data_transposed)

    def calculate_transmit_delay_at_vehicle(self,request):
        #time to acquire channel
        #time to put data onto the channel
        time_to_acquire_channel=0
        packet_size=0#"size of request packet"
        data_rate=1#uplink data rate
        transmit_time=packet_size/data_rate
        return transmit_time

    def calculate_propagation_delay_from_vehicle_to_rsu(self,request):
        #time at which request for received at RSU-time at which request was sent
        #distance between RSU and vehicle when the request was sent/speed of light
        veh_lat=request[2]
        veh_long=request[3]
        #veh_speed=float(request[4]) if float(request[4])!=0.0 else 0.1
        speed_of_light=3*10**8
        #TO DO:Change the vehicle lat and long to, converted tile lat and long.
        distance=(calculate_distance(self.rsu_pos[0],self.rsu_pos[1],veh_lat,veh_long))
        self.delays[9]=distance
        print("Distance between vehicle and RSU",distance)
        propagation_delay=distance/speed_of_light
        print("time to reach tile", propagation_delay)
        #return time_to_reach_tile
        
        return propagation_delay
    
    def calculate_processing_delay_at_RSU(self):
        #Time to acquire channel, assumed to be 0
        #Time to schedule a requested tile using algo. TO DO: Run mergesort with 200 elements.
        #Tx= packet size/PHY data rate
        #MIMO=8
        packet_size=float(12*(2**10)*8)  #12KB assumed per 1ms.
        #transmit_time=packet_size/100
        #per request it will be neglglible
        process_delay=0.0008 #around 0.8 milliseconds for mergesort on 200 elements.
        downlink_phy_rate=100*10e6#100Mbps if 8x8 MIMO, MCS=14
        transmit_delay=packet_size/downlink_phy_rate
        process_transmit_delay=transmit_delay+process_delay
        self.delays[5]=process_delay
        self.delays[6]=transmit_delay
        print("Transmit delay",transmit_delay)
        return process_transmit_delay
    
    def calculate_propagation_delay_from_rsu_to_vehicle(self,request):
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=float(request[4]) if float(request[4])!=0.0 else 0.1
        #TO DO:Add the drifted Lat and Long.
        speed_of_light=3e8
        propagation_delay=(calculate_distance(self.rsu_pos[0],self.rsu_pos[1],veh_lat,veh_long))/speed_of_light
        
        additional_delay=(calculate_distance(self.rsu_pos[0],self.rsu_pos[1],veh_lat,veh_long))/veh_speed
        print("additional delay",additional_delay)
        print("time to reach tile", propagation_delay)
        #return time_to_reach_tile
        
        return propagation_delay
    
    def calculate_total_delay_without_pr(self,request):
        a=self.calculate_transmit_delay_at_vehicle(request)
        self.delays[3]=a
        b=self.calculate_propagation_delay_from_vehicle_to_rsu(request)
        self.delays[4]=b
        #c=self.calculate_processing_delay_at_RSU()
        self.delays[5]=0.0
        self.delays[6]=0.0
        d=self.calculate_propagation_delay_from_rsu_to_vehicle(request)
        self.delays[7]=d
        total_delay_per_request=a+b+d
        self.delays[8]=total_delay_per_request
        #print("Total delay per request",a,b,d,total_delay_per_request) 
        return total_delay_per_request
    
    def calculate_total_delay_with_pr(self,request):
        a=self.calculate_transmit_delay_at_vehicle(request)
        self.delays[3]=a
        b=self.calculate_propagation_delay_from_vehicle_to_rsu(request)
        self.delays[4]=b
        c=self.calculate_processing_delay_at_RSU()
        d=self.calculate_propagation_delay_from_rsu_to_vehicle(request)
        self.delays[7]=d
        total_delay_per_request=a+b+c+d
        self.delays[8]=total_delay_per_request
        #print("Total delay per request",a,b,c,d,total_delay_per_request) 
        return total_delay_per_request




    def initialise_broadcast_channel_with_grid(self):
        

        # Generate slot numbers from 1 to 100
        #for slot_number in range(1, 10):
        slot_number=1
        # Generate tile names in the format "(10, 10)_x_y"
        for x in range(0, 10):
            for y in range(0, 10):
                tile_name = f"(10, 10)_{x}_{y}_osm"
                self.broadcast_channel[slot_number] = tile_name
                slot_number += 1
                tile_name = f"(10, 10)_{x}_{y}_pcd"
                self.broadcast_channel[slot_number] = tile_name
                slot_number += 1
        

        # Create empty lists to store the data
        column1 = []
        column2 = []
                    
        # Loop through the dictionary items
        for slot_number, tile_name in self.broadcast_channel.items():
            # Add the slot number to the first list
            column1.append(str(slot_number))

            # Add the tile name to the second list
            column2.append(tile_name)
        self.table.append(column1)
        self.table.append(column2)
        # # Add a header to the dictionary
        # header = ["Slot Number", "Tile Name"]
        # broadcast_channel = {k: v for k, v in zip(header, broadcast_channel.items())}
        self.data_transposed = list(map(list, zip(*self.table)))


    def _print_broadcast(self):
        self.initialise_broadcast_channel_with_grid()
        tile_to_slot = reverse_mapping(self.broadcast_channel)
        while True:
            #print(broadcast_channel)
            #print(tabulate(self.data_transposed, headers='firstrow', tablefmt='fancy_grid'))
            #print("Hello")
            #print("Printing tabulated data", data_transposed)
            time.sleep(1)
    
    def get_validity_of_tile(self,tile_name):
        tile_type=tile_name.split('_')[3]
        print("tile type and validity",tile_type,self.tile_props[tile_type])
        return self.tile_props[tile_type][1]
    
    def get_slot_when_tile_published_next(self,tile_name):
        tile_to_slot = reverse_mapping(self.broadcast_channel)

        print("slot when tile published",min(tile_to_slot[tile_name]))
        return min(tile_to_slot[tile_name])
    
    def calculate_wait_time(self,slot_when_tile_published_next):
        current_time=time.time()
        currrent_slot=int(current_time-self.global_min_ts)
        wait_time=slot_when_tile_published_next-currrent_slot
        print("Wait time",wait_time)
        return wait_time

    def calculate_time_to_reach_requested_tile(self,request):
        #distance between RSU and vehicle/speed of vehicle
        #request=request.decode()
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=float(request[4]) if float(request[4])!=0.0 else 0.1
        #TO DO:Change the vehicle lat and long to, converted tile lat and long.
        time_to_reach_tile=(calculate_distance(self.rsu_pos[0],self.rsu_pos[1],veh_lat,veh_long))/veh_speed
        print("time to reach tile", time_to_reach_tile)
        return time_to_reach_tile

    def add_tile_to_current_slot(self,tile_name):
        tile_to_slot = reverse_mapping(self.broadcast_channel)
        self.broadcast_channel[self.current_slot_time],self.broadcast_channel[tile_to_slot[tile_name][0]]=self.broadcast_channel[tile_to_slot[tile_name][0]],self.broadcast_channel[self.current_slot_time]
    



    def add_tile_to_slot_based_on_priority(self,request,jobs):
        #jobs=[['tile_name',deadline, priority]]
        jobs = [['a', 2, 100], ['b', 1, 40], ['c', 2, 80], ['d', 1, 20], ['e', 3, 60]]
        print("Following is maximum profit sequence of jobs")

        # length of array
        n = len(jobs)
        t = 3

        # Sort all jobs according to
        # decreasing order of profit
        for i in range(n):
            for j in range(n - 1 - i):
                if jobs[j][2] < jobs[j + 1][2]:
                    jobs[j], jobs[j + 1] = jobs[j + 1], jobs[j]

        # To keep track of free time slots
        result = [False] * t

        # To store result (Sequence of jobs)
        job = ['-1'] * t

        # Iterate through all given jobs
        for i in range(len(jobs)):

            # Find a free slot for this job
            # (Note that we start from the
            # last possible slot)
            for j in range(min(t - 1, jobs[i][1] - 1), -1, -1):

                # Free slot found
                if result[j] is False:
                    result[j] = True
                    job[j] = jobs[i][0]
                    break

        # print the sequence
        print(job)

    def tobroadcast(self,request):
        #to decide whether to broadcast tile or not
        #request=request.decode()
        request=request.split(",")
        req_id=request[0].split(":")[1]
        print("Request id",req_id)
        veh_id=request[1]
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=request[4]
        tile_name=request[5]+','+request[6]
        req_timestamp=request[7]
        
        print("tile_name inside tobroadcast",tile_name)
        if self.broadcast_channel[self.current_slot_time]==tile_name:
            #do nothing
            return
        else:
            self.delays[0]=req_id
            self.delays[1]=veh_id
            self.delays[2]=tile_name
            validity=self.get_validity_of_tile(tile_name)
            slot_when_tile_published_next=self.get_slot_when_tile_published_next(tile_name)
            wait_time=self.calculate_wait_time(slot_when_tile_published_next)
            time_to_reach_tile=self.calculate_time_to_reach_requested_tile(request)
            
            if wait_time < validity and wait_time < time_to_reach_tile:
                #increase priority
                #do nothing, vehicle can wait
                total_delay=self.calculate_total_delay_without_pr(request)

                print("total delay without processing delay",total_delay)
            else:
                #TO DO:search for a slot before the validity expires
                #weighted job scheduling greedy algo
                print("tile replaced this tile %s by this tile%s in slot %s",self.broadcast_channel[self.current_slot_time],tile_name, self.current_slot_time)
                self.add_tile_to_current_slot(tile_name)#urgent scheduling

                print("Total delay",self.calculate_total_delay_with_pr(request))

            add_row_to_csv(delays_logs_csv,self.delays)
        print()

    async def _handle_request(self, request):
        # Process the request here
        print("Request Received from vehicle:",request)
        request=request.decode()
        if self.global_min_ts==-1:
            self.global_min_ts=int(float(request.split(",")[7]))
        self.current_slot_time=((int(float(request.split(",")[7]))-self.global_min_ts)%200)+1
        print(self.current_slot_time)
        self.tobroadcast(request)
        response = b""
        return response

    async def serve(self):
        while True:
            message = await self._socket.recv()
            #print(message)
            response = await self._handle_request(message)
            await self._socket.send(response)

    async def run(self):
        await self.serve()


def main(id,sip,sport,algo,pattern):
    # rsu = RSU(1,'127.0.0.1',5555,'flat','block')
    # Create a new CSV file
    delay_logs_csv = 'delay_logs.csv'
    headers = ['Req_ID', 'Veh_ID', 'Tile_name','Tx1','P1','Pr1','Tx2','P2','Total delay','Distance']
    create_csv_file(delay_logs_csv, headers)
    rsu = RSU(id,sip,sport,algo,pattern)

    asyncio.run(rsu.run())

#Uncomment when RSU to be tested standalone
# if __name__ == "__main__":
#     rsu = RSU(1,'127.0.0.1',5555,'flat','block')
#     asyncio.run(rsu.run())



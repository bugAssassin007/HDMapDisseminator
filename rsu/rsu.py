
import zmq.asyncio
import asyncio
import threading
import time
from threading import *
import time
from tabulate import tabulate
import csv
import math
import sys
from collections import OrderedDict


delay_logs_priority="delay_logs_priority.csv"
delay_logs_basic="delay_logs_basic.csv"
delay_logs_greedy="delay_logs_greedy.csv"
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
        self.jobs={}
        self.global_min_ts=-1
        self.broadcast_channel={}
        self.tile_to_slot = {}
        self.bandwidth=10 #Given in MHz
        self.mcs=14
        num_elements = 10
        self.time_to_reach_tile=0
        self.deadline=0
        self.priority=0#can be defined as the reciprocal of deadline
        self.profits=0#
        self.frequency=1
        #self.request=""
        self.req_id=""
        self.delays=[None] * num_elements #need to initialise array before assigning values
        self.rsu_pos=[36.906882,-1.185770]
        #self.tile_props={"osm":[1,5,3],"pcd":[2,0.3,1],"pcd_mid":[2,2,2]}
        self.tile_props={"osm":[1,2,10],"pcd":[2,1,10],"pcd_mid":[2,2,2]}
        #tile_request_props={"tile_name":[frequency]}
        self.tile_req_props={}
        self.tile_schedule={}
        self.jobs=[[]]
        self.global_jobs={}
        self.hits_with_basic=[]
        self.misses_with_basic=[]
        self.hits_with_greedy=[]
        self.misses_with_greedy=[]
        self.hits_with_priority=[]
        self.misses_with_priority=[]
        # List to store replaced tile pairs
        self.replaced_tiles = []  
        # List to store tiles that cannot be scheduled due to unavailability
        self.cannot_be_scheduled = []
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
                self.tile_req_props[tile_name]=[0]

            # Create empty lists to store the data
            column1 = []
            column2 = []
        
        #for tile_name in self.broadcast_channel.values():
        #     self.tile_req_props[tile_name]=[0]

        for key,val in self.tile_req_props:
            print(key,val)
                    
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
    
    def calculate_processing_delay_at_RSU_for_greedy(self):
        #would it be different from the above function??
        #Time to acquire channel, assumed to be 0
        #Time to schedule a requested tile using algo. TO DO: Run mergesort with 200 elements.
        #Tx= packet size/PHY data rate
        #MIMO=8
        packet_size=float(12*(2**10)*8)  #12KB assumed per 1ms.
        #transmit_time=packet_size/100
        #per request it will be neglglible
        #process_delay=0.0008 #around 0.8 milliseconds for mergesort on 200 elements.
        process_delay=0.0016#for accessing channel and scheduling immediately.
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


    def calculate_total_delay_with_pr_for_greedy(self,request):
        a=self.calculate_transmit_delay_at_vehicle(request)
        self.delays[3]=a
        b=self.calculate_propagation_delay_from_vehicle_to_rsu(request)
        self.delays[4]=b
        c=self.calculate_processing_delay_at_RSU_for_greedy()
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

        for tile_name in self.broadcast_channel.values():
            self.tile_req_props[tile_name]=[0]

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

        # print("slot when tile published",min(tile_to_slot[tile_name]))
        # return min(tile_to_slot[tile_name])
        if tile_name in tile_to_slot:
            print("Slot when tile published:", min(tile_to_slot[tile_name]))
            return min(tile_to_slot[tile_name])
        else:
            #or should I return 0?
            return sys.maxsize
    
    def calculate_wait_time(self,slot_when_tile_published_next):
        current_time = time.time()
        currrent_slot = int(current_time - self.global_min_ts)
        wait_time = slot_when_tile_published_next - currrent_slot
        print("Wait time",wait_time)
        return wait_time

    def calculate_time_to_reach_requested_tile(self,request):
        #distance between RSU and vehicle/speed of vehicle
        #request=request.decode()
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=float(request[4]) if float(request[4])!=0.0 else 0.1
        #TO DO:Change the vehicle lat and long to, converted tile lat and long.
        self.time_to_reach_tile=(calculate_distance(self.rsu_pos[0],self.rsu_pos[1],veh_lat,veh_long))/veh_speed
        print("time to reach tile", self.time_to_reach_tile)

        return self.time_to_reach_tile

    def add_tile_to_current_slot(self,tile_name):
        tile_to_slot = reverse_mapping(self.broadcast_channel)
        self.broadcast_channel[self.current_slot_time],self.broadcast_channel[tile_to_slot[tile_name][0]]=self.broadcast_channel[tile_to_slot[tile_name][0]],self.broadcast_channel[self.current_slot_time]
    
    # def add_tile_to_slot_based_on_priority(self, tile_name, slot):
    #     tile_to_slot = reverse_mapping(self.broadcast_channel)
    #     self.broadcast_channel[slot],self.broadcast_channel[tile_to_slot[tile_name][0]]=self.broadcast_channel[tile_to_slot[tile_name][0]],self.broadcast_channel[slot]



    def add_tile_to_jobs_list_based_on_priority(self,request):
        #jobs=[['tile_name',deadline, priority,isScheduled?]]
        #TO DO: pcd starvation occurs, new algorithm to handle this tradeoff.
        # or if we dont want starvation to occur, how is the performance.
        #request=request.split(",")
        self.req_id=request[0].split(":")[1]
        print("Request id",self.req_id)
        veh_id=request[1]
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=request[4]
        tile_name=request[5]+','+request[6]
        req_timestamp=request[7]
        deadline=self.calculate_time_to_reach_requested_tile(request)
        priority=self.tile_props[tile_name.split('_')[3]]

        # Create a new job entry
        job_entry = [priority, deadline, 0, 0]  # [priority, deadline, isscheduled, isprocessed]
        # Add the job to the global list of jobs
        self.global_jobs[tile_name] = job_entry

        # Update the tile_req_props dictionary
        if tile_name not in self.tile_req_props:
            self.tile_req_props[tile_name] = [0]

        # Sort the jobs in descending order based on priority and deadline
        sorted_jobs = sorted(self.global_jobs.items(), key=lambda x: (x[1][0], x[1][1]), reverse=True)

        # Update the global list with the sorted jobs
        self.global_jobs.clear()
        self.global_jobs.update(sorted_jobs)

        #return self.jobs

    


    
    def schedule_tile_at_slot(self):
        #get current slot
        #need a different function to check if a slot if free to tackle when the broadcast channel is initialised 
        #with segment instead of the grid
        #if the tile_type==osm:
            #if(is_free_slot_found_before_deadline(deadline) || )
        # Iterate through the global_jobs dictionary
        for tile_name, job_entry in self.global_jobs.items():
            priority = job_entry[0]
            deadline = job_entry[1]
            isscheduled = job_entry[2]
            isprocessed = job_entry[3]
            # Check if the tile has not been scheduled and is not yet processed
            if isscheduled == 0 and isprocessed == 0:
                tile_type = tile_name.split('_')[-1]  # Extract tile type from tile_name
                if tile_type == "osm":
                # Browse all slots in the broadcast_channel before the deadline
                # to find an empty slot or a slot with a pcd tile
                    for slot_name, slot_tile in self.broadcast_channel.items():
                        ##TO DO: Change the condition after or, using reverse_broadcast_channel to find slot with pcd tile.
                        if (slot_tile == "" or slot_tile.split('_')[-1] == "pcd") and slot_name <= deadline:
                            # Replace the tile in the slot with the current tile
                            self.replaced_tiles.append([tile_name, slot_tile])
                            self.broadcast_channel[slot_name] = tile_name
                            job_entry[2] = 1  # Set isscheduled flag to 1
                            job_entry[3] = 1  # Set isprocessed flag to 1

                            request_tile= f"{self.req_id}:{tile_name}"
                            if request_tile not in self.hits_with_priority:
                                self.hits_with_priority.append(request_tile) 


                            # #Not the right place to update frequency of the requested tile. TO DO
                            # # Update the tile_req_props dictionary
                            # if slot_tile != "":
                            #     self.tile_req_props[slot_tile][0] -= 1


                            
                        else:
                            # Find a slot before the deadline of type osm with lower frequency
                            current_frequency = self.tile_req_props[tile_name][0]
                            for slot_name, slot_tile in self.broadcast_channel.items():
                                if slot_tile.split('_')[-1]=="osm" and self.tile_req_props[slot_tile][0] < current_frequency and slot_name <= deadline:
                                    # Replace the tile in the slot with the current tile
                                    self.replaced_tiles.append([tile_name, slot_tile])
                                    self.broadcast_channel[slot_name] = tile_name
                                    #self.hits_with_priority.append(tile_name)
                                    job_entry[2] = 1  # Set isscheduled flag to 1
                                    job_entry[3] = 1  # Set isprocessed flag to 1

                                    request_tile= f"{self.req_id}:{tile_name}"
                                    if request_tile not in self.hits_with_priority:
                                        self.hits_with_priority.append(request_tile) 

                                    #break
                                else:
                                    self.cannot_be_scheduled.append(tile_name)
                                    # Set isprocessed flag to 1
                                    job_entry[3] = 1 
                                    #self.misses_with_priority.append(tile_name)
                                    request_tile= f"{self.req_id}:{tile_name}"
                                    if request_tile not in self.misses_with_priority:
                                        self.misses_with_priority.append(request_tile) 
                                

                                    




                            #TO DO: Do you want to add a cannot be scheduled case? if yes use the below code
                            #cannot_be_scheduled.append(tile_name)
                            #job_entry[3] = 1  # Set isprocessed flag to 1
                #if tile is pcd, can add more types by changing the else to elif tile_type=="pcd"
                else:
                    # Find a slot before the deadline with a pcd tile and lower frequency
                    current_frequency = self.tile_req_props[tile_name][0]
                    for slot_name, slot_tile in self.broadcast_channel.items():
                        if slot_tile != "" and self.tile_req_props[slot_tile][0] < current_frequency and slot_name < deadline: 
                            # Replace the tile in the slot with the current tile
                            self.replaced_tiles.append([tile_name, slot_tile])
                            self.broadcast_channel[slot_name] = tile_name
                            #self.hits_with_priority.append(tile_name)
                            job_entry[2] = 1  # Set isscheduled flag to 1
                            job_entry[3] = 1  # Set isprocessed flag to 1
                            request_tile= f"{self.req_id}:{tile_name}"
                            if request_tile not in self.hits_with_priority:
                                self.hits_with_priority.append(request_tile) 
                            #break
                        else:
                            self.cannot_be_scheduled.append(tile_name)
                            # self.misses_with_priority.append(tile_name)
                            job_entry[3] = 1  # Set isprocessed flag to 1
                            request_tile= f"{self.req_id}:{tile_name}"
                            if request_tile not in self.misses_with_priority:
                                self.misses_with_priority.append(request_tile) 
                        
        #return

    # def schedule_tile_at_slot(self):
    #     for tile_name, job_entry in self.global_jobs.items():
    #         priority = job_entry[0]
    #         deadline = job_entry[1]
    #         isscheduled = job_entry[2]
    #         isprocessed = job_entry[3]

    #         # Check if the tile has not been scheduled and is not yet processed
    #         if isscheduled == 0 and isprocessed == 0:
    #             tile_type = tile_name.split('_')[-1]  # Extract tile type from tile_name

    #             if tile_type == "osm":
    #                 self.schedule_osm_tile(tile_name, deadline, job_entry)
    #             else:  # tile_type == "pcd"
    #                 self.schedule_pcd_tile(tile_name, deadline, job_entry)

    # def schedule_osm_tile(self, tile_name, deadline, job_entry):
    #     for slot_name, slot_tile in self.broadcast_channel.items():
    #         if (slot_tile == "" or slot_tile.split('_')[-1] == "pcd") and slot_name <= deadline:
    #             # Replace the tile in the slot with the current tile
    #             self.replaced_tiles.append([tile_name, slot_tile])
    #             self.broadcast_channel[slot_name] = tile_name
    #             job_entry[2] = 1  # Set isscheduled flag to 1
    #             job_entry[3] = 1  # Set isprocessed flag to 1

    #             request_tile = f"{self.req_id}:{tile_name}"
    #             if request_tile not in self.hits_with_priority:
    #                 self.hits_with_priority.append(request_tile)
    #             break
    #         else:
    #             current_frequency = self.tile_req_props[tile_name][0]
    #             for slot_name, slot_tile in self.broadcast_channel.items():
    #                 if slot_tile.split('_')[-1] == "osm" and self.tile_req_props[slot_tile][0] < current_frequency and slot_name <= deadline:
    #                     # Replace the tile in the slot with the current tile
    #                     self.replaced_tiles.append([tile_name, slot_tile])
    #                     self.broadcast_channel[slot_name] = tile_name
    #                     job_entry[2] = 1  # Set isscheduled flag to 1
    #                     job_entry[3] = 1  # Set isprocessed flag to 1

    #                     request_tile = f"{self.req_id}:{tile_name}"
    #                     if request_tile not in self.hits_with_priority:
    #                         self.hits_with_priority.append(request_tile)
    #                     break
    #                 else:
    #                     self.cannot_be_scheduled.append(tile_name)
    #                     job_entry[3] = 1  # Set isprocessed flag to 1
    #                     request_tile = f"{self.req_id}:{tile_name}"
    #                     if request_tile not in self.misses_with_priority:
    #                         self.misses_with_priority.append(request_tile)

    # def schedule_pcd_tile(self, tile_name, deadline, job_entry):
    #     current_frequency = self.tile_req_props[tile_name][0]
    #     for slot_name, slot_tile in self.broadcast_channel.items():
    #         if  slot_tile != "" or (slot_tile.split('_')[-1] == "pcd" and self.tile_req_props[slot_tile][0] < current_frequency) and slot_name < deadline:
    #             # Replace the tile in the slot with the current tile
    #             self.replaced_tiles.append([tile_name, slot_tile])
    #             self.broadcast_channel[slot_name] = tile_name
    #             job_entry[2] = 1  # Set isscheduled flag to 1
    #             job_entry[3] = 1  # Set isprocessed flag to 1

    #             request_tile = f"{self.req_id}:{tile_name}"
    #             if request_tile not in self.hits_with_priority:
    #                 self.hits_with_priority.append(request_tile)
    #             break
    #         else:
    #             self.cannot_be_scheduled.append(tile_name)
    #             job_entry[3] = 1  # Set isprocessed flag to 1
    #             request_tile = f"{self.req_id}:{tile_name}"
    #             if request_tile not in self.misses_with_priority:
    #                 self.misses_with_priority.append(request_tile)




    def update_tile_frequency(self,tile_name):
        if tile_name in self.tile_req_props:
            self.tile_req_props[tile_name][0] += 1  # Increment frequency if tile exists
        else:
            self.tile_req_props[tile_name] = [1] #Add tile if not exitsts

    def tobroadcast_greedy(self,request):
        #schedule every tile current slot.
     
        request=request.split(",")
        req_id=request[0].split(":")[1]
        print("Request id",req_id)
        veh_id=request[1]
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=request[4]
        tile_name=request[5]+','+request[6]
        req_timestamp=request[7]
        if self.broadcast_channel[self.current_slot_time]==tile_name:
            #do nothing
            #can count as a hit
            self.hits_with_greedy.append(tile_name)
            return
        else:
            self.delays[0]=req_id 
            self.delays[1]=veh_id
            self.delays[2]=tile_name
            validity=self.get_validity_of_tile(tile_name)
            slot_when_tile_published_next=self.get_slot_when_tile_published_next(tile_name)
            wait_time=self.calculate_wait_time(slot_when_tile_published_next)
            self.time_to_reach_tile=self.calculate_time_to_reach_requested_tile(request)
            self.deadline=self.current_slot_time+(self.time_to_reach_tile-self.global_min_ts)
            self.priority=self.tile_props[self.delays[2].split("_")[-1]][2]
            self.profit=(1/self.deadline)+self.priority
            if wait_time < validity and wait_time < self.time_to_reach_tile:
                #increase frequency
                #self.tile_request_props[tile_name]+=1
                self.update_tile_frequency(tile_name)
                #do nothing, vehicle can wait
                total_delay=self.calculate_total_delay_with_pr(request)+wait_time
                self.hits_with_greedy.append(tile_name)

                print("total delay without processing delay",total_delay)
            else:
                self.add_tile_to_current_slot(tile_name)
                total_delay=self.calculate_total_delay_with_pr_for_greedy(request)
                #self.misses_with_greedy.append(tile_name)
                self.hits_with_greedy.append(tile_name)


        add_row_to_csv(delay_logs_greedy,self.delays)    
        print("No. of misses with greedy are ", len(self.misses_with_greedy))
        print("No. of hits with greedy are ", len(self.hits_with_greedy))
        print(self.global_jobs)
                                                                 

        

    def tobroadcast_basic(self,request):
        reversed_broadcast_channel = OrderedDict((len(self.broadcast_channel) - i, tile) for i, tile in self.broadcast_channel.items())
        self.broadcast_channel=OrderedDict((len(reversed_broadcast_channel) - i, tile) for i, tile in reversed_broadcast_channel.items())
        
        #normal broadcast, every tile is broadcasted once only.
        request=request.split(",")
        req_id=request[0].split(":")[1]
        print("Request id",req_id)
        veh_id=request[1]
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=request[4]
        tile_name=request[5]+','+request[6]
        req_timestamp=request[7]
        if self.broadcast_channel[self.current_slot_time]==tile_name:

            #do nothing
            total_delay=self.calculate_total_delay_without_pr(request)
            self.hits_with_basic.append(tile_name)


            #can count as a hit
            return
        else:
            self.delays[0]=req_id 
            self.delays[1]=veh_id
            self.delays[2]=tile_name
            validity=self.get_validity_of_tile(tile_name)
            slot_when_tile_published_next=self.get_slot_when_tile_published_next(tile_name)
            wait_time=self.calculate_wait_time(slot_when_tile_published_next)
            self.time_to_reach_tile=self.calculate_time_to_reach_requested_tile(request)
            self.deadline=self.current_slot_time+(self.time_to_reach_tile-self.global_min_ts)
            self.priority=self.tile_props[self.delays[2].split("_")[-1]][2]
            self.profit=(1/self.deadline)+self.priority
            if wait_time < validity and wait_time < self.time_to_reach_tile:
                #increase frequency
                #self.tile_request_props[tile_name]+=1
                #self.update_tile_frequency(tile_name)
                #do nothing, vehicle can wait
                total_delay=self.calculate_total_delay_without_pr(request) + wait_time
                self.hits_with_basic.append(tile_name)

                print("total delay without processing delay",total_delay)
            else:
                total_delay=self.calculate_total_delay_without_pr(request)+ self.time_to_reach_tile
                self.misses_with_basic.append(tile_name)

        add_row_to_csv(delay_logs_basic,self.delays)    
        print("No. of misses with basic are ", len(self.misses_with_basic))
        print("No. of hits with basic are ", len(self.hits_with_basic))
        
    def find_duplicates(self,input_list):
        seen = set()
        duplicates = set()

        for item in input_list:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)

        return list(duplicates)
    
    def tobroadcast_priority(self,request):
        #to decide whether to broadcast tile or not
        #and then schedule broadcast only when urgent.
        #request=request.decode()
        request=request.split(",")
        self.req_id=request[0].split(":")[1]
        print("Request id",self.req_id)
        veh_id=request[1]
        veh_lat=request[2]
        veh_long=request[3]
        veh_speed=request[4]
        tile_name=request[5]+','+request[6]
        req_timestamp=request[7]
        request_tile= f"{self.req_id}:{tile_name}"
                                    
        print("tile_name inside tobroadcast",tile_name)
        if self.broadcast_channel[self.current_slot_time]==tile_name:
            #do nothing
            if request_tile not in self.hits_with_priority:
                self.hits_with_priority.append(request_tile)
            
        else:
            self.delays[0]=self.req_id 
            self.delays[1]=veh_id
            self.delays[2]=tile_name
            validity=self.get_validity_of_tile(tile_name)
            slot_when_tile_published_next=self.get_slot_when_tile_published_next(tile_name)
            wait_time=self.calculate_wait_time(slot_when_tile_published_next)
            self.time_to_reach_tile=self.calculate_time_to_reach_requested_tile(request)
            self.deadline=self.current_slot_time+(self.time_to_reach_tile-self.global_min_ts)
            self.priority=self.tile_props[self.delays[2].split("_")[-1]][2]
            self.profit=(1/self.deadline)+self.priority
            self.update_tile_frequency(tile_name)
            if wait_time < self.time_to_reach_tile:
                #TO DO: Understand why a check of wait_time with validity is needed, removing this check for now.
                #increase frequency
                #self.tile_request_props[tile_name]+=1
                
                if request_tile not in self.hits_with_priority:
                    self.hits_with_priority.append(request_tile)
                #do nothing, vehicle can wait
                total_delay=self.calculate_total_delay_without_pr(request)+ wait_time
                print("total delay without processing delay",total_delay)
                #return
            else:
                #TO DO:search for a slot before the validity expires
                #weighted job scheduling greedy algo
                #slot=schedule the tile
                #if the tile is scheduled immediately, loss of tile and probably urgent tiles.
                #disadvantage: pcd overrides osm data.
                #no. of osm overrides.
                #vehicle move forward.. or not--animation style.
                print("tile replaced this tile %s by this tile%s in slot %s",self.broadcast_channel[self.current_slot_time],tile_name, self.current_slot_time)
                #self.add_tile_to_current_slot(tile_name)#urgent scheduling
                ##self.add_tile_to_slot_based_on_priority(tile_name, self.get_slot_based_on_priority(request)[0][])
                self.add_tile_to_jobs_list_based_on_priority(request)
                self.schedule_tile_at_slot()
                total_delay=self.calculate_total_delay_with_pr(request)
                print("Total delay",total_delay)

        add_row_to_csv(delay_logs_priority,self.delays)
        print("No. of misses with priority are ", len(self.misses_with_priority))
        count_osm = sum(1 for item in self.misses_with_priority if item.endswith("osm"))
        count_pcd = sum(1 for item in self.misses_with_priority if item.endswith("pcd"))
        print("No. of pcd misses and osm misses respectively are", count_pcd, " ", count_osm)
        print("No. of hits with priority are ", len(self.hits_with_priority))
        print(self.misses_with_priority)
        #print(self.hits_with_priority)

        print(self.find_duplicates(self.misses_with_priority))
        print(self.find_duplicates(self.hits_with_priority))


        common_elements = set(self.hits_with_priority) & set(self.misses_with_priority)
        print("common elements",common_elements)


        # File path where you want to write the list
        file_path = 'hits_and_misses.txt'

        # Open the file in append mode ('a' mode) to add the list to the file
        with open(file_path, 'a') as file:
            # Convert the list elements to strings and join them with a separator (e.g., a comma)
            list_str = ','.join(map(str, self.hits_with_priority))
            
            # Write the list string to the file
            file.write(list_str + '\n')

        print()

    async def _handle_request(self, request):
        # Process the request here
        print("Request Received from vehicle:",request)
        request=request.decode()
        if self.global_min_ts==-1:
            self.global_min_ts=int(float(request.split(",")[7]))
        self.current_slot_time=((int(float(request.split(",")[7]))-self.global_min_ts)%200)+1
        
        print(self.current_slot_time)
        #self.tobroadcast_basic(request)
        #self.tobroadcast_greedy(request)
        self.tobroadcast_priority(request)
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
    #delay_logs_csv = 'delay_logs.csv'
    #delay_logs_basic = 'delay_logs_basic.csv'
    delay_logs_priority = 'delay_logs_priority.csv'
    #delay_logs_greedy = 'delay_logs_greedy.csv'
    headers = ['Req_ID', 'Veh_ID', 'Tile_name','Tx1','P1','Pr1','Tx2','P2','Total delay','Distance']
    #create_csv_file(delay_logs_basic, headers)
    #create_csv_file(delay_logs_greedy, headers)
    create_csv_file(delay_logs_priority, headers)
    rsu = RSU(id,sip,sport,algo,pattern)

    asyncio.run(rsu.run())

#Uncomment when RSU to be tested standalone
# if __name__ == "__main__":
#     rsu = RSU(1,'127.0.0.1',5555,'flat','block')
#     asyncio.run(rsu.run())



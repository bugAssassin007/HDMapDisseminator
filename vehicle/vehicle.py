import zmq.asyncio
import asyncio
import csv
import numpy as np
import pandas as pd
import time
from utils.common_args import common_args, handler_keyboard_interrupt
import signal

#tile_props={"format/tile_type":["size(in units of cache)","validity(in seconds)"]}
tile_props={"osm":[1,5],"pcd":[2,1],"pcd_mid":[2,2]}


class Vehicle:

    def __init__(self, id, pip, pport, cache_size, input_file):
        self.id = id
        self.pip = pip
        self.pport = pport
        self.input_file = input_file
        self.veh_cache=[]
        self.max_length=cache_size
        self.payload=""

    async def send_request(self, request):

        #Create socket and send request to RSU
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://%s:%s'%(self.pip,self.pport))
        print("request sent is",request)
        await socket.send(request)

        #request is sent every second
        time.sleep(1)#TO DO:send the requests based on the timestamp
        response = await socket.recv()

        # close the socket after each request
        socket.close()  
        return response
    
    async def process_response(self, response):
        pass
        #print()
    
    async def client(self,message):
            
            # Send a request
            request = f"{message}".encode()
            response = await self.send_request(request)

            # Process the response
            await self.process_response(response)

    def isTileValid(self,tile):
        #Fetch the tiles list for a vehicle ID
        #print("self.id",self.id)
        tiles=self.veh_cache
        print(f"tiles for vehicle {self.id}:", tiles)
        #Iterate through all tiles in the cache for a vehicle ID
        #t[0] since veh_cache={vehicle_id:[tile_name, tiled_time],[],..maxlength}
        for t in tiles:
            if t[0] == tile:
                tiledTime=float(t[1])

        #Get the last part of the tile name which indicates tile type
        #Eg: '(10, 10)_9_8_osm' where osm is the type
        type = tile.split('_')[-1]

        #Calculate current time
        currentTime=time.time()
        
        #remainingTime = currentTime-tiledTime
        timePassed = currentTime-tiledTime
        print("Time passed=",timePassed)
        print("Tiled time", tiledTime)
        print("for tile",tile)
        print("validity=", tile_props[type][1])
                
        #If tile validity is greater than the remaining time, return True, else return False
        #if(tile_props[type][1] - timePassed > 0):
        #print("if timePassed>=tile_props[type][1]?")
        if(timePassed<tile_props[type][1]):
            #print("Tile valid returned!")
            return True
        else:
            #print("Tile invalid returned!")
            return False
        
    def remove_tile_from_cache(self, tile_name):
        # Check if the vehicle_id exists in the cache
        # if vehicle_id in self.veh_cache:
        #     # Get the list of tiles for the given vehicle_id


        # Iterate through the list of tiles for the vehicle_id
        for tile in self.veh_cache:
            if tile[0] == tile_name:
                # Remove the tile from the list
                self.veh_cache.remove(tile)
                print(f"Tile '{tile_name}' removed from cache for vehicle_id '{self.id}'.")
                return
        #print(f"Tile '{tile_name}' not found in cache for vehicle_id '{vehicle_id}'.")
        # else:
        #     print(f"Vehicle ID '{vehicle_id}' not found in cache.")
        
    async def update_cache(self, tile_name, time_step):
        print()
        print("------------------------------------------------------------------------------------------------------------")
        print("Update cache called with the row and tile",time_step,tile_name)
        print("This is cache ....", self.veh_cache)

        #Get the current timestamp
        curr_timestamp = time.time()
        # isVehiclePresent = False
        isTilePresent= False
        # if vehicle_id in self.veh_cache:
            # isVehiclePresent=True
        for tile in self.veh_cache:
            #print("tile present in cachetile_name)
            if tile[0] == tile_name:
                isTilePresent=True
            
        
        # check if vehicle_id exists in cache
        
        #if vehicle_id in self.veh_cache :

            #Iterate over all tiles in the cache for that vehicle ID, to check if the tile exists
            #for tile in self.veh_cache[vehicle_id]:

                # check if tile already exists in cache
                #if tile[0] == tile_name:
        
        # if isVehiclePresent: 
        if isTilePresent:
            print("Tile in if exists",tile_name)
            print("Is tile valid?",self.isTileValid(tile_name))
            if self.isTileValid(tile_name):
                
                print("Tile exists and is valid",tile_name)
                # do nothing if tile already exists in cache and is valid
                #since a request is not sent to the RSU in the case where tile is present and valid, the hits are not counted in this case
                #hence count them here and then add it to the hits in the RSU
                hits_count=0
                hits_count=hits_count+1
                print("Vehicle additional hits", hits_count)
                #return 
            
            else:

                #print("Tile in if exists but invalid",tile_name)
                #If tile exists in cache, but is invalid, request RSU for the tile
                
                #Create the payload to be sent to the RSU, by appending the tile_name and the time at which the request is being sent
                self.payload=self.payload+','+tile_name+','+str(time.time())
                #print("")
                await self.client(self.payload)

                #Requesting RSU for tile due to invalidity!
                current_length=0
                for tile in self.veh_cache:
                    #print("tile present in cachetile_name)
                    #if tile[0] == tile_name:
                    type = tile[0].split('_')[-1]
                    current_length=current_length+(1*tile_props[type][0])
                type = tile_name.split('_')[-1]
                print("Tile props",tile_props[type][0])
                print("max length", self.max_length)
                print("length of the current cache",current_length)
                if current_length+ tile_props[type][0]> self.max_length:
                    print("Tile exists but invalid and no space in cache",tile_name)

                    # remove the least recently used tile, removing the first stored tile.
                    self.veh_cache.pop(0)
                    print("popped 1....")

                    # add the new tile to cache
                    self.veh_cache.append([tile_name, curr_timestamp])

                    #TO DO: Check if sorting is required to fetch the least recently used.
                else:

                    #create a new entry for vehicle_id in cache
                    #send a request to the RSU
                    print("Tile in if exists but invalid and has space in cache",tile_name)
                    self.remove_tile_from_cache(tile_name)
                    #add the new tile to cache

                    self.veh_cache.append([tile_name, curr_timestamp])
        else:
            
            #Create the payload to be sent to the RSU, by appending the tile_name and the time at which the request is being sent
            #print("Tile in if not in cache",tile_name)
            self.payload=self.payload+','+tile_name+','+str(time.time())
            print("Inside tile not exists in cache!")
            await self.client(self.payload)

            
            #print("Requesting RSU for tile due to absence of tile in cache!")
            
            
            current_length=0
            for tile in self.veh_cache:
                #print("tile present in cachetile_name)
                #if tile[0] == tile_name:
                type = tile[0].split('_')[-1]
                current_length=current_length+(1*tile_props[type][0])
            type = tile_name.split('_')[-1]
            print("Tile props",tile_props[type][0])
            print("max length", self.max_length)
            print("length of the current cache",current_length)
            # add the new tile to cache
            if current_length + tile_props[type][0]>self.max_length: ##$$checking correct? it was double equal to earlier
                # remove the least recently used tile
                print("The length of the cache is",len(self.veh_cache))
                print("Tile in not exists in cache and no space in cache",tile_name)
                self.veh_cache.pop(0)
                print("popped 2...")

                # add the new tile to cache
                self.veh_cache.append([tile_name, curr_timestamp])
            else:
                # create a new entry for vehicle_id in cache
                #send a request to the RSU
                print("Tile does not exist and has space in cache",tile_name)
                #TO DO: WHy are u removing when there is space in the cache...I Think because its invalid
                #self.remove_tile_from_cache(vehicle_id, tile[0])
                # add the new tile to cache
                self.veh_cache.append([tile_name, curr_timestamp])
                print("Added to cache",self.veh_cache)
        # if not isVehiclePresent:
        #     #If a new vehicle is added, then request for that tile
        #     #print("Tile in if new vehicle addded",tile_name)
        #     self.payload=self.payload+','+tile_name+','+str(time.time())
        #     print("Inside tile not exists in cache!")
        #     await self.client(self.payload)

        #     #TO DO: Check if there is a drastic change in calculation of the current timestamp upwards and here.
        #     self.veh_cache[vehicle_id] = [[tile_name, curr_timestamp]]
        #     print("Added to cache",self.veh_cache)
        

    #Function takes in latitudes, longitudes and matrix shape and gives i, j for a matrix where a particular point lies
    def scale_to_indices(self,latitudes, longitudes, matrix_shape):
        min_lat = np.min(latitudes)
        max_lat = np.max(latitudes)
        min_long = np.min(longitudes)
        max_long = np.max(longitudes)

        # Compute scaling factors for latitudes and longitudes
        lat_scale = matrix_shape[0] / (max_lat - min_lat)
        long_scale = matrix_shape[1] / (max_long - min_long)

        # Create a list to store the scaled indices
        indices = []

        # Scale each latitude and longitude value and add it to the indices list
        for i in range(len(latitudes)):
            x = min(max(int((latitudes[i] - min_lat) * lat_scale), 0), matrix_shape[0] - 1)
            y = min(max(int((longitudes[i] - min_long) * long_scale), 0), matrix_shape[1] - 1)
            indices.append((x, y))

        return indices

    #Using the indices from the above function to create tiles and add it to the csv file
    def add_indices_to_csv(self,file_path, matrix_shape):
        # Load the CSV file into a Pandas DataFrame
        df = pd.read_csv(file_path)

        # Scale the Lat and Long values to matrix indices
        indices = self.scale_to_indices(df['Lat'], df['Long'], matrix_shape)

        # Add the indices as a new column to the DataFrame
        df['matrix_indices'] = indices

        # Create a new column with tile name values
        tile_names = []
        for index in indices:
            osm_tile_name = f"{matrix_shape}_{index[0]}_{index[1]}_osm"
            pcd_tile_name = f"{matrix_shape}_{index[0]}_{index[1]}_pcd"
            tile_names.append([osm_tile_name, pcd_tile_name])

        df['tile_name'] = tile_names

        # Write the updated DataFrame back to the CSV file
        df.to_csv(file_path, index=False)

        return df
    
def main(args):
    vehicle = Vehicle(args.id, args.pip, args.pport, args.cache_size, args.input_file)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{args.ciip}:{args.ciport}")
    socket.setsockopt(zmq.SUBSCRIBE, b'')

    finish_socket = context.socket(zmq.REQ)
    finish_socket.connect(f'tcp://{args.csip}:{args.csport}')

    df = pd.read_csv(args.input_file)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    while True:
        #  Wait for next request from client
        print('Waiting for message...')
        try:
            message = socket.recv()
            if message == b'END':
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            print('Exiting')
            socket.close()
            finish_socket.close()
            context.destroy()
            break
        # finally:
        #     print('Closing sockets')
        #     socket.close()
        #     context.destroy()
        print(f"Perform iteration...")
        message = int(message)
        #  Do some 'work'
        #TODO some message transform
        row = df[(df['Time'] == message) & (df['Vehicle ID'] == vehicle.id)]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        tile_lst = eval(row.loc['tile_name'])
        for i in range(2):
            #print("This is list",lst[i])
            #print("Request number is=")
            row_number = int(row.loc['row_number'])
            if i==0:

                reqnbr= str(row_number + (row_number - 1))
            else:
                reqnbr=str(row_number * 2)
            #For both add the request in the format row:requestnumber,vehicle_id,Lat,Long,Speed
            vehicle.payload = f"row:{reqnbr},{row.loc['Vehicle ID']},{row.loc['Lat']},{row.loc['Long']},{row.loc['Speed']}"
            print(vehicle.payload)
            asyncio.run(vehicle.update_cache(tile_lst[i], reqnbr))
        finish_socket.send(b'finished')
        finish_socket.recv()
        # #  Send reply back to client
        # with open("test.txt", 'r') as f:
        #     for line in f:
        #         socket.send_string(line.rstrip("\n"))

if __name__ == "__main__":
    args = common_args()
    main(args)
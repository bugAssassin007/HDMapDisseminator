import zmq.asyncio
import asyncio
import csv
import numpy as np
import pandas as pd
import time

#tile_props={"format/tile_type":["size(in units of cache)","validity(in seconds)"]}
tile_props={"osm":[1,2],"pcd":[2,2],"pcd_mid":[2,2]}



class Vehicle:

    def __init__(self, id, pip, pport, cache_size, input_file):
        self.id = id
        self.pip = pip
        self.pport = pport
        self.input_file = input_file
        self.veh_cache={}
        self.max_length=cache_size

    async def send_request(self, request):

        #Create socket and send request to RSU
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://%s:%s'%(self.pip,self.pport))
        await socket.send(request)

        #request is sent every second
        #time.sleep(1)#TO DO:send the requests based on the timestamp
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
        tiles=self.veh_cache[self.id]

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
        
        remainingTime =currentTime-tiledTime
                
        #If tile validity is greater than the remaining time, return True, else return False
        if(tile_props[type][1]> remainingTime):
            #print("Tile valid returned!")
            return True
        else:
            #print("Tile invalid returned!")
            return False
        
    async def update_cache(self, vehicle_id, tile_name, max_length, time_step, payload):


        print(self.veh_cache)

        #Get the current timestamp
        curr_timestamp = time.time()

        
        # check if vehicle_id exists in cache
        
        if vehicle_id in self.veh_cache :

            #Iterate over all tiles in the cache for that vehicle ID, to check if the tile exists
            for tile in self.veh_cache[vehicle_id]:

                # check if tile already exists in cache
                if tile[0] == tile_name:

                    #print("Tile in if exists",tile_name)

                    if self.isTileValid(tile_name):
                        
                        #print("Tile in if exists and is valid",tile_name)
                        # do nothing if tile already exists in cache
                        return 
                    
                    else:

                        #print("Tile in if exists but invalid",tile_name)
                        #If tile exists in cache, but is invalid, request RSU for the tile
                        
                        #Create the payload to be sent to the RSU, by appending the tile_name and the time at which the request is being sent
                        payload=payload+','+tile_name+','+str(time.time())

                        await self.client(payload)

                        #Requesting RSU for tile due to invalidity!
                        if len(self.veh_cache[vehicle_id]) >= max_length:
                            #print("Tile in if exists but invalid and no space in cache",tile_name)

                            # remove the least recently used tile
                            self.veh_cache[vehicle_id].pop(0)

                            # add the new tile to cache
                            self.veh_cache[vehicle_id].append([tile_name, curr_timestamp])
                        else:

                            #create a new entry for vehicle_id in cache
                            #send a request to the RSU
                            #print("Tile in if exists but invalid and has space in cache",tile_name)
                            #add the new tile to cache
                            self.veh_cache[vehicle_id].append([tile_name, curr_timestamp])
                else:
                    
                    #Create the payload to be sent to the RSU, by appending the tile_name and the time at which the request is being sent
                    #print("Tile in if not in cache",tile_name)
                    payload=payload+','+tile_name+','+str(time.time())
                    #print("Inside tile not exists in cache!")
                    await self.client(payload)

                    
                    #print("Requesting RSU for tile due to absence of tile in cache!")
                    # add the new tile to cache
                    if len(self.veh_cache[vehicle_id]) == max_length:
                        # remove the least recently used tile
                        #print("Tile in not exists in cache and no space in cache",tile_name)
                        self.veh_cache[vehicle_id].pop(0)

                        # add the new tile to cache
                        self.veh_cache[vehicle_id].append([tile_name, curr_timestamp])
                    else:
                        # create a new entry for vehicle_id in cache
                        #send a request to the RSU
                        #print("Tile in if exists but invalid and has space in cache",tile_name)
                        # add the new tile to cache
                        self.veh_cache[vehicle_id].append([tile_name, curr_timestamp])
        else:
            #If a new vehicle is added, then request for that tile
            #print("Tile in if new vehicle addded",tile_name)
            payload=payload+','+tile_name+','+str(time.time())
            #print("Inside tile not exists in cache!")
            await self.client(payload)
            self.veh_cache[vehicle_id] = [[tile_name, curr_timestamp]]
        

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
    


    async def main(self):
        
        self.add_indices_to_csv('short_datatotest.csv', (10, 10))
        with open('sumo_longtrace.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                payload="row:"+row[9]+','+row[1]+','+row[4]+','+row[5]+','+row[6]
                #print(payload)
                time_step=row[0]
                #vehicle_id = row[1]
                self.id = row[1]
                #print("vehicle id:",self.id)
                tile = row[7]
                lst = eval(tile)
                #print("This is list",lst)
                for i in range(2):
                    #print("This is list",lst[i])

                    await self.update_cache(self.id, lst[i], self.max_length,time_step,payload)

def main(id,pip,pport,cache_size,input_file):
    #vehicle1 = Vehicle(1,'127.0.0.1',5555,'hello')
    vehicle1 = Vehicle(id,pip,pport,cache_size,input_file)
    asyncio.run(vehicle1.main())


#Uncomment this when running vehicle standalone

# if __name__ == "__main__":
#     vehicle1 = Vehicle(1,'127.0.0.1',5555,'hello')
#     asyncio.run(vehicle1.main())

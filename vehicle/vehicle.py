import zmq.asyncio
import asyncio

class Vehicle:
    def __init__(self, id,pip,pport,input_file):
        self.id = id
        self.pip=pip
        self.pport=pport
        self.input_file=input_file

    async def send_request(self, request):
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REQ)
        #socket.connect("tcp://localhost:5555")
        socket.connect('tcp://%s:%s'%(self.pip,self.pport))
        await socket.send(request)
        response = await socket.recv()
        socket.close()  # close the socket after each request
        return response
    
    async def process_response(self, response):
        # Process the response here
        print(f"Vehicle {self.id} received response: {response.decode()}")
        print("from ip and port",self.pip, self.pport)
    async def client(self):
        while True:
            # Send a request
            request = f"Vehicle {self.id} request".encode()
            response = await self.send_request(request)

            # Process the response
            await self.process_response(response)

    async def main(self):
        await self.client()


def main(id,pip,pport,input_file):
    # vehicle1 = Vehicle(1,'127.0.0.1',5555,'hello')
    vehicle1 = Vehicle(id,pip,pport,input_file)
    asyncio.run(vehicle1.main())

if __name__ == "__main__":
    vehicle1 = Vehicle(1,'127.0.0.1',5555,'hello')
    asyncio.run(vehicle1.main())

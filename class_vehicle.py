import zmq.asyncio
import asyncio

class Vehicle:
    def __init__(self, id):
        self.id = id
    
    async def send_request(self, request):
        context = zmq.asyncio.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")
        await socket.send(request)
        response = await socket.recv()
        socket.close()  # close the socket after each request
        return response
    
    async def process_response(self, response):
        # Process the response here
        print(f"Vehicle {self.id} received response: {response.decode()}")

    async def client(self):
        while True:
            # Send a request
            request = f"Vehicle {self.id} request".encode()
            response = await self.send_request(request)

            # Process the response
            await self.process_response(response)

    async def main(self):
        await self.client()

if __name__ == "__main__":
    vehicle1 = Vehicle(1)
    asyncio.run(vehicle1.main())

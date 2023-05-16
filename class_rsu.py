import zmq.asyncio
import asyncio
import threading
import time

class RSU:
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._context = zmq.asyncio.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind("tcp://*:5555")
        
        # Start the daemon thread to print "Hello"
        self._hello_thread = threading.Thread(target=self._print_hello, daemon=True)
        self._hello_thread.start()

    def _print_hello(self):
        while True:
            print("Hello")
            time.sleep(1)

    async def _handle_request(self, request):
        # Process the request here
        response = b"Hello from RSU"
        return response

    async def serve(self):
        while True:
            message = await self._socket.recv()
            print(message)
            response = await self._handle_request(message)
            await self._socket.send(response)

    async def run(self):
        await self.serve()

if __name__ == "__main__":
    rsu = RSU()
    asyncio.run(rsu.run())
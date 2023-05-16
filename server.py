import zmq.asyncio
import asyncio
import threading
import time

def print_hello():
    while True:
        print("Hello")
        time.sleep(1)

async def handle_request(request):
    # Process the request here
    response = b"Hello from server"
    return response

async def server():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        message = await socket.recv()
        print(message)
        response = await handle_request(message)
        await socket.send(response)

async def main():
    # Start the daemon thread to print "Hello"
    t = threading.Thread(target=print_hello, daemon=True)
    t.start()

    # Start the server to handle requests
    await server()

if __name__ == "__main__":
    asyncio.run(main())
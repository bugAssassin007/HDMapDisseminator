import zmq.asyncio
import asyncio
import threading

async def send_request(request):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    await socket.send(request)
    response = await socket.recv()
    return response

async def process_response(response):
    # Process the response here
    print(f"Received response: {response.decode()}")

async def client():
    tasks = []
    while True:
        # Prompt user for request
        request_str = input("Enter a request (or 'q' to quit): ")
        if request_str == 'q':
            break
        
        # Send the request and process the response
        request = request_str.encode()
        send_task = asyncio.create_task(send_request(request))
        process_task = asyncio.create_task(process_response(await send_task))
        tasks.append(process_task)

    # Wait for all responses to complete
    await asyncio.gather(*tasks)

async def main():
    await client()

if __name__ == "__main__":
    asyncio.run(main())

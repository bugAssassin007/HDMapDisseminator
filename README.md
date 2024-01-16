# HDMapDisseminator - High-Definition Map Dissemination Tool

Welcome to HDMapDisseminator, a tool designed for the efficient dissemination of high-definition (HD) map tiles to vehicles. This tool is particularly useful for researchers and developers working on novel algorithms in the field of autonomous driving and vehicle communication networks.

## Running the Vehicle Module

To simulate a vehicle within the network, use the following command:

python3 main.py vehicle --id 1 --pip 127.0.0.1 --pport 5502 --cache_size 2 --input_file "requests.csv"


### Configuration Parameters:
- `--id`: Vehicle ID. Assign different IDs to simulate multiple vehicles simultaneously.
- `--pip`: Parent IP. This should be set to the IP of the Road-Side Unit (RSU).
- `--pport`: Parent Port. Specify the port of the RSU to establish a connection.
- `--cache_size`: Size of the Least Recently Used (LRU) cache at the vehicle, measured in tile size units.
- `--input_file`: The file containing the vehicle's request data.

## Running the RSU Module

To initiate a Road-Side Unit (RSU), use the following command:

python3 main.py rsu --id 1 --sip 127.0.0.1 --sport 5502 --algo flat --pattern alternate


### Configuration Parameters:
- `--id`: RSU ID. Use different IDs for multiple RSU instances.
- `--sip`: Self IP.
- `--sport`: Self Port.
- `--algo`: Algorithm used for map dissemination. Default is 'flat', applicable to all modes (Basic, Adaptive, Optimal).
- `--pattern`: The pattern for broadcasting map layers. Default is 'alternate', which alternates between .osm and .pcd layers.

---

This setup is ideal for testing and implementing new algorithms in the field of HD map dissemination, providing a flexible and configurable environment for both vehicle and RSU simulation.

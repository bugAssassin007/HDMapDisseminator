# HDMapDisseminator
This setup helps in implementing novel algorithms to disseminate HD map tiles to the vehicles.

To run Vehicle:
python3 main.py vehicle --id 1 --pip 127.0.0.1 --pport 5502 --cache_size 2 --input_file "requests.csv"

  vehicle ID: Change ID to run multiple vehicles simulataneously
  
  pip: parent IP/ IP of the RSU 
  
  port: Parent Port/ Port of the RSU to be connected to
  
  cache_size: Size of the LRU cache implemented at the vehicle in units of Tile sizes
  
  input_file: The input file consisting of the vehicle requests
  
  




To run RSU:
python3 main.py rsu --id 1 --sip 127.0.0.1 --sport 5502 --algo flat --pattern alternate

  id: RSU ID, can change IDs to create multiple instances of an RSU
  
  sip: self IP
  
  sport: self Port
  
  algo: flat(default for all modes- Basic, Adaptive and Optimal)
  
  pattern: alternate(default for all modes, alternating pattern of appearance of .osm and .pcd layer in the broadcast channel)

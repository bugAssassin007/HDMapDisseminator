from ast import arg
import logging, argparse
import string
from rsu import rsu
from vehicle import vehicle
#from folder import file

def rsu_main(args: argparse.Namespace):

    #object=file.classname
    # rsu_o=rsu.RSU(args.id, args.sip,args.sport, args.algo, args.pattern)
    #object.function name
    # rsu_o.rsu_script()
    rsu.main(args.id, args.sip,args.sport, args.algo, args.pattern)


def vehicle_main(args:argparse.Namespace):
    # vehicle_o=vehicle.Vehicle(args.pip,args.pport,args.input_file)
    # vehicle_o.veh_script()
    vehicle.main(args.id,args.pip,args.pport,args.input_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Starts  Application')
    subparsers = parser.add_subparsers(dest='mode', help='application mode (vehicle/rsu)')
    subparsers.required = True
    parser_rsu = subparsers.add_parser('rsu')
    parser_rsu.add_argument('--id', metavar='rsu_identifier', type=int,help='identifier for RSU')
    parser_rsu.add_argument('--sip', metavar='self_ip', help='self ip for dealing with requests to self')
    parser_rsu.add_argument('--sport', metavar='self_port', type=int, help='self port for dealing with requests to self')
    parser_rsu.add_argument('--algo', metavar='type_of_organisation', help='Mode of broadcast organisation- flat or prioritized ')
    parser_rsu.add_argument('--pattern', metavar='pattern(block/alternate)', help='Pattern of the broadcast channel')
    #parser_rsu.add_argument('--input-file', metavar='input_csv_file',help='Input CSV file consisting of the vehicle routes')

    parser_client = subparsers.add_parser('vehicle')
    parser_client.add_argument('--id', metavar='vehicle_id', type=int, help='identifier for the vehicle')
    parser_client.add_argument('--pip', metavar='parent_ip', help='parent rsu ip to which vehicle is connected')
    parser_client.add_argument('--pport', metavar='parent_port', type=int, help='parent rsu port to which vehicle is connected')
    parser_client.add_argument('--input_file', metavar='input_csv_file', help='Input CSV file consisting of the vehicle routes')
    #TO DO: can also take in number of vehicles as argument.

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.mode == 'vehicle':

        vehicle_main(args)

    elif args.mode == 'rsu': 
        rsu_main(args)
    else:
        print("check command line options")

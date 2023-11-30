from ast import arg
import logging, argparse
import string
from rsu import rsu
from vehicle import vehicle
import utils.common_args as common_args
import control
#from folder import file

def rsu_main(args: argparse.Namespace):

    rsu.main(args.id, args.sip,args.sport, args.algo, args.pattern)

if __name__ == "__main__":
    args = common_args.common_args()
    logging.basicConfig(level=logging.INFO)
    if args.mode == 'vehicle':
        vehicle.main(args)

    elif args.mode == 'rsu': 
        rsu_main(args)
    elif args.mode == 'control':
        control.main(args)
    else:
        print("check command line options")

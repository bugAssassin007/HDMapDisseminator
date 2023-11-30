import argparse

def handler_keyboard_interrupt():
    raise KeyboardInterrupt()

def common_args() -> argparse.Namespace:
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
    parser_client.add_argument('--cache_size', metavar='cache_size', type=int, help='size of the cache, signifying the number of tiles it can store')
    parser_client.add_argument('--input_file', metavar='input_csv_file', help='Input CSV file consisting of the vehicle routes')
    parser_client.add_argument('--ciip', metavar='control_iteration_ip', help='iteration control IP address')
    parser_client.add_argument('--ciport', metavar='control_iteration_port', help='iteration control port')
    parser_client.add_argument('--csip', metavar='control_step_ip', help='step control IP address')
    parser_client.add_argument('--csport', metavar='control_step_port', help='step control port')

    parser_control = subparsers.add_parser('control')
    parser_control.add_argument('--input_file', metavar='control_input_csv_file', help='Input CSV file consisting of the vehicle routes')
    parser_control.add_argument('--ciip', metavar='control_iteration_ip', help='iteration control IP address')
    parser_control.add_argument('--ciport', metavar='control_iteration_port', help='iteration control port')
    parser_control.add_argument('--csip', metavar='control_step_ip', help='step control IP address')
    parser_control.add_argument('--csport', metavar='control_step_port', help='step control port')


    #TO DO: can also take in number of vehicles as argument.

    return parser.parse_args()


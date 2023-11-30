import time
import subprocess as sp
import pandas as pd
import zmq
from utils.common_args import common_args, handler_keyboard_interrupt
import signal

class Controller:
    def __init__(self, input_file, ciip, ciport, csip, csport):
        #vehicle1 = Vehicle(1,'127.0.0.1',5555,'hello')
        self.context = zmq.Context()
        self.iteration_socket = self.context.socket(zmq.PUB)
        self.iteration_socket.bind(f"tcp://{ciip}:{ciport}")

        self.step_socket = self.context.socket(zmq.REP)
        self.step_socket.bind(f"tcp://{csip}:{csport}")

        self.df = pd.read_csv(input_file)

    def start_iteration(self):
        time.sleep(5)
        grouped = self.df.groupby('Time')
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        for name, group in grouped:
            try:
                self.process(group, name)
            except KeyboardInterrupt:
                self.iteration_socket.close()
                self.step_socket.close()
                self.context.term()
                break
            # finally:
            #     print('Closing sockets')
            #     self.iteration_socket.close()
            #     self.step_socket.close()
            #     self.context.term()
        self.iteration_socket.send(b'END')

    def process(self, df, name):
        print(name)
        self.iteration_socket.send_string(str(name))
        num_of_clients = len(df)
        for _ in range(num_of_clients):
            print('Waiting for clients to finish')
            self.step_socket.recv()
            self.step_socket.send(b'')


def main(args):
    c = Controller(args.input_file, args.ciip, args.ciport, args.csip, args.csport)
    c.start_iteration()

if __name__ == "__main__":
    args = common_args()
    main(args)
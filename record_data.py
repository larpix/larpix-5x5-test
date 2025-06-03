import larpix
import larpix.io
# from base import utility_base
import larpix.format.rawhdf5format as rhdf5
import time
import larpix.format.pacman_msg_format as pacman_msg_fmt
import argparse
import pickle

from util import data, save_controller

def unmask(c, keys):
    for i in range(10):
        for key in reversed(keys):

            c[key].config.csa_enable= [1]*64
            c[key].config.channel_mask= [1]*64
            c[key].config.periodic_trigger_mask=[0]*64
            c.write_configuration(key, 'periodic_trigger_mask')
            c.write_configuration(key, 'csa_enable')
            c.write_configuration(key, 'channel_mask')


def main(runtime=60, file_count=1, data_dir='/data/v3/5x5/cold_Apr2025/'):
    
    #load controller
    c=larpix.Controller()
    c.io = larpix.io.PACMAN_IO(relaxed=True, asic_version=3)
   
    for i in range(file_count):
        data(c,runtime, data_dir=data_dir )
    

if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        
        parser.add_argument('--file_count', default=1, type=int, help='''number of consecutive files to record''')
        parser.add_argument('--runtime', default=60, type=int, help='''Time in seconds for each data file''')
        parser.add_argument('--data_dir', default='/data/v3/5x5/cold_Apr2025/cosmics_5kv_3/', type=str, help='''Path to write data file, default is in current directory''')
        args = parser.parse_args()
        main(**vars(args))         

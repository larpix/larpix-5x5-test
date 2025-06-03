import larpix
import larpix.io
# from base import utility_base
import argparse
import time

import pickle


def power_readback(io, io_group, pacman_version, tile):
    readback={}
    for i in tile:
        readback[i]=[]
        if pacman_version=='v1rev4':
            vdda=io.get_reg(0x24030+(i-1), io_group=io_group)
            vddd=io.get_reg(0x24040+(i-1), io_group=io_group)
            idda=io.get_reg(0x24050+(i-1), io_group=io_group)
            iddd=io.get_reg(0x24060+(i-1), io_group=io_group)
            print('Tile ',i,'  VDDA: ',vdda,' mV  IDDA: ',int(idda*0.1),' mA  ',
                  'VDDD: ',vddd,' mV  IDDD: ',int(iddd>>12),' mA')
            readback[i]=[vdda, idda*0.1, vddd, iddd>>12]
        elif pacman_version=='v1rev3' or 'v1revS1':
            vdda=io.get_reg(0x00024001+(i-1)*32+1, io_group=io_group)
            idda=io.get_reg(0x00024001+(i-1)*32, io_group=io_group)
            vddd=io.get_reg(0x00024001+(i-1)*32+17, io_group=io_group)
            iddd=io.get_reg(0x00024001+(i-1)*32+16, io_group=io_group)
            print('Tile ',i,'  VDDA: ',(((vdda>>16)>>3)*4),' mV  IDDA: ',
                  (((idda>>16)-(idda>>31)*65535)*500*0.001),' mV  VDDD: ',\
                  (((vddd>>16)>>3)*4),' mV  IDDD: ',
                  (((iddd>>16)-(iddd>>31)*65535)*500*0.001),' mA')
            readback[i]=[(((vdda>>16)>>3)*4),
                         (((idda>>16)-(idda>>31)*65535)*500*0.001),
                         (((vddd>>16)>>3)*4),
                         (((iddd>>16)-(iddd>>31)*65535)*500*0.001)]
        else:
            print('WARNING: PACMAN version ',pacman_version,' unknown')
            return readback
    return readback


def main(vdda, vddd, io_group=1, pacman_tile=1, verbose=True):

    ###########################################
    IO_GROUP = io_group
    PACMAN_TILE = pacman_tile  # 1IO_CHAN = 25 # 1
    IO_CHAN = (pacman_tile-1) * 4 + 1
    VDDA_DAC = vdda #VDDA_DAC = 52000 #48000 cold
    VDDD_DAC = vddd #VDDD_DAC = 28000 # 32000# 28500 # ~1.1 V #42000 cold
    RESET_CYCLES = 300000  # 5000000

    # create a larpix controller
    c = larpix.Controller()
    c.io = larpix.io.PACMAN_IO(relaxed=True, asic_version=3)
    io_group = IO_GROUP
    pacman_version = 'v1rev4'
    pacman_tile = [PACMAN_TILE]

    bitstring = list('00000000000000000000000000000000')
    rx_en = c.io.get_reg(0x18, io_group)
    c.io.set_reg(0x18, int("".join(bitstring), 2), io_group)
    if True:
        print('disable pacman power')
        # disable tile power, LARPIX clock
        c.io.set_reg(0x00000010, 0, io_group)
        c.io.set_reg(0x00000014, 0, io_group)

        readback = power_readback(
        c.io, io_group, pacman_version, [PACMAN_TILE])
        time.sleep(0.015)
    
if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--io_group', default=1, type=int, help='''Which io_group, default 1''')
        parser.add_argument('--pacman_tile', default=1, type=int, help='''Which tile to enable power on''')
        parser.add_argument('--vdda', default=46000, type=int, help='''VDDA dac value''')
        parser.add_argument('--vddd', default=22000, type=int, help='''VDDA dac value''')
        args = parser.parse_args()
        main(**vars(args))

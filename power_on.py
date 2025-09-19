import larpix
import larpix.io
# from base import utility_base
import argparse
import time

import pickle


def power_readback(io, io_group, pacman_version, tile):
    readback = {}
    for i in tile:
        readback[i] = []
        if pacman_version == 'v1rev4':
            vdda = io.get_reg(0x24030+(i-1), io_group=io_group)
            vddd = io.get_reg(0x24040+(i-1), io_group=io_group)
            idda = io.get_reg(0x24050+(i-1), io_group=io_group)
            iddd = io.get_reg(0x24060+(i-1), io_group=io_group)
            print('Tile ', i, '  VDDA: ', vdda, ' mV  IDDA: ', int(idda*0.1), ' mA  ',
                  'VDDD: ', vddd, ' mV  IDDD: ', int(iddd >> 12), ' mA')
            readback[i] = [vdda, idda*0.1, vddd, iddd >> 12]
        elif pacman_version == 'v1rev3' or 'v1revS1':
            vdda = io.get_reg(0x00024001+(i-1)*32+1, io_group=io_group)
            idda = io.get_reg(0x00024001+(i-1)*32, io_group=io_group)
            vddd = io.get_reg(0x00024001+(i-1)*32+17, io_group=io_group)
            iddd = io.get_reg(0x00024001+(i-1)*32+16, io_group=io_group)
            print('Tile ', i, '  VDDA: ', (((vdda >> 16) >> 3)*4), ' mV  IDDA: ',
                  (((idda >> 16)-(idda >> 31)*65535)*500*0.001), ' mV  VDDD: ',
                  (((vddd >> 16) >> 3)*4), ' mV  IDDD: ',
                  (((iddd >> 16)-(iddd >> 31)*65535)*500*0.001), ' mA')
            readback[i] = [(((vdda >> 16) >> 3)*4),
                           (((idda >> 16)-(idda >> 31)*65535)*500*0.001),
                           (((vddd >> 16) >> 3)*4),
                           (((iddd >> 16)-(iddd >> 31)*65535)*500*0.001)]
        else:
            print('WARNING: PACMAN version ', pacman_version, ' unknown')
            return readback
    return readback


def main(vdda, vddd, io_group=1, pacman_tile='1', verbose=True):

    ###########################################
    IO_GROUP = io_group
    VDDA_DAC = vdda  # VDDA_DAC = 52000 #48000 cold
    VDDD_DAC = vddd  # VDDD_DAC = 28000 # 32000# 28500 # ~1.1 V #42000 cold
    RESET_CYCLES = 300000  # 5000000

    list_pacman_tiles = pacman_tile.split(',')
    for i in range(len(list_pacman_tiles)):
        list_pacman_tiles[i] = int(list_pacman_tiles[i].strip())

    # create a larpix controller
    c = larpix.Controller()
    c.io = larpix.io.PACMAN_IO(relaxed=True, asic_version=3)
    io_group = IO_GROUP
    pacman_version = 'v1rev4'

    bitstring = list('00000000000000000000000000000000')
    rx_en = c.io.get_reg(0x18, io_group)
    c.io.set_reg(0x18, int("".join(bitstring), 2), io_group)

    print('enable pacman power')
    # set up mclk in pacman
    c.io.set_reg(0x101c, 4, io_group)

    # enable pacman power
    c.io.set_reg(0x00000014, 1, io_group)

    # set uart clock ratio and power for all tiles
    for PACMAN_TILE in list_pacman_tiles:
        IO_CHAN = (PACMAN_TILE-1) * 4 + 1
        c.io.set_uart_clock_ratio(IO_CHAN,   5)
        time.sleep(0.015)
        c.io.set_uart_clock_ratio(IO_CHAN+1, 5)
        time.sleep(0.015)
        c.io.set_uart_clock_ratio(IO_CHAN+2, 5)
        time.sleep(0.015)
        c.io.set_uart_clock_ratio(IO_CHAN+3, 5)

        time.sleep(0.015)

        # set voltage dacs  VDDD first
        c.io.set_reg(0x24020+(PACMAN_TILE-1), VDDD_DAC, io_group)
        c.io.set_reg(0x24010+(PACMAN_TILE-1), VDDA_DAC, io_group)

    c.io.reset_larpix(length=1024)
    c.io.reset_larpix(length=1024)

    # enable tile power
    tile_enable_sum = 0
    tile_enable_val = 0
    for PACMAN_TILE in list_pacman_tiles:
        tile_enable_sum = pow(2, PACMAN_TILE-1) + tile_enable_sum
        tile_enable_val = tile_enable_sum+0x0200  # enable one tile at a time
        c.io.set_reg(0x00000010, tile_enable_val, io_group)
        time.sleep(0.05)

    readback = power_readback(
        c.io, io_group, pacman_version, list_pacman_tiles)

    c.io.reset_larpix(length=1024)
    c.io.reset_larpix(length=1024)
    c.io.reset_larpix(length=1024)
    c.io.reset_larpix(length=1024)

    with open('controller.pkl', 'wb') as f:
        c.io = None
        pickle.dump(c, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--io_group', default=1, type=int,
                        help='''Which io_group, default 1''')
    parser.add_argument('--pacman_tile', default='1', type=str,
                        help='''Which tile to enable power on''')
    parser.add_argument('--vdda', default=56000, type=int,
                        help='''VDDA dac value''')
    parser.add_argument('--vddd', default=30000, type=int,
                        help='''VDDA dac value''')
    args = parser.parse_args()
    main(**vars(args))

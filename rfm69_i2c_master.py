#!/usr/bin/env python

# https://www.abelectronics.co.uk/kb/article/1094/i2c-part-4---programming-i-c-with-python


def main():
    '''
    Main program function
    '''
buf = [0,0]
 
if __name__ == "__main__":
    main()
    
from smbus import SMBus
import time

i2cbus = SMBus(1)  # Create a new I2C bus
i2c_address = 0x20  # Address of keypad
RFM69_RESET          = 0x01
RFM69_CLR_RX         = 0x02
RFM69_CLR_TX         = 0x03
RFM69_SEND_MSG       = 0x10
RFM69_RX_AVAIL       = 0x40
RFM69_TX_FREE        = 0x50

print('Starting...')
send_msg = ['H','e','l','l','o', ' ','W','o','r','l','d'  ]
send_msg_int = [ord(str) for str in send_msg]

# i2cbus.write_i2c_block_data(i2caddress,SET_KEY_VALUES_CMND, New_Int_Values)
buf = [0,0]
time.sleep(1)
i2cbus.write_block_data(i2c_address, RFM69_RESET,buf)
# i2cbus.write_i2c_block_data(i2c_address, RFM69_SEND_MSG, send_msg_int)

while 1:
    try:
        # buf = i2cbus.read_i2c_block_data(i2caddress,RD_KEY_CMND,2)
        tx_free = i2cbus.read_byte_data(i2c_address, RFM69_TX_FREE)
        time.sleep(0.1)
        i2cbus.write_i2c_block_data(i2c_address, RFM69_SEND_MSG, send_msg_int)
    except:
        buf[0] = 0
    # duration = i2cbus.read_byte(i2caddress)
    #if buf[0] != 0:
    print(tx_free)
    time.sleep(1)

#!/usr/bin/env python

# https://www.abelectronics.co.uk/kb/article/1094/i2c-part-4---programming-i-c-with-python


def main():
    '''
    Main program function
    '''
buf = [0,0]
 
if __name__ == "__main__":
    main()
    
from smbus2 import SMBus
import time

# i2cbus = SMBus(1)  # Create a new I2C bus
i2c_address = 0x20  # Address of keypad
I2C_BUF_LEN = 16
RFM69_RESET          = 0x01
RFM69_CLR_RX         = 0x02
RFM69_CLR_TX         = 0x03
RFM69_SEND_MSG       = 0x10
RFM69_TX_DATA        = 0x11
RFM69_RX_AVAIL       = 0x40
RFM69_RX_LOAD_MSG    = 0x41
RFM69_RX_RD_MSG      = 0x42
RFM69_RX_RD_LEN      = 0x43

RFM69_TX_FREE        = 0x50


def wr_i2c_vector( i2c_addr, cmd, data):
    dindx    = 0
    wr_bytes = 0
    all_done = False
    data_len = len(data)
    tx_buf   = [0]*I2C_BUF_LEN
    # print('data_len=',data_len)
    # print('data=',data)
    
    while not all_done:
         wr_bytes = I2C_BUF_LEN - 1
         if (dindx + wr_bytes) >= data_len:
             wr_bytes = data_len - dindx 
             
         if wr_bytes > 0:
             tx_buf = [dindx] + data[dindx:dindx + wr_bytes]
             with SMBus(1) as bus:
                 print(dindx, ': ', tx_buf)
                 bus.write_i2c_block_data(i2c_addr, cmd, tx_buf)
                 time.sleep(0.1)
             dindx = dindx + wr_bytes  
         else:
            all_done = True
                 
                 
    

print('Starting...')
# send_msg = ['H','e','l','l','o', ' ','W','o','r','l','d','-','0','\0'  ]
#                0         1         2         3         4         5         6
#                0123456789012345678901234567890123456789012345678901234567890123456789
send_msg = list('Villa Astrid long message  over 32 0' + '\0')
# send_msg = list('Villa Astrid  0' + '\0')
print(send_msg)
# send_msg = 'Villa Astrid 0' + '\0'
send_msg_int = [ord(str) for str in send_msg]

# wr_i2c_vector( i2c_address, RFM69_TX_DATA, send_msg_int)

#for i in send_msg_int:
#    print(i)
    
# i2cbus.write_i2c_block_data(i2caddress,SET_KEY_VALUES_CMND, New_Int_Values)
buf = [0,0]
i = 0
tx_free = 0
time.sleep(1)
with SMBus(1) as bus:
    bus.write_byte_data(i2c_address, 0, RFM69_RESET)
# i2cbus.write_i2c_block_data(i2c_address, RFM69_SEND_MSG, send_msg_int)
tx_buf = [32] + send_msg_int[0:31]
print(tx_buf)
print(send_msg_int)
print(send_msg_int[0:31])
print(send_msg_int[31:])
#print(send_msg_int)

while 1:
    try:
        send_msg_int[-2] = (i & 0x7)+0x30
        # buf = i2cbus.read_i2c_block_data(i2caddress,RD_KEY_CMND,2)
        with SMBus(1) as bus:
            # bus.write_byte_data(i2c_address, 0, RFM69_TX_FREE)
            tx_free = bus.read_byte_data(i2c_address, RFM69_TX_FREE)
        print('tx_free', tx_free)
        time.sleep(0.5)
        wr_i2c_vector( i2c_address, RFM69_TX_DATA, send_msg_int)
        time.sleep(0.5)
        with SMBus(1) as bus:
            bus.write_byte_data(i2c_address, RFM69_SEND_MSG,0)
        time.sleep(0.5)    
        with SMBus(1) as bus:    
            rx_avail = bus.read_byte_data(i2c_address, RFM69_RX_AVAIL)
            print('Rx Available = ',rx_avail)
    except:
        buf[0] = 0
        print('Error when writing to I2C')
    # duration = i2cbus.read_byte(i2caddress)
    #if buf[0] != 0:
    i = i + 1
    time.sleep(5)

#!/usr/bin/env python

# https://www.abelectronics.co.uk/kb/article/1094/i2c-part-4---programming-i-c-with-python
# https://www.engineersgarage.com/raspberrypi/articles-raspberry-pi-i2c-bus-pins-smbus-smbus2-python/


def main():
    '''
    Main program function
    '''
buf = [0,0]
 
if __name__ == "__main__":
    main()
    
from smbus2 import SMBus

import time
import json
import sys
from Adafruit_IO import Client, Feed, RequestError
 
# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

#cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
#sys.path.append(cwd)
#print(cwd)
sys.path.append('/home/pi/project/libraries')
print(sys.path)


try:
    from MySecrets import secrets
except ImportError:
    print("My secrets are kept in secrets.py, please add them there!")
    raise

print('Secrets: ', secrets)
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
RFM69_RX_RD_MSG1     = 0x42
RFM69_RX_RD_MSG2     = 0x43
RFM69_RX_RD_LEN      = 0x44

RFM69_TX_FREE        = 0x50

MIN_UPLOAD_INTERVAL  = 60.0*5

aio_dict = {'Dock_T_Water': {'feed':'villaastrid.water-temp','available': False, 'timeto': 0.0, 'value':0.0},
            'Dock_T_bmp180': {'feed':'villaastrid.dock-temp','available': False, 'timeto': 0.0, 'value':0.0},
            'Dock_P_bmp180': {'feed':'villaastrid.dock-pres','available': False, 'timeto': 0.0, 'value':0.0},
            'Dock_T_dht22': {'feed':'villaastrid.outdoor1-temp-dht22','available': False, 'timeto': 0.0, 'value':0.0},
            'Dock_H_dht22': {'feed':'villaastrid.dock-hum-dht22','available': False, 'timeto': 0.0, 'value':0.0},
            'OD_1_Temp':  {'feed':'villaastrid.outdoor1-temp','available': False, 'timeto': 0.0, 'value':0.0},
            'OD_1_Hum':  {'feed':'villaastrid.outdoor1-hum-dht22','available': False, 'timeto': 0.0, 'value':0.0},
            'OD_1_P_mb':  {'feed':'villaastrid.outdoor1-pmb','available': False, 'timeto': 0.0, 'value':0.0},
            'OD_1_Light1':  {'feed':'villaastrid.outdoor1-ldr1','available': False, 'timeto': 0.0, 'value':0.0},
            'OD_1_Temp2': {'feed':'villaastrid.outdoor1-temp-dht22','available': False, 'timeto': 0.0,  'value':0.0}}
for key in aio_dict:
    aio_dict[key]['timeto'] = time.monotonic() 

# {'Z': 'OD_1', 'S': 'Temp2', 'V': 17.17, 'R': ''}
# {'Z': 'Dock', 'S': 'H_dht22', 'V': 99.9, 'R': ''}
# {'Z': 'Dock', 'S': 'T_dht22', 'V': 18.2, 'R': ''}
# {'Z': 'OD_1', 'S': 'P_mb', 'V': 1009.86, 'R': ''}
# {'Z': 'OD_1', 'S': 'Hum', 'V': 67.5, 'R': ''}
# {'Z': 'OD_1', 'S': 'Light1', 'V': '777', 'R': ''}
# {'Z': 'Dock', 'S': 'P_bmp180', 'V': '990.0', 'R': ''}


print(aio_dict)

# check for new values and upload to AIO if min interval requirement is fulfilled
def upload_feed_to_aio():
    for key in aio_dict:
        if aio_dict[key]['available']:
            if time.monotonic() > aio_dict[key]['timeto']:
                aio_dict[key]['timeto'] = time.monotonic() + MIN_UPLOAD_INTERVAL
                aio_dict[key]['available'] = False
                try:
                    client.publish(aio_dict[key]['feed'], aio_dict[key]['value'])
                    print('Feed ', aio_dict[key]['feed'], ' uploaded')
                except:
                    print('Feed ', aio_dict[key]['feed'], ' upload failed')

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for DemoFeed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('rpi-test.red-led')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    if feed_id == AIO_REDLED_FEED:
        GPIO.output(red_led, GPIO.HIGH if payload == 'ON' else GPIO.LOW)
        

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
            with SMBus(1) as txbus:
                print(dindx, ': ', tx_buf)
                txbus.write_i2c_block_data(i2c_addr, cmd, tx_buf)
                time.sleep(0.1)
            dindx = dindx + wr_bytes  
        else:
            all_done = True
                 
 
def save_measurement(m_dict):
    global aio_dict
    m_key = m_dict['Z'] + '_' + m_dict['S']
    print(m_key)
    if m_key in aio_dict:
        print ('key found, AIO=',aio_dict[m_key])
        aio_dict[m_key]['available'] = True
        aio_dict[m_key]['value'] = m_dict['V']
        
    else:
        print ('key not found')
        
def read_rfm69_msg():        
    do_continue = True
    # print('- - - - - - - - - - - - - - - - - - - - - - - -')
    if do_continue:
        with SMBus(1) as bus:
            try:
                rx_avail = bus.read_byte_data(i2c_address, RFM69_RX_AVAIL)
                # print('Rx Available = ',rx_avail)
            except:
                print('Failed when bus.read_byte_data')
                do_continue = False
    if do_continue:
        if rx_avail > 0:
            with SMBus(1) as bus:
                time.sleep(1)
                try:
                    rd_len = 0
                    rd_len = bus.read_byte_data(i2c_address, RFM69_RX_LOAD_MSG)
                    print('rd_len=',rd_len)
                except:
                    do_continue = False
                    print('LOAD_MSG Error')
        else:
            do_continue = False

    if do_continue:
        try:
            with SMBus(1) as bus:
                rd1 = [0]*32
                rd2 = [0]*32
                rd1 = bus.read_i2c_block_data(i2c_address, RFM69_RX_RD_MSG1,32)
                rd2 = bus.read_i2c_block_data(i2c_address, RFM69_RX_RD_MSG2, rd_len - 32)
                rd = rd1 + rd2
                print(rd)
                i = 0
                while rd[i] != 0x00:
                    i = i + 1
                rd = rd[0:i]
                print(rd)
                
        except:    
            do_continue = False
            print('read block data failed')                
        
                        
    if do_continue:
        x = 255
        try:
            for i in range(len(rd)):
                if x == 0:
                    rd[i] = 0
                elif rd[i] == 0:
                    x = 0
        except:
            do_continue = False
            print('Error when fillin the vector with zero: ')

    if do_continue:
        try:
            for i in range(len(rd)):
                if rd[i] > 127:
                    do_continue = false
            if not do_continue:
                print('Error illegalcharacters: ')    
        except:
            do_continue = False
            print('Error when identifying illegal characters: ')

    if do_continue:
        try:
            b = bytes(rd)
            print(b)
            s = b.decode('utf-8')
            print(s)
        except:
            print('Error when decoding message: ')
            do_continue = false
            
    if do_continue:
        try:
            
            msg_dict = json.loads(s)
            print('msg=',msg_dict)
            save_measurement(msg_dict)
            
        except:
            print('Error when preparing json: ',s)
    return do_continue

# Create an MQTT client instance.
client = MQTTClient(secrets['aio_username'], secrets['aio_key'])
# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
# Connect to the Adafruit IO server.
client.connect()
client.loop_background()
# Now send new values every 10 seconds.

 

while 1:
    # read sensor messages and fill the dictionary with new values
    if read_rfm69_msg():    
        upload_feed_to_aio()
    
    time.sleep(5)

#  scratchpad   #######################################################################

# {"Z":"Dock","S":"P_bmp180","V":986.00,"R":""} 

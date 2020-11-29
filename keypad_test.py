import time
import sys 
import board
import busio

sys.path.append('/home/pi/project/libraries')
print(sys.path)

import keypad_i2c
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
# i2c = board.I2C()
kp = keypad_i2c.keypad_i2c(i2c)

while True:
    try:
       key, dur = kp.key_pressed
    except:
       key = 0x00

    if key != 0x00:
        key_str = chr(key) + chr(dur)
        print(key_str)

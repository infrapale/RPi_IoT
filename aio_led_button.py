# aio_led_button.py
#
# Description:
# Interfaces an LED and a button with the Adafruit IO service.
#
# Circuit:
# Red LED connected to BCM pin 21, physical pin 40.
# Momentary push button connected to BCM pin 5, physical pin 29.
#
# Created by John Woolsey on 05/24/2019.
# Copyright (c) 2019 Woolsey Workshop.  All rights reserved.

# https://github.com/adafruit/Adafruit_IO_Python


# Libraries
import RPi.GPIO as GPIO
from time import sleep
from Adafruit_IO import Client, Feed, RequestError
import json


with open ('../secrets.json') as file:
    secrets = json.load(file)

print(secrets)

# Pin Mapping
button =   5
red_led = 21


# Global Variables
AIO_USERNAME    = secrets['AIO']['username']
AIO_KEY         = secrets['AIO']['key']
AIO_BUTTON_FEED = "home-tampere.button"
AIO_REDLED_FEED = "home-tampere.led"
button_state    = False
red_led_state   = False
#infrapale/feeds/home-tampere.button

# Functions

def button_pressed(button):
   """Toggles and sends button state to AIO service.

   Parameters:
      button: The pressed button.

   Returns:
      None
   """
   global button_state
   print("Button pressed.")
   button_state = not button_state
   aio.send(button_feed.key, 1 if button_state else 0)


# Main

# Pin configuration
GPIO.setmode(GPIO.BCM)                                 # use BCM pin numbering
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # utilize microprocessor's internal pull-up resistor
GPIO.setup(red_led, GPIO.OUT)

# Initialize interrupt service routine
# Calls button_pressed() function when button is pressed,
# i.e., the button pin value falls from high to low.
GPIO.add_event_detect(button, GPIO.FALLING, callback=button_pressed, bouncetime=250)

# Adafruit IO configuration
aio = Client(AIO_USERNAME, AIO_KEY)  # create Adafruit IO REST client instance
try:  # connect to existing button feed
   button_feed = aio.feeds(AIO_BUTTON_FEED)
except RequestError:  # or create button feed if it does not exist
   button_feed = aio.create_feed(Feed(name=AIO_BUTTON_FEED))
try:  # connect to existing red LED feed
   red_led_feed = aio.feeds(AIO_REDLED_FEED)
except RequestError:  # or create red LED feed if it does not exist
   red_led_feed = aio.create_feed(Feed(name=AIO_REDLED_FEED))

# Synchronize feed states
#button_state = True if aio.receive(button_feed.key).value == "1" else False
#red_led_state = True if aio.receive(red_led_feed.key).value == "ON" else False
GPIO.output(red_led, GPIO.HIGH if red_led_state else GPIO.LOW)

print("Press CTRL-C to exit.")
try:
   while True:
      # Retrieve and update LED state
    data = aio.receive(button_feed.key)
    if int(data.value) == 1:
        print('received <- ON\n')
    elif int(data.value) == 0:
        print('received <- OFF\n')

    data = aio.receive(red_led_feed.key)
    if int(data.value) == 1:
        GPIO.output(red_led, GPIO.HIGH) 
    elif int(data.value) == 0:
        GPIO.output(red_led, GPIO.LOW )
      
        #red_led_state = True if aio.receive(red_led_feed.key).value == "ON" else False
        #GPIO.output(red_led, GPIO.HIGH if red_led_state else GPIO.LOW)

        # Do not flood AIO with requests
        sleep(1.0)

# Cleanup
finally:           # exit cleanly when CTRL+C is pressed
   GPIO.cleanup()  # release all GPIO resources
   print("\nCompleted cleanup of GPIO resources.")
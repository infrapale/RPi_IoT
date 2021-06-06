# mqrr_client_class.py
# Author: Tom Hoglund
# https://github.com/adafruit/Adafruit_IO_Python
# Import standard python modules.
import random
import sys
import time
import RPi.GPIO as GPIO
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

# Pin Mapping
button          = 5
red_led         = 21
button_state    = False
red_led_state   = False

AIO_BUTTON_FEED      = "rpi-test.button"
AIO_REDLED_FEED      = "rpi-test.red-led"


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
   if button_state:
       client.publish(AIO_BUTTON_FEED, 1)
   else:
       client.publish(AIO_BUTTON_FEED, 0)
       
   #aio.send(button_feed.key, 1 if button_state else 0)


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
        
            
# Pin configuration
GPIO.setmode(GPIO.BCM)                                 # use BCM pin numbering
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # utilize microprocessor's internal pull-up resistor
GPIO.setup(red_led, GPIO.OUT)

# Initialize interrupt service routine
# Calls button_pressed() function when button is pressed,
# i.e., the button pin value falls from high to low.
GPIO.add_event_detect(button, GPIO.FALLING, callback=button_pressed, bouncetime=250)
    


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
print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
while True:
    value = random.randint(0, 100)
    print('Publishing {0} to DemoFeed.'.format(value))
    client.publish('DemoFeed', value)
    time.sleep(10)

import time
#from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import board
import busio
import adafruit_mcp9808

i2c_bus = busio.I2C(board.SCL, board.SDA)

# To initialise using the default address:
mcp = adafruit_mcp9808.MCP9808(i2c_bus)




received_count = 0
received_all_event = threading.Event()

my_keys = {
    "endpoint": "a2febl6wg07iik-ats.iot.eu-central-1.amazonaws.com",
    "cert_filepath": "/home/pi/myAWS/Keys/certificate.pem.crt",
    "pri_key_filepath": "/home/pi/myAWS/Keys/private.pem.key",
    "ca_filepath": "/home/pi/myAWS/Keys/root-ca.pem",
    "client_id": "IpaID",
    "count": 100,
    "topic": "ipa_testing",
    "message": "Hello from ipa"
    }

iot_topics = {
    'sensors': 'MCP9808'
}
 
print(type(my_keys['count']))
print(type(received_count))

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == 10:
        received_all_event.set()



if __name__ == '__main__':
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    print(client_bootstrap)

   
    
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint = my_keys["endpoint"] ,
        cert_filepath = my_keys["cert_filepath"],
        pri_key_filepath= my_keys["pri_key_filepath"],
        client_bootstrap=client_bootstrap,
        ca_filepath= my_keys["ca_filepath"],
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id = my_keys['client_id'],
        clean_session=False,
        keep_alive_secs=6)
    
    print("Connecting to {} with client ID '{}'...".format(
        my_keys['endpoint'], my_keys['client_id']))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(my_keys['topic']))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic = my_keys['topic'],
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if my_keys['message']:
        if my_keys['count'] == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(my_keys['count']))

        publish_count = 1
        while (publish_count <= my_keys['count']):
            tempC = mcp.temperature
            print("Temperature: {} C ".format(tempC))

            message = "{}".format(tempC)            
            # message = "{}  [{}]".format(my_keys['message'], publish_count)
            print("Publishing message to topic '{}': {}".format(my_keys['topic'], message))
            mqtt_connection.publish(
                topic=my_keys['topic'],
                payload=message,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")

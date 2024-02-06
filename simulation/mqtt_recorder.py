
from paho.mqtt import client as mqtt_client
import argparse
import json
import time

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default='localhost', help="IP address where broker process is running. Default is localhost")
    parser.add_argument("--port", type=int, default=1883, help="IP address where broker process is running. Default is 1883.")
    parser.add_argument("--topic", type=str, default='#', help="Topics you are interested to. Default ot all topics.")
    parser.add_argument("--store", type=str, default='', help="If you intend to register the network activity, point here the destination of a .json file which will store it.")
    parser.add_argument("--duration", "-d", type=float, default=60.0, help="Time duration, in seconds.")
    
    # If needed. add other custom stuff here.
    return parser.parse_args()



def connect_mqtt(ip:str, port:int) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)


    client = mqtt_client.Client()
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(ip, port,)
    return client


def subscribe(client: mqtt_client, topic:str, history:list = None):
    def on_message(client, userdata, msg):
        if not history is None:
            history.append({'ts':time.time(), 'topic':msg.topic, 'message':msg.payload.decode()})
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def main():
    args = get_arguments()
    if args.store != '':
        str(args.store)


    history = []

    client = connect_mqtt(args.ip, args.port)
    subscribe(client, args.topic, history)
    client.loop_start()

    time.sleep(args.duration)
    client.loop_stop()
    print('\nTotal messages:', len(history))

    if args.store != '':
        # Serializing json
        json_object = json.dumps(history, indent=4)
        # Writing to sample.json
        with open(args.store, "w") as outfile:
            outfile.write(json_object)
        print(f'Correctly stored data in {args.store}')

if __name__ == '__main__':
    main()

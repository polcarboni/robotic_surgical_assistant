import json

from paho.mqtt import client as mqtt_client
import argparse
import json
import time
import os

def get_arguments():
    """Parse all the arguments provided from the CLI.
    Returns:
      A list of parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default='localhost', help="IP address where broker process is running. Default is localhost")
    parser.add_argument("--port", type=int, default=1883, help="IP address where broker process is running. Default is 1883.")
    parser.add_argument("--source", "-s", type=str, required=True, help="The .json file containing a recorded session.")
   
    # If needed. add other custom stuff here.
    return parser.parse_args()


def main():
    args = get_arguments()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    source = str(args.source)
    assert os.path.isfile(source)
    assert source.endswith('.json')

    with open(source, 'r') as openfile:
        # Reading from json file
        session = json.load(openfile)
        print(f'Loaded {len(session)} messages form the file..')

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(args.ip, args.port)
    client.loop_start()

    current_ts = time.time()
    while True:
        try:
            for idx, m in enumerate(session):
                message = m['message']
                topic = m['topic']
                original_ts = m['ts']

                if idx > 0:
                    original_dt = original_ts - session[idx-1]['ts']
                    simuation_dt = time.time() - current_ts
                    sleep_time = original_dt - simuation_dt
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                current_ts = time.time()
                client.publish(topic, message)
                print(f"{topic} --> {message}")
        except KeyboardInterrupt:
            break

    return
    

if __name__ == '__main__':
    main()
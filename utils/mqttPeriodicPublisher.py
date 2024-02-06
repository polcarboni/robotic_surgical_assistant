
import os
import json
from paho.mqtt import client as mqtt_client
import threading
from time import sleep

from .poseBuffer import PoseBuffer


class PeriodicPublisher:
    def __init__(self, settings_path:str, id:str, data_source:PoseBuffer) -> None:

        assert os.path.isfile(settings_path)
        assert settings_path.endswith('.json')

        with open(settings_path, 'r') as openfile:
            # Reading from json file
            settings = json.load(openfile)

        self.mutex = threading.Lock()
        self.started_ = False   # protected by mutex.
        self.must_stop_ = False # protected by mutex.

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                with self.mutex:
                    self.started_ = True
            else:
                print("Failed to connect, return code %d\n", rc)

        self.topic = f"{settings['parent_topic']}/{id}"

        self.client = mqtt_client.Client()
        self.client.on_connect = on_connect
        self.client.connect(settings["broker_ip"], settings["broker_port"])
        self.client.loop_start()

        self.data_source = data_source
        self.pub_period = float(settings['pub_period'])

        self.thread_ = threading.Thread(target=self.pub_thread_)
        self.thread_.start()

    def pub_thread_(self):
        while True:
            skip=False
            with self.mutex:
                if self.must_stop_:
                    break
                if not self.started_:
                    skip = True

            if skip:
                sleep(self.pub_period)
                continue
                
            _, data = self.data_source.poll_last_data()
            self.client.publish(self.topic, data)
            #print('sent data to', self.topic)
            sleep(self.pub_period)

    def stop(self):
        """Remember to invoke me at the end!"""
        with self.mutex:
            self.must_stop_ = True
        self.client.loop_stop()
    
    def __del__(self):
        self.thread_.join()
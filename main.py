from assistant import Assistant
from paho.mqtt import client as mqtt_client
import ast
import argparse
import threading
#CONTROLLO DEGLI STATI

def parse_args():
    parser = argparse.ArgumentParser(description='Testing SamFW')
    parser.add_argument('--ip', type=str, default="localhost" )
    
    args = parser.parse_args()
    return args



class Simulation:
    def __init__(self):
        args = parse_args()
        IP = args.ip
        PORT = 1883
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
        client.on_connect = self._on_connect
        client.connect(IP, PORT, keepalive=300)
        client.on_message = self._on_message #default

        client.subscribe([("data/#",0), ("activation/#",0)])
        client.message_callback_add("data/hand_position", self._hand_position)
        client.message_callback_add("data/tool/#", self._tool_position)
        client.message_callback_add("activation/#", self._voice_act)  #va comunque fatta subscribe
        client.on_disconnect = self._on_disconnect
        self.client = client
        self.client.timeout = 180
        
        self.assistant = Assistant()
        self.name = None
        self.objs = dict()
        self.objs[0] = "pinza_box"
        self.objs[1] = "cucchiaio_box"
        self.state_lock = threading.Lock()
        self.state_lock.acquire()
        self.STATE = 0
        self.state_lock.release()
        '''
        0 -> Idle
        1 -> Voice Activated, waiting for hand position
        2 -> hand position received, start routine_1
        
        0
        1 -> tool detected, given position, start routine_2
        
        Unless the state is 0 (meaning that the robot is ready to reach given goal) every message is ignore,
        only message coming after reaching a state will be considered.
        '''

    def run(self):
        self.client.loop_start()
        while True:
            try:        
                pass
            except Exception as e:
                print(f"Exception {e} mf")
                break
        self.client.loop_stop()
    
    def _on_disconnect(self,client,userdata,flags,rc, propertiers):
        print("Client MQTT disconnected")

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
        '''client.subscribe([("topic/#",0),("data/#",0), ("activation/#",0)])
        client.message_callback_add("topic/#", self._hand_position)
        client.message_callback_add("data/#", self._tool_position)
        client.message_callback_add("activation/#", self._voice_act)  #va comunque fatta subscribe
        client.on_disconnect = self._on_disconnect
        self.client = client
        self.client.timeout = 180'''
        print(self.client)

    def _on_message(self, client, userdata, msg):
        print(f"{msg.topic} |  {msg.payload.decode()}")

    def _hand_position(self, client, userdata, msg):
        def r1(self,p1, p2):
            ret = self.assistant.routine_1(p1,p2)
            if ret:
                self.state_lock.acquire()
                self.STATE = 0
                print(f"Actual state: {self.STATE}")
                self.state_lock.release()
                
            else:
                self.state_lock.acquire()
                self.STATE = 2
                print(f"Actual state: {self.STATE}")
                self.state_lock.release()

        print("DEBUG: data/hand_position messaged arruives")
        t = None
        if self.STATE == 2 and msg.payload.decode() != '' and self.actual_name in self.assistant.world.names:
            self.state_lock.acquire()
            self.STATE = 3
            self.state_lock.release()
            print("MSG: ", msg.payload.decode())
            print("Hand position Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")
            print('------- Routine 1 -------')
            t = threading.Thread(target = r1, args= (self,self.actual_name, tuple(ast.literal_eval(msg.payload.decode()))))
            t.start()
            print('------- Routine 1 ended -------')
        
    def _tool_position(self, client, userdata, msg):
        print("DEBUG: data/tool/i message arrived")
        def r2(self,p1, p2):
            ret = self.assistant.routine_2(p1,p2)
            if ret:
                self.state_lock.acquire()
                self.STATE = 0
                print(f"Actual state: {self.STATE}")
                self.state_lock.release()
                
            else:

                self.state_lock.acquire()
                self.STATE = 0
                print(f"Actual state: {self.STATE} ")
                self.state_lock.release()


        name = self.objs[int(msg.topic.split("/")[-1])]
        if self.STATE == 0 and msg.payload.decode() != '' and name not in self.assistant.world.names:
            self.state_lock.acquire()
            self.STATE = 4
            self.state_lock.release()
            print('------- Routine 2 -------')
            t = threading.Thread(target = r2, args= (self, name, tuple(ast.literal_eval(msg.payload.decode()))))
            t.start()
            print('------- Routine 2 ended -------')

            print("Tool position Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")

    def _voice_act(self, client, userdata, msg):
        print("DEBUG: voice message arrived")
        if self.STATE == 0:
            self.state_lock.acquire()
            self.STATE = 1
            self.actual_name = self.objs[int(msg.topic.split('/')[1])]
            self.STATE = 2
            self.state_lock.release()
            print('------------------------------------')
            print("Voice activation Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")
            print('------------------------------------')
            print('Waiting for hand position...')

if __name__ == '__main__':
    Simulation().run()
'''
NOTE: 0,0,0 as orientation means the gripper points up, if you want the gripper points at least down, the correct orientation is (3.1415,0,0)
'''
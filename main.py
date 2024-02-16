from assistant import Assistant
from paho.mqtt import client as mqtt_client
import ast
import argparse
import threading
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='Testing SamFW')
    parser.add_argument('--ip', type=str, default="155.185.73.120" )
    
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

        self.wrong_position_hand = 0
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
        print("Excecution started")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Exception")
            self.client.disconnect()
        
    
    def _on_disconnect(self,client,userdata,flags,rc, propertiers):
        print("Client MQTT disconnected")

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
        

    def _on_message(self, client, userdata, msg):
        print(f"{msg.topic} |  {msg.payload.decode()}")

    def _hand_position(self, client, userdata, msg):
        def r1(self,p1, p2):
            ret = self.assistant.routine_1(p1,p2)
            if ret:
                self.state_lock.acquire()
                self.STATE = 0
                self.wrong_position_hand=0
                
            else:
                self.state_lock.acquire()
                self.wrong_position_hand+=1
                if self.wrong_position_hand < 4:
                    self.STATE = 2
                else:
                    self.STATE = 0
                    self.wrong_position_hand = 0
                
            print(f"Actual state: {self.STATE}")
            self.state_lock.release()
            print('------------------------------------')

        t = None
        if self.STATE == 2 and msg.payload.decode() != '' and self.actual_name in self.assistant.world.names:
            self.state_lock.acquire()   
            self.STATE = 3
            self.state_lock.release()
            print('------------------------------------')
            print("Hand position Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")
            
            t = threading.Thread(target = r1, args= (self,self.actual_name, tuple(ast.literal_eval(msg.payload.decode()))))
            t.start()
            print('------------------------------------')
        
    def _tool_position(self, client, userdata, msg):

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
                print(f"Actual state: {self.STATE} \n------------------------------------")
                self.state_lock.release()


        name = self.objs[int(msg.topic.split("/")[-1])]
        if self.STATE == 0 and msg.payload.decode() != '' :
            if name not in self.assistant.world.names:
                self.state_lock.acquire()
                self.STATE = 4
                self.state_lock.release()
                t = threading.Thread(target = r2, args= (self, name, tuple(ast.literal_eval(msg.payload.decode()))))
                t.start()

                
            else:
                print(f"Tool {name} already exists in the scene!")

    def _voice_act(self, client, userdata, msg):
        if self.STATE == 0:
            print('------------------------------------')
            print("Voice activation Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")
            
            self.state_lock.acquire()
            self.STATE = 1
            self.actual_name = self.objs[int(msg.topic.split('/')[1])]
            if self.actual_name not in self.assistant.world.names:
                print(f"Object not in scene!")
                self.STATE = 0
            else:
                self.STATE = 2
                print('Waiting for hand position...')
            self.state_lock.release()
            print('------------------------------------')
            
            

if __name__ == '__main__':
    try:
        Simulation().run()
    except KeyboardInterrupt:
        sys.exit()
'''
NOTE: 0,0,0 as orientation means the gripper points up, if you want the gripper points at least down, the correct orientation is (3.1415,0,0)
'''
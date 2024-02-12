from assistant import Assistant
from paho.mqtt import client as mqtt_client


#CONTROLLO DEGLI STATI




class Simulation:
    def __init__(self):

        IP = 'localhost'
        PORT = 1883
        client = mqtt_client.Client()
        client.on_connect = self._on_connect
        client.connect(IP, PORT)
        client.subscribe([("topic/#",0),("tool/#",0), ("activation/#",0)])

        client.on_message = self._on_message #default
        client.message_callback_add("topic/#", self._hand_position)
        client.message_callback_add("tool/#", self._tool_position)
        client.message_callback_add("activation/#", self._voice_act)  #va comunque fatta subscribe
        self.client = client
        self.assistant = Assistant()
        self.name = None
        self.objs =dict()
        self.objs[0] = "pinza_box"
        self.objs[1] = "cucchiaio_box"
        self.STATE = 0
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
        try:
            while True:
                pass

        except KeyboardInterrupt:
            self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def _on_message(self, client, userdata, msg):
        print(f"{msg.topic} |  {msg.payload.decode()}")

    def _hand_position(self, client, userdata, msg):
        if self.state == 1:
            self.assistant.routine_1(self.name, tuple(msg.payload.decode()))
            print("Hand position Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")
            self.state = 0

    def _tool_position(self, client, userdata, msg):
        if self.state == 0 and msg.payload.decode() != []:
            self.state = 3
            self.assistant.routine_2(self.objs[msg.topic.split("/")[1]], tuple(msg.payload.decode()))
            self.state = 0
            print("Tool position Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")

    def _voice_act(self, client, userdata, msg):
        if self.state == 0:
            self.state = 1
            self.name = msg.payload.decode()
            print("Voice activation Callback")
            print(f"{msg.topic} |  {msg.payload.decode()}")

if __name__ == '__main__':
    Simulation().run()

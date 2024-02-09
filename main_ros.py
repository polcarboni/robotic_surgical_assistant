from controls.create_world import World
from controls.control import Control, generate_pose
import time
import json

class Assistant:
    def __init__(self, filename = "/home/leo/robotic_surgical_assistant/controls/object_positions.json"):
        self.objects = ["start_tray","end_tray","pinza_box", "cucchiaio_box" ]
        self. = World()
        with open(filename, "r") as f:
            self.positions = json.load(f)

        for obj in self.objects:
            self.world.insert_tool(obj, tuple(self.positions[obj]))

        self.cntl = Control(world.get_controllers() )
        
    def get_current_conf(self):
        return self.cntl.get_current_conf()

    def get_current_position(self):
        return self.cntl.get_current_position()


    def routine_1(self,name, destination_coordinates):
        '''
        Input: name of tool, destination_coordinates
        '''
        self.cntl.open_gripper()
        loc = self.position[name]
        self.cntl.move_to_position(generate_pose(loc[0], loc[1], loc[2], 3.1415, 0, -3.1415/4))
        self.cntl.close_gripper()
        self.cntl.move_to_position(generate_pose(destination_coordinates))
        self.cntl.open_gripper() # ToDo: manage the interaction with the human
        self.cntl.move_to_rest()

    def routine_2(self, name, object_coordinates):
        '''
        Input: name of the object and its position and orientatio 
        '''
        self.cntl.open_gripper()
        loc = self.position[name]
        self.cntl.move_to_position(generate_pose(object_coordinates))
        self.cntl.close_gripper()
        self.cntl.move_to_position(generate_pose(loc[0], loc[1], loc[2], 3.1415, 0, -3.1415/4))
        self.cntl.open_gripper() # ToDo: manage the interaction with the human
        self.cntl.move_to_rest()


def main():
    assistant = Assistant()

    '''TO DO: manage interaction with other component via MQTT:

        TOPIC:
            - topics/hand_position -> [x, y, z] (note: fixed orientation)
            - tool/0-1 -> [x, y, z, rx, ry, rz] (note: the orientation is relative to the object, it isn't the one the robot should assume)

            missing: 
                -voice activation topic
    '''

if __name__ == '__main__':
    main()
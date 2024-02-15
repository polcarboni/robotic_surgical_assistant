from controls.create_world import World
from controls.control import Control, generate_pose
import time
import json

class Assistant:
    def __init__(self, filename = "/home/leo/robotic_surgical_assistant/controls/object_positions.json"):
        self.objects = ["start_tray","end_tray","pinza_box", "cucchiaio_box" ]
        self.world = World()
        with open(filename, "r") as f:
            self.positions = json.load(f)

        for obj in self.objects:
            self.world.insert_tool(obj, tuple(self.positions[obj]))

        self.cntl = Control(self.world.get_controllers() )
        self.cntl.move_to_rest()
        
    def get_current_conf(self):
        return self.cntl.get_current_conf()

    def get_current_position(self):
        return self.cntl.get_current_position()


    def routine_1(self,name, destination_coordinates):
        '''
        Input: name of tool, destination_coordinates
        '''
        
        self.cntl.open_gripper()
        loc = self.positions[name]
        obj_loc = (loc[0], loc[1], loc[2]+0.1 , 3.1415, 0, -3.1415/4)
        print("Moving into : ", obj_loc)

        # Understand if destination coordinates are valid
        valid = self.cntl.move_group.plan(generate_pose(destination_coordinates))[0]
        if valid:
            print("Position planned and valid")
            self.cntl.move_to_position(generate_pose(obj_loc))
            print("Position reached")

            self.cntl.close_gripper()
            print("Object taken")

            self.cntl.move_to_position(generate_pose(destination_coordinates))
            time.sleep(3)
            self.cntl.open_gripper() # ToDo: manage the interaction with the human
            self.world.delete_tool(name)
            print("Object delivered")

            self.cntl.move_to_rest()
            self.cntl.close_gripper()
            return True
        else:
            print("Position not valid")
            return False


    def routine_2(self, name, object_coordinates):
        '''
        Input: name of the object and its position and orientatio 
        '''
        if name not in self.world.names:
            valid = self.cntl.move_group.plan(generate_pose(object_coordinates))[0]
            if valid:
                object_coordinates = list(object_coordinates)
                object_coordinates[2] = 0.87
                self.world.insert_tool(name, object_coordinates)

                self.cntl.open_gripper()
                loc = self.positions[name]
                print(" Moving into: ",object_coordinates)
                object_coordinates = list(object_coordinates)
                object_coordinates[2] += 0.1
                print(f"obj coord: {object_coordinates}")

                self.cntl.move_to_position(generate_pose(tuple(object_coordinates)))
                self.cntl.close_gripper()
                print(f"Object {name} taken, reordering it")

                self.cntl.move_to_position(generate_pose((loc[0], loc[1], loc[2]+0.1, 3.1415, 0, -3.1415/4)))
                self.cntl.open_gripper() 
                print("Object placed, rip")

                self.cntl.move_to_rest()
                return True
            else:
                print(f"Object position detected are out of range, replace {name}")
                return False
        else:
            print(f"Can't remove {name}, object is still in the scene!")
            return False
        
    def test(self,name):
        '''
        Input: name of tool, destination_coordinates
        '''
        self.cntl.open_gripper()
        loc = self.positions[name]
        self.cntl.move_to_position(generate_pose((loc[0], loc[1], loc[2]+0.1, 3.1415, 0, -3.1415/4)))
        self.cntl.close_gripper()
        self.cntl.move_to_rest()
        self.cntl.open_gripper() # ToDo: manage the interaction with the human



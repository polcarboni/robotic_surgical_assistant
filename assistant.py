from controls.create_world import World
from controls.control import Control, generate_pose
import time
import json
from tf.transformations import euler_from_quaternion

PI = 3.141592653589793

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
        print('------- Routine 1 -------')
        self.cntl.open_gripper()
        loc = self.positions[name]
        obj_loc = (loc[0], loc[1], loc[2]+0.1 , PI, 0, -PI/4)
        print("R1: Moving into : ", obj_loc)

        # Understand if destination coordinates are valid
        valid = self.cntl.move_group.plan(generate_pose(destination_coordinates))[0]
        if valid:
            tmp_obj = list(destination_coordinates[:3])
            tmp_obj[2]-=0.2
            self.world.insert_hand((tmp_obj))
            tmp_obj=None
            print("R1: Position planned and valid")
            self.cntl.move_to_position(generate_pose(obj_loc))
            print("R1: Position reached")

            self.cntl.close_gripper()
            print("R1: Object taken")

            self.cntl.move_to_position(generate_pose(destination_coordinates))
            time.sleep(2.5)
            self.world.remove_hand()
            self.cntl.open_gripper() # ToDo: manage the interaction with the human
            self.world.delete_tool(name)
            print("R1: Object delivered")

            self.cntl.move_to_rest()
            self.cntl.close_gripper()
            print('------- Routine 1 ended-------')
            return True
        else:
            print("R1: Position not valid")
            print('------- Routine 1 ended-------')
            return False


    def routine_2(self, name, object_coordinates):
        '''
        Input: name of the object and its position and orientatio 
        '''
        if name not in self.world.names:
            print('------- Routine 2 -------')
            object_coordinates = list(object_coordinates)
            object_coordinates[2] = 0.87 # ensure that the object is over the tray

            pos = object_coordinates[:3]    #xyz of the object

            #compute orientation, assume that if the len is 6, then the orientation is euler
            if len(object_coordinates) == 7:
                orientation = list(euler_from_quaternion(object_coordinates[3:]))
            else:
                orientation = object_coordinates[3:]

            # put together position and orientation
            robot_coordinates = pos + orientation

            assert len(robot_coordinates) == 6


            # push the orientation of the robot to the ones which can actually grasp the object
            robot_coordinates[2]+=0.1
            robot_coordinates[3] = PI
            robot_coordinates[4] = 0
            robot_coordinates[5] = robot_coordinates[5]  - PI/4
            valid = self.cntl.move_group.plan(generate_pose(robot_coordinates))[0] #!!!!
            if valid:
                print("Valid goal position.")
                
                self.world.insert_tool(name, object_coordinates)

                self.cntl.open_gripper()
                loc = self.positions[name]
                
                print(" Moving into: ",robot_coordinates)

                self.cntl.move_to_position(generate_pose(tuple(robot_coordinates)))
                self.cntl.close_gripper()
                print(f"Object {name} taken, reordering it")

                self.cntl.move_to_position(generate_pose((loc[0], loc[1], loc[2]+0.1, PI, 0, -PI/4)))
                
                self.cntl.open_gripper() 
                print("Object placed, rip")

                self.world.delete_tool(name)
                time.sleep(1)
                self.world.insert_tool(name, tuple(self.positions[name]))                

                self.cntl.move_to_rest()
                print('------- Routine 2 ended -------')
                return True
            else:
                print(f"Object position detected are out of range, replace {name}")
                print('------- Routine 2 ended -------')

                return False
        else:
            print(f"Can't remove {name}, object is still in the scene!")
            print('------- Routine 2 ended-------')

            return False
        
    def test(self,name):
        '''
        Input: name of tool, destination_coordinates
        '''
        self.cntl.open_gripper()
        loc = self.positions[name]
        self.cntl.move_to_position(generate_pose((loc[0], loc[1], loc[2]+0.1, PI, 0, -PI/4)))
        self.cntl.close_gripper()
        self.cntl.move_to_rest()
        self.cntl.open_gripper() # ToDo: manage the interaction with the human



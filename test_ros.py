from control.create_world import World
from control.control import Control, generate_pose
import time
objects = ["table","table2","human","start_tray","end_tray", "lanchet", "tool2","tool3"]
world = World(objects)

cntl = Control(world.get_controllers() )
print(cntl.get_current_position())
print(cntl.get_current_conf())
time.sleep(5)
cntl.move_to_rest()
cntl.open_gripper()
input("Press enter for next step")

cntl.move_to_position(generate_pose(0,-0.5,0.97, 3.1415,0,-3.1415/4))
input("Press enter for next step")

cntl.close_gripper()
input("Press enter for next step")

cntl.move_to_rest()
input("Press enter for finish")


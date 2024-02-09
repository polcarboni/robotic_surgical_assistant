from controls.create_world import World
from controls.control import Control, generate_pose
import time
import json



objects = ["start_tray","end_tray","pinza_box", "cucchiaio_box" ]
world = World()
with open("/home/leo/robotic_surgical_assistant/controls/object_positions.json", "r") as f:
	positions = json.load(f)

for obj in objects:
	world.insert_tool(obj, tuple(positions[obj]))

'''

cntl = Control(world.get_controllers() )
print(cntl.get_current_position())
print(cntl.get_current_conf())
time.sleep(5)
cntl.move_to_rest()
cntl.open_gripper()
cntl.move_to_position(generate_pose(0,-0.5,0.97, 3.1415,0,-3.1415/4))
cntl.close_gripper()

cntl.move_to_rest()

'''
if __name__ == '__main__':
	main()
import franka_gripper.msg
import actionlib
from tf.transformations import quaternion_from_euler
import geometry_msgs.msg

class Control:
    def __init__(self, world):
        self.robot = world[0]
        self.move_group = world[1]
        self.scene = world[2]
        self.traj_pub = world[3]
    
    def get_current_position(self):
        return self.move_group.get_current_pose().pose.position

    def get_current_conf(self):
        return self.robot.get_current_state().joint_state.position

    def move_to_position(self, pose):
        """ [x, y, z, rot_x, rot_y, rot_z] or a list of 7 floats [x, y, z, qx, qy, qz, qw] """

        self.move_group.set_pose_target(pose)
        self.move_group.go(wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()

    def move_to_rest(self):
        q = (-0.00016272923401494666, -0.7856324561972281, 2.086219991515037e-05, -2.355962075525751, 9.053475886311446e-06, 1.5717530416926113, 0.7854065868959381, 0.0009982510310871334, 0.0009982510310871334)
        self.move_to_config(q)
    
    
    def open_gripper(self):
        client = actionlib.SimpleActionClient('/franka_gripper/move', franka_gripper.msg.MoveAction)
        client.wait_for_server()

        goal = franka_gripper.msg.MoveGoal()
        goal.width = 0.06
        goal.speed = 0.3

        client.send_goal(goal)
        client.wait_for_result()
        return client.get_result()

    def close_gripper(self):
        client = actionlib.SimpleActionClient('/franka_gripper/grasp', franka_gripper.msg.GraspAction)
        client.wait_for_server()

        goal = franka_gripper.msg.GraspGoal()
        goal.width = 0.03
        goal.epsilon.inner = 0.04
        goal.epsilon.outer = 0.04
        goal.speed = 0.1
        goal.force = 10

        client.send_goal(goal)
        client.wait_for_result()
        return client.get_result()
    
    def move_to_config(self, q):
        joint_goal = self.move_group.get_current_joint_values()
        joint_goal[0] = q[0]
        joint_goal[1] = q[1]
        joint_goal[2] = q[2]
        joint_goal[3] = q[3]
        joint_goal[4] = q[4]
        joint_goal[5] = q[5]

        self.move_group.go(joint_goal, wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()

def generate_pose(x, y, z, rx, py, yz):
    # Converts coordinates + RPY in Pose
    # x, y, z coordinted referred to world RF
    # rx, py, yz rotation angle (in radiants) as roll, pith and yaw on x,y,z

    pose = geometry_msgs.msg.Pose()

    pose.position.x = x
    pose.position.y = y
    pose.position.z = z

    quat = quaternion_from_euler(rx, py, yz)
    pose.orientation.x = quat[0]
    pose.orientation.y = quat[1]
    pose.orientation.z = quat[2]
    pose.orientation.w = quat[3]

    return pose
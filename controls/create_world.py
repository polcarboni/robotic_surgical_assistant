import rospy
import geometry_msgs
import moveit_commander
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState, SpawnModel, DeleteModel
from geometry_msgs.msg import Pose
import sys
import moveit_msgs
import re
from tf.transformations import quaternion_from_euler



class World:
    def __init__(self):
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('python_control_node', anonymous=True)

        self.robot = moveit_commander.RobotCommander()
        self.move_group = moveit_commander.MoveGroupCommander("panda_arm")
        self.scene = moveit_commander.PlanningSceneInterface()
        self.traj_pub = rospy.Publisher('/move_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=20)
        self.table_height = 0.83
        self.names = ["table","table2","human"]
        self.base_position = dict()
        self.number_instances = 0
        for name in self.names:

            self._insert_obj(name)
            self._add_scene_box(name)
        print("World created!")

    def get_controllers(self):
        return (self.robot, self.move_group, self.scene, self.traj_pub)

    def _add_scene_box(self, name):
        
        model_xml = open(f"/home/leo/robotic_surgical_assistant/prj_urdf/{name}.sdf", 'r').read()
        size = tuple([float(x) for x in model_xml[model_xml.find("<size>")+6:model_xml.find("</size>")].split()])

        position = tuple([float(x) for x in model_xml[model_xml.find("<pose>")+6:model_xml.find("</pose>")].split()])
        print(position)
        box_pose = geometry_msgs.msg.PoseStamped()
        box_pose.header.frame_id = "world"
        box_pose.pose.orientation.w = 1.0
        box_pose.pose.position.x = position[0]
        box_pose.pose.position.y = position[1]
        box_pose.pose.position.z = position[2]
        box_name = name
        self.scene.add_box(box_name, box_pose, size=size)
        
    def _insert_obj(self,name, pose = (0,0,0), w=1):
        spawn_model_client = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
        model_xml = open(f"/home/leo/robotic_surgical_assistant/prj_urdf/{name}.sdf", 'r').read()
        
        pos = Pose()
        pos.position.x = pose[0]
        pos.position.y = pose[1]
        pos.position.z = pose[2]
        pos.orientation.w = w

        spawn_model_client(model_name=name, model_xml=model_xml, initial_pose=pos, reference_frame="world")

    def _delete_obj(self, name:str):
        self.names.remove(name)
        return rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)(name)

    def insert_tool(self, name, pose_param = (0,0,0,1.0,0,0,0)):

        spawn_model_client = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
        model_xml = open(f"/home/leo/robotic_surgical_assistant/prj_urdf/{name}.sdf", 'r').read()

        size = tuple([float(x) for x in model_xml[model_xml.find("<size>")+6:model_xml.find("</size>")].split()])

        self.names.append(name)
        box_pose = geometry_msgs.msg.PoseStamped()
        box_pose.header.frame_id = "world"

        pose_in = pose_param[:3]
        quaternion = pose_param[3:]
        
        if len(pose_param) == 7:
            quaternion = pose_param[3:]
        elif len(pose_param)==6:
            quaternion = quaternion_from_euler(pose_param[3],pose_param[4],pose_param[5])
        else:
            quaternion = (0.,0.,0.,1.)
        
        box_pose.pose.orientation.x = quaternion[0]
        box_pose.pose.orientation.y = quaternion[1]
        box_pose.pose.orientation.z = quaternion[2]
        box_pose.pose.orientation.w = quaternion[3]

        box_pose.pose.position.x = pose_in[0]
        box_pose.pose.position.y = pose_in[1]
        box_pose.pose.position.z = pose_in[2]

        

        pos = Pose()
        pos.position.x = pose_in[0]
        pos.position.y = pose_in[1]
        pos.position.z = pose_in[2]

        pos.orientation.x = quaternion[0]
        pos.orientation.y = quaternion[1]
        pos.orientation.z = quaternion[2]
        pos.orientation.w = quaternion[3]


        self.scene.add_box(name, box_pose, size=size)
        spawn_model_client(model_name=name, model_xml=model_xml, initial_pose=pos, reference_frame="world")
        self.number_instances += 1
     
    
    def delete_tool(self, name:str):
        self.names.remove(name)
        self.number_instances -= 1
        self.scene.remove_world_object(name)
        return rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)(name)

    def insert_hand(self,pose_in=(0,0,0)):
        spawn_model_client = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
        model_xml = open(f"/home/leo/robotic_surgical_assistant/prj_urdf/hand_box.sdf", 'r').read()

        pos = Pose()

        pos.orientation.w = 1.0

        pos.position.x = pose_in[0]
        pos.position.y = pose_in[1]
        pos.position.z = pose_in[2]



        spawn_model_client(model_name="sphere_hand", model_xml=model_xml, initial_pose=pos, reference_frame="world")
    
    def remove_hand(self):
        return rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)("sphere_hand")
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from tf2_ros import TransformListener, Buffer
import tf_transformations
import random
import math

class PayloadVisualizer(Node):
    def __init__(self):
        super().__init__('payload_visualizer')

        # Initializes marker publisher for RViz
        self.publisher = self.createpublisher(Marker, '/visualization_marker', 10)

        # Buffer and listener to get the frames transformation
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Robot parameter (examples)
        self.links = ["arm_link_0", "arm_link_1", "arm_link_2","arm_link_3", "arm_link_4"]
        self.mass_distribution = [8, 6, 5, 3, 2] # kg for every link
        self.max_joint_torque = [80, 70, 60, 50, 40] # Nm for every link

        # Timer to update the visualization every 0.5 seconds
        self.timer = self.create_timer(0.5, self.timer_callback)
    
    def timer_callback(self):
        for i, link in enumerate(self.links):
            try:
                # Obtain the transformation of the link 
                now = rclpy.time.Time()
                transform = self.tf_buffer.lookup_transform('base_footprint', link, now)

                # Kinematic and dynamic calculations
                position = transform.transform.translation
                distance = math.sqrt(position.x**2 + position.y**2 + position.z**2) + 0.01 # distance from center
                joint_velocity = random.uniform(0.1, 1.5)
                joint_acceleration = random.uniform(0.1, 3.0)

                ### Useful Payload Calculation ###
                # Max load = τ_max / (r * a_eff)
                # a_eff = g + joint_acceleration

                a_eff = 9.81 + joint_acceleration
                torque = self.max_joint_torque[i]
                payload = torque / (distance * a_eff)
                payload = max(0.0, min(payload, 20.0))    # limitations for security reasons

                # Heatmap and number publication
                self.publish_marker(link, i, payload)    # heatmap
                self.publish_text(link, i, payload)   # number

            except Exception as e:
                self.get_logger().warn(f"Tf error for {link}: {e}")
    
    def publish_marker(self, frame, idx, payload):
        # Heatmap sphere marker
        marker = Marker()
        marker.header.frame_id = frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "payload_heatmap"
        marker.id = idx
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.pose.orientation.z = 0.05
        marker.scale.x = 0.1
        marker.scale.y = 0.1
        marker.scale.z = 0.1

        # Color scheme (green = low payload, red = high payload)
        normalized = min(payload/20.0, 1.0)
        marker.color.r = 1.0 - normalized
        marker.color.g = normalized
        marker.color.b = 0.0
        marker.color.a = 0.85

        self.publisher.publish(marker)

    def publish_text(self, frame, idx, payload):
        # Text marker for numerical indications
        marker = Marker()
        marker.header.frame_id = frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "payload_text"
        marker.id = idx + 100
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.pose.position.z = 0.2
        marker.scale.z = 0.08
        marker.color.r = 1.0
        marker.color.g = 1.0
        marker.color.b = 1.0
        marker.color.a = 1.0
        marker.text = f"{payload: .2f} kg"

        self.publisher.publish(marker)

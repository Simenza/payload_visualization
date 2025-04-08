from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    xacro_file = os.path.join(
        get_package_share_directory('tiago_description'),
        'robots',
        'tiago.urdf.xacro'
    )

    robot_description_config = xacro.process_file(xacro_file)
    robot_description = robot_description_config.toxml()


    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        )
    ])
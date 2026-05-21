from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar',
            output='screen',
            parameters=[
                {'serial_port': '/dev/ttyUSB0'},
                {'frame_id': 'laser'}
            ]
        )
    ])

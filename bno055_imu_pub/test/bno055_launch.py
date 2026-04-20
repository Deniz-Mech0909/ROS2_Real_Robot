from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='bno055_imu_pub',
            executable='bno055_node',
            name='bno055_node',
            output='screen',
        ),
        Node(
            package='bno055_imu_pub',
            executable='tf_broadcaster',
            name='tf_broadcaster',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', '/home/pios/ros2_ws/src/bno055_imu_pub/config/bno055_imu.rviz'],
            output='screen',
        )
    ])

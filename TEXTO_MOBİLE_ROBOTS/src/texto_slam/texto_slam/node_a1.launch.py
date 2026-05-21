from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable

def generate_launch_description():
    # Xacro dosyasına tam yol (ament index’e ihtiyaç yok)
    xacro_file = "/home/pios/ros2_ws/src/texto_mobil_description/urdf/texto_mobil.urdf.xacro"

    robot_description = Command([
        FindExecutable(name="xacro"),
        " ",
        xacro_file
    ])

    return LaunchDescription([
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 115200,
                'frame_id': 'laser',
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Standard',
                'topic_name': 'scan',
                'channel_type': 'serial',
                'queue_size': 10
            }]
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'publish_frequency': 50.0},
                {'use_sim_time': False}
            ]
        )
    ])

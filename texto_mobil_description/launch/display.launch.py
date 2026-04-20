from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Xacro dosyasının yolu
    urdf_file = PathJoinSubstitution([
        FindPackageShare("texto_mobil_description"),
        "urdf",
        "texto_mobil.urdf.xacro"
    ])

    # robot_description parametresi (xacro çıktısı)
    robot_description = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        urdf_file
    ])

    return LaunchDescription([
        # robot_state_publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": robot_description
            }]
        ),

        # RViz2 (varsayılan olarak başlatılır, config dosyası eklenmediyse boş açılır)
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen"
        )
    ])

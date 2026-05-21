from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # --- Launch args ---
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    serial_port = LaunchConfiguration('serial_port')
    odom_publish_tf = LaunchConfiguration('odom_publish_tf')
    debug_raw = LaunchConfiguration('debug_raw')

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=PathJoinSubstitution([FindPackageShare('texto_nav2'), 'maps', 'my_map.yaml']),
        description='Yüklenecek harita YAML dosyası'
    )

    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=PathJoinSubstitution([FindPackageShare('texto_nav2'), 'config', 'nav2_params.yaml']),
        description='Nav2 params.yaml'
    )

    declare_serial = DeclareLaunchArgument(
        'serial_port',
        default_value=TextSubstitution(text='/dev/ttyUSB1'),
        description='Encoder odom için seri port'
    )

    declare_publish_tf = DeclareLaunchArgument(
        'odom_publish_tf',
        default_value=TextSubstitution(text='false'),
        description='encoder_odom_node odom->base_link TF yayınlasın mı? (ekf yayınlıyorsa false)'
    )

    declare_debug_raw = DeclareLaunchArgument(
        'debug_raw',
        default_value=TextSubstitution(text='true'),
        description='encoder_odom_node raw seri satırlarını logla'
    )

    # --- Sensors / local TF ---
    bno055 = Node(
        package='texto_nav2',
        executable='bno055_node',
        name='bno055_node',
        output='screen',
        emulate_tty=True
    )

    encoder_odom = Node(
        package='texto_nav2',
        executable='encoder_odom_node',
        name='encoder_odom_node',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'port': serial_port,
            'publish_tf': odom_publish_tf,
            'debug_raw': debug_raw,
            # teker ve taban geometrini istersen buradan da override edebilirsin:
            # 'R': 0.04,
            # 'LX': 0.16,
            # 'LY': 0.195,
            # 'cpr_wheel': 1985,
            # 'frame_id_odom': 'odom',
            # 'frame_id_base': 'base_link',
        }]
    )

    imu_tf = Node(
        package='texto_nav2',
        executable='tf_broadcaster',
        name='tf_broadcaster',
        output='screen',
        emulate_tty=True
    )

    # --- Nav2 core ---
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        emulate_tty=True,
        parameters=[{'yaml_filename': map_yaml}]
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    planner = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    controller = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    behavior = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    bt_nav = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    waypoint = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        emulate_tty=True,
        parameters=[params_file]
    )

    lifecycle = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        emulate_tty=True,
        parameters=[{
            'use_sim_time': False,
            'autostart': True,
            'node_names': [
                'map_server','amcl','controller_server',
                'planner_server','behavior_server',
                'bt_navigator','waypoint_follower'
            ]
        }]
    )

    return LaunchDescription([
        declare_map, declare_params, declare_serial, declare_publish_tf, declare_debug_raw,
        # sensors first
        bno055, encoder_odom, imu_tf,
        # then nav2 stack
        map_server, amcl, planner, controller, behavior, bt_nav, waypoint, lifecycle
    ])

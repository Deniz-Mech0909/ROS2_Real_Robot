from setuptools import setup

package_name = 'bno055_imu_pub'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pios',
    maintainer_email='pios@example.com',
    description='BNO055 IMU ROS 2 Publisher with QoS',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bno055_node = bno055_imu_pub.bno055_node:main',
            'tf_broadcaster = bno055_imu_pub.tf_broadcaster:main',
            'fake_odom_node = bno055_imu_pub.fake_odom_node:main',
            'laser_tf_broadcaster = bno055_imu_pub.laser_tf_broadcaster:main',
            
        ],
    },
)

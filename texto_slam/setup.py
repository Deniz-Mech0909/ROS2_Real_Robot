from setuptools import setup
import os
from glob import glob

package_name = 'texto_slam'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # launch dosyasını dahil ediyoruz
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pios',
    maintainer_email='pios@todo.todo',
    description='SLAM + IMU + LiDAR entegrasyonu için ROS2 paketi',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bno055_node = texto_slam.bno055_node:main',
            'tf_broadcaster = texto_slam.tf_broadcaster:main',
            'fake_odom_node = texto_slam.fake_odom_node:main',
            'laser_tf_broadcaster = texto_slam.laser_tf_broadcaster:main',
        ],
    },
)

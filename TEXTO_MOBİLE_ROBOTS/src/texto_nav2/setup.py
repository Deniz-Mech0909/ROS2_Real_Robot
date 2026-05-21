from setuptools import setup
import os
from glob import glob

package_name = 'texto_nav2'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name, package_name + '.scripts'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'maps'),   glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pios',
    maintainer_email='pios@todo.todo',
    description='Nav2 bringup + AMCL + configs',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'encoder_odom_node = texto_nav2.scripts.encoder_odom_node:main',
            'bno055_node = texto_nav2.scripts.bno055_node:main',
            'tf_broadcaster = texto_nav2.scripts.tf_broadcaster:main',
        ],
    },
)

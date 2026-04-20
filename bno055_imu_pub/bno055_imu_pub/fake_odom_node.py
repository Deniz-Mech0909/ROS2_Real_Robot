import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion, TransformStamped
import tf_transformations
import tf2_ros
import math

class OdomNode(Node):
    def __init__(self):
        super().__init__('filtered_odom_node')

        self.subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.br = tf2_ros.TransformBroadcaster(self)

        self.last_time = self.get_clock().now()
        self.th = 0.0  # sadece yaw
        self.x = 0.0
        self.y = 0.0

    def imu_callback(self, msg):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9  # saniyeye çevir

        # Yalnızca z-ekseni açısal hızı al (yaw)
        wz = msg.angular_velocity.z
        self.th += wz * dt  # yaw güncelle

        # Lineer pozisyonu sabit tut veya küçük hareket ekle
        # İsteğe bağlı: self.x += math.cos(self.th) * hız * dt gibi genişletilebilir

        odom_msg = Odometry()
        odom_msg.header.stamp = now.to_msg()
        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id = "base_link"

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0

        odom_quat = tf_transformations.quaternion_from_euler(0, 0, self.th)
        odom_msg.pose.pose.orientation = Quaternion(
            x=odom_quat[0],
            y=odom_quat[1],
            z=odom_quat[2],
            w=odom_quat[3]
        )

        # Sabit lineer hız (0), sadece dönüş bildiriliyor
        odom_msg.twist.twist.linear.x = 0.0
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.angular.z = wz

        self.odom_pub.publish(odom_msg)

        # TF yayınla
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation = odom_msg.pose.pose.orientation

        self.br.sendTransform(t)

        self.last_time = now

def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

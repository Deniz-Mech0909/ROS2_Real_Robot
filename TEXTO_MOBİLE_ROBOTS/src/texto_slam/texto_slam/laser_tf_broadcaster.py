import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import tf_transformations  # İleride dönüşlü TF gerekiyorsa hazırda olsun

class LaserTFBroadcaster(Node):
    def __init__(self):
        super().__init__('laser_tf_broadcaster')
        self.broadcaster = TransformBroadcaster(self)

        # 10 Hz yayın (0.1 saniye)
        self.timer = self.create_timer(0.1, self.broadcast)

    def broadcast(self):
        now = self.get_clock().now().to_msg()

        t = TransformStamped()
        t.header.stamp = now  # ⬅️ Zaman damgası çok önemli
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'laser'

        # Lazerin konumu: 10 cm yukarıda
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.1

        # Dönüş yok (quat = [0, 0, 0, 1])
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # Yayınla
        self.broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = LaserTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

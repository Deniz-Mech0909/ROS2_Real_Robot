import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

class IMUTFBroadcaster(Node):
    def __init__(self):
        super().__init__('imu_tf_broadcaster')

        # 🔧 QoS ayarları: RELIABLE & KEEP_LAST
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )

        # 🔁 Transform yayıncısı
        self.br = TransformBroadcaster(self, qos)

        # 🔁 Timer ile periyodik yayın (10 Hz)
        self.timer = self.create_timer(0.1, self.broadcast_tf)

    def broadcast_tf(self):
        # 🧭 IMU'nun base_link'e göre konumu
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'imu_link'

        # IMU, robot üzerinde hafif yukarıda konumlanmış gibi (örnek)
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.1

        # Yönelim (sabit)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        # 📤 Yayınla
        self.br.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = IMUTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

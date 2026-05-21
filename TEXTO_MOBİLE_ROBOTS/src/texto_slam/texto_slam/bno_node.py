import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import Imu
import board
import busio
import adafruit_bno055
import math

class BNO055IMUNode(Node):
    def __init__(self):
        super().__init__('bno055_imu_node')

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bno055.BNO055_I2C(i2c)
            self.sensor.mode = adafruit_bno055.NDOF_MODE
            self.get_logger().info("✅ BNO055 bağlantısı başarılı.")
        except Exception as e:
            self.get_logger().error(f"❌ BNO055 bağlantı hatası: {e}")
            self.sensor = None
            return

        qos = QoSProfile(depth=50)
        self.publisher_ = self.create_publisher(Imu, '/imu/data', qos)
        self.timer = self.create_timer(0.01, self.publish_imu_data)

    def publish_imu_data(self):
        if self.sensor is None:
            return

        # Orientation verisi (Euler → Quaternion)
        euler = self.sensor.euler
        if euler is None or None in euler:
            self.get_logger().warn("⚠️ Euler verisi okunamadı.")
            return
        roll, pitch, yaw = [math.radians(v) for v in euler]

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        qw = cr * cp * cy + sr * sp * sy

        # Angular velocity
        gyro = self.sensor.gyro
        if gyro is None or None in gyro:
            self.get_logger().warn("⚠️ Gyro verisi okunamadı.")
            return
        gx, gy, gz = gyro  # rad/s

        # Linear acceleration (gravity çıkarılmış)
        accel = self.sensor.linear_acceleration
        if accel is None or None in accel:
            self.get_logger().warn("⚠️ Linear acceleration verisi okunamadı.")
            return
        ax, ay, az = accel

        # IMU mesajı oluştur
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'

        msg.orientation.x = qx
        msg.orientation.y = qy
        msg.orientation.z = qz
        msg.orientation.w = qw

        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        # Covariances
        msg.orientation_covariance = [0.01, 0.0, 0.0,
                                      0.0, 0.01, 0.0,
                                      0.0, 0.0, 0.01]
        msg.angular_velocity_covariance = [0.02, 0.0, 0.0,
                                           0.0, 0.02, 0.0,
                                           0.0, 0.0, 0.02]
        msg.linear_acceleration_covariance = [0.1, 0.0, 0.0,
                                              0.0, 0.1, 0.0,
                                              0.0, 0.0, 0.1]

        self.publisher_.publish(msg)
        self.get_logger().info("📤 IMU verisi yayınlandı.")

def main(args=None):
    rclpy.init(args=args)
    node = BNO055IMUNode()
    if node.sensor is not None:
        rclpy.spin(node)
        node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

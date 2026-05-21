#!/usr/bin/env python3
import math, re, time
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class EncoderOdomNode(Node):
    def __init__(self):
        super().__init__('encoder_odom_node')
        self.get_logger().info("encoder_odom_node starting…")

        # ---- Parametreler ----
        self.declare_parameter('port', '/dev/ttyUSB1')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('R', 0.04)
        self.declare_parameter('LX', 0.16)
        self.declare_parameter('LY', 0.195)
        self.declare_parameter('cpr_wheel', 1985)
        self.declare_parameter('frame_id_odom', 'odom')
        self.declare_parameter('frame_id_base', 'base_link')
        self.declare_parameter('publish_tf', False)
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('debug_raw', True)

        self.port = self.get_parameter('port').value
        self.baud = int(self.get_parameter('baud').value)
        self.R = float(self.get_parameter('R').value)
        self.LX = float(self.get_parameter('LX').value)
        self.LY = float(self.get_parameter('LY').value)
        self.A = self.LX + self.LY
        self.CPR = int(self.get_parameter('cpr_wheel').value)
        self.frame_odom = self.get_parameter('frame_id_odom').value
        self.frame_base = self.get_parameter('frame_id_base').value
        self.publish_tf = bool(self.get_parameter('publish_tf').value)
        self.odom_topic = self.get_parameter('odom_topic').value
        self.debug_raw = bool(self.get_parameter('debug_raw').value)

        self.odom_pub = self.create_publisher(Odometry, self.odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.line_re = re.compile(
            r"Sağ\s*Ön:\s*(-?\d+)\s+Sol\s*Ön:\s*(-?\d+)\s+Sağ\s*Arka:\s*(-?\d+)\s+Sol\s*Arka:\s*(-?\d+)",
            re.IGNORECASE
        )

        self.x = 0.0; self.y = 0.0; self.theta = 0.0
        self.prev_ticks = None; self.prev_t = None
        self.ser = None

        # Seri portu devreye almayı deneyen timer
        self.serial_timer = self.create_timer(1.0, self._ensure_serial)
        # Ana döngü
        self.timer = self.create_timer(0.005, self.loop_once)  # 200 Hz

    def _ensure_serial(self):
        if self.ser and self.ser.is_open:
            return
        try:
            import serial  # lazy import
            self.ser = serial.Serial(self.port, self.baud, timeout=0.01)
            time.sleep(0.2)
            self.get_logger().info(f'✅ Serial opened: {self.port} @ {self.baud}')
        except Exception as e:
            self.get_logger().warn(f'⚠️ Serial not ready ({self.port}): {e}')

    def wheel_linear_delta(self, dticks: int) -> float:
        return (2.0 * math.pi * self.R) * (dticks / self.CPR)

    def loop_once(self):
        if not (self.ser and self.ser.is_open):
            return
        try:
            raw = self.ser.readline().decode('utf-8', errors='ignore').strip()
        except Exception as e:
            self.get_logger().warn(f'serial read error: {e}')
            return

        if not raw:
            return
        if self.debug_raw:
            self.get_logger().info(f'RAW: {raw}')

        nums = re.findall(r'-?\d+', raw)
        if len(nums) >= 4:
            SagOn, SolOn, SagArka, SolArka = map(int, nums[:4])
        else:
            m = self.line_re.search(raw)
            if not m:
                return
            SagOn, SolOn, SagArka, SolArka = (int(m.group(i)) for i in range(1, 5))

        now = self.get_clock().now().nanoseconds * 1e-9
        if self.prev_ticks is None:
            self.prev_ticks = (SagOn, SolOn, SagArka, SolArka)
            self.prev_t = now
            self.get_logger().info('First sample received, waiting next to compute delta…')
            return

        dt = max(1e-6, now - self.prev_t)
        dSagOn   = SagOn   - self.prev_ticks[0]
        dSolOn   = SolOn   - self.prev_ticks[1]
        dSagArka = SagArka - self.prev_ticks[2]
        dSolArka = SolArka - self.prev_ticks[3]

        ds_LF = self.wheel_linear_delta(dSolOn)
        ds_RF = self.wheel_linear_delta(dSagOn)
        ds_LR = self.wheel_linear_delta(dSolArka)
        ds_RR = self.wheel_linear_delta(dSagArka)

        w_LF = (ds_LF / self.R) / dt
        w_RF = (ds_RF / self.R) / dt
        w_LR = (ds_LR / self.R) / dt
        w_RR = (ds_RR / self.R) / dt

        vx = (self.R / 4.0) * (w_LF + w_RF + w_LR + w_RR)
        vy = (self.R / 4.0) * (-w_LF + w_RF + w_LR - w_RR)
        wz = (self.R / (4.0 * self.A)) * (-w_LF + w_RF - w_LR + w_RR)

        self.x += (vx * math.cos(self.theta) - vy * math.sin(self.theta)) * dt
        self.y += (vx * math.sin(self.theta) + vy * math.cos(self.theta)) * dt
        self.theta += wz * dt

        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = self.frame_odom
            t.child_frame_id = self.frame_base
            t.transform.translation.x = float(self.x)
            t.transform.translation.y = float(self.y)
            t.transform.translation.z = 0.0
            t.transform.rotation.z = math.sin(self.theta * 0.5)
            t.transform.rotation.w = math.cos(self.theta * 0.5)
            self.tf_broadcaster.sendTransform(t)

        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = self.frame_odom
        odom.child_frame_id = self.frame_base
        odom.pose.pose.position.x = float(self.x)
        odom.pose.pose.position.y = float(self.y)
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.z = math.sin(self.theta * 0.5)
        odom.pose.pose.orientation.w = math.cos(self.theta * 0.5)

        odom.pose.covariance = [0.05,0,0,0,0,0,
                                0,0.05,0,0,0,0,
                                0,0,999,0,0,0,
                                0,0,0,999,0,0,
                                0,0,0,0,999,0,
                                0,0,0,0,0,0.1]
        odom.twist.twist.linear.x = float(vx)
        odom.twist.twist.linear.y = float(vy)
        odom.twist.twist.angular.z = float(wz)
        odom.twist.covariance = [0.1,0,0,0,0,0,
                                 0,0.1,0,0,0,0,
                                 0,0,999,0,0,0,
                                 0,0,0,999,0,0,
                                 0,0,0,0,999,0,
                                 0,0,0,0,0,0.1]
        self.odom_pub.publish(odom)

        self.prev_ticks = (SagOn, SolOn, SagArka, SolArka)
        self.prev_t = now

def main():
    rclpy.init()
    node = EncoderOdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if getattr(node, 'ser', None) and node.ser.is_open:
                node.ser.close()
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

import time
import board
import busio
import adafruit_bno055

# 🔌 I2C başlat
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bno055.BNO055_I2C(i2c)
except Exception as e:
    print(f"❌ BNO055 bağlantı hatası: {e}")
    exit(1)

# 🔁 Sürekli veri yazdır
while True:
    print("Euler Angles (Heading, Roll, Pitch):", sensor.euler)
    print("Gyroscope (X, Y, Z):", sensor.gyro)
    print("Accelerometer (X, Y, Z):", sensor.acceleration)
    print("Linear Acceleration (X, Y, Z):", sensor.linear_acceleration)
    print("Gravity (X, Y, Z):", sensor.gravity)
    print("Temperature: {} °C".format(sensor.temperature))
    print("-" * 50)
    time.sleep(2)

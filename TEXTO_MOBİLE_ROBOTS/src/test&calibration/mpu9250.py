from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import board
import adafruit_bmp280
import time
import busio

# MPU9255 Başlat (0x68 adresinde)
mpu = MPU9250(
    address_ak=AK8963_ADDRESS,          # Manyetometre
    address_mpu_master=MPU9050_ADDRESS_68,  # 0x68
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_250, afs=AFS_2G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ
)

mpu.configure()  # Kalibrasyon yaptıysan gerek yok
# mpu.calibrate()  # ilk sefer için önerilir, sonra yorum satırı yap

# BMP280 başlat (0x77 adresinde)
i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)

bmp280.sea_level_pressure = 1013.25  # Opsiyonel

print("Veriler geliyor...\n")

while True:
    ax, ay, az = mpu.readAccelerometerMaster()
    gx, gy, gz = mpu.readGyroscopeMaster()
    mx, my, mz = mpu.readMagnetometerMaster()

    print(f"Accel: X={ax:.2f}g  Y={ay:.2f}g  Z={az:.2f}g")
    print(f"Gyro : X={gx:.2f}°/s  Y={gy:.2f}°/s  Z={gz:.2f}°/s")
    print(f"Mag  : X={mx:.2f}µT  Y={my:.2f}µT  Z={mz:.2f}µT")
    print(f"Temp : {bmp280.temperature:.2f} °C")
    print(f"Pres : {bmp280.pressure:.2f} hPa")
    print("-" * 40)

    time.sleep(4.0)

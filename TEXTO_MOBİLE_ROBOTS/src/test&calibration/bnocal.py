import time
import board
import busio
import adafruit_bno055

# I2C başlat
i2c = busio.I2C(board.SCL, board.SDA)

# BNO055 sensörünü başlat (I2C adresi: 0x28 default)
sensor = adafruit_bno055.BNO055_I2C(i2c)

# Kalibrasyon seviyesini gösteren fonksiyon
def get_calib_status():
    sys, gyro, accel, mag = sensor.calibration_status
    print(f"CALIBRATION STATUS -> SYS:{sys} | GYRO:{gyro} | ACCEL:{accel} | MAG:{mag}")
    if sys < 3:
        print("⚠️ Kalibrasyon tam değil! Sensörü hareket ettir...")
    else:
        print("✅ Tüm sistem tam kalibre!")

# Ana döngü
while True:
    try:
        get_calib_status()

        euler = sensor.euler
        if euler is not None:
            print("Euler (Yaw, Pitch, Roll):", euler)
        else:
            print("Euler verisi alınamadı.")

        accel = sensor.acceleration
        if accel is not None:
            print("İvme (X, Y, Z):", accel)
        else:
            print("İvme verisi alınamadı.")

        print("-" * 50)
        time.sleep(1)

    except Exception as e:
        print("❌ Hata oluştu:", e)
        time.sleep(1)

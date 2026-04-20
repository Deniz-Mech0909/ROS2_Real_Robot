#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)

motors = {
    "LF": {"IN1": 17, "IN2": 27, "EN": 18},  # Sol ön
    "RF": {"IN1": 22, "IN2": 23, "EN": 19},  # Sağ ön
    "LR": {"IN1": 5,  "IN2": 6,  "EN": 12},  # Sol arka
    "RR": {"IN1": 13, "IN2": 26, "EN": 16},  # Sağ arka
}

# --- Pin yönleri ayarla ---
for m in motors.values():
    GPIO.setup(m["IN1"], GPIO.OUT)
    GPIO.setup(m["IN2"], GPIO.OUT)
    GPIO.setup(m["EN"], GPIO.OUT)
    m["pwm"] = GPIO.PWM(m["EN"], 1000)  # 1 kHz PWM
    m["pwm"].start(0)

def set_motor(motor, speed):
    """speed: -1.0 ... +1.0"""
    if speed > 0:
        GPIO.output(motor["IN1"], GPIO.HIGH)
        GPIO.output(motor["IN2"], GPIO.LOW)
    elif speed < 0:
        GPIO.output(motor["IN1"], GPIO.LOW)
        GPIO.output(motor["IN2"], GPIO.HIGH)
    else:
        GPIO.output(motor["IN1"], GPIO.LOW)
        GPIO.output(motor["IN2"], GPIO.LOW)
    motor["pwm"].ChangeDutyCycle(min(abs(speed) * 100, 100))

def stop_all():
    for m in motors.values():
        set_motor(m, 0)

try:
    print("Motorlar ileri yönde 5 saniye çalışıyor...")
    for m in motors.values():
        set_motor(m, 0.8)  # %80 hızla ileri
    time.sleep(5)

except KeyboardInterrupt:
    print("Kullanıcı tarafından durduruldu.")

finally:
    print("Motorlar durduruluyor ve GPIO temizleniyor...")
    stop_all()
    GPIO.cleanup()

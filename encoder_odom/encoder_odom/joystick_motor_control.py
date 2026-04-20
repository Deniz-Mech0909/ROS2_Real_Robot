#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import pygame

# --- GPIO setup ---
GPIO.setwarnings(False)
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
    m["pwm"] = GPIO.PWM(m["EN"], 1000)  # 1kHz PWM
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

# --- Joystick setup ---
pygame.init()
pygame.joystick.init()

try:
    js = pygame.joystick.Joystick(0)
    js.init()
    print("🎮 Joystick bulundu:", js.get_name())
except pygame.error:
    print("⚠️ Joystick bulunamadı! Lütfen takın ve yeniden başlatın.")
    stop_all()
    GPIO.cleanup()
    pygame.quit()
    exit()

print("Başlatıldı. Çıkmak için Ctrl+C")

try:
    while True:
        pygame.event.pump()
        y = -js.get_axis(1)  # ileri/geri
        x = js.get_axis(0)   # sağ/sol

        # Tank sürüş karışımı
        left_speed  = y + x
        right_speed = y - x

        # normalize
        maxv = max(1.0, abs(left_speed), abs(right_speed))
        left_speed  /= maxv
        right_speed /= maxv

        # Motorlara uygula
        set_motor(motors["LF"], left_speed)
        set_motor(motors["LR"], left_speed)
        set_motor(motors["RF"], right_speed)
        set_motor(motors["RR"], right_speed)

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n🛑 Program sonlandırıldı.")
finally:
    stop_all()
    GPIO.cleanup()
    pygame.quit()
    print("✅ GPIO temizlendi ve çıkıldı.")

import RPi.GPIO as GPIO
import time
from MQTT import MQTTClient
import threading

# SET SERVO-MOTORS
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
pwm1 = GPIO.PWM(12, 50)
pwm2 = GPIO.PWM(13, 50)
pwm1.start(0)
pwm2.start(0)

# SET TARGETS
GPIO.setup(20, GPIO.IN)
GPIO.setup(16, GPIO.IN)

def set_position(servo, angle):
    duty_cycle = angle / 18.0 + 2.5
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)
    
def on_hit(servo):
    print("HIT")
    set_position(servo, 0)
    set_position(servo, 60)
    time.sleep(1)
    set_position(servo, 0)
    time.sleep(0.2)

mqtt_client = MQTTClient("localhost", 1883, "username", "password")
mqtt_client.connect()

last_activation_time_1 = 0
last_activation_time_2 = 0

try:
    while True:
        print("Waiting for start signal...")
        mqtt_client.subscribe("topic")
        points = 0
        game_length = 26
        countdown_time = 3
        t_end = time.time() + game_length
        while time.time() < t_end:
            if (t_end - game_length) + countdown_time > time.time():
                print("GAME IS COUNTING DOWN")
            else:
                print("GAME IS LIVE")
                target_one_hit = GPIO.input(20)
                target_two_hit = GPIO.input(16)

                if not target_one_hit and time.time() - last_activation_time_1 >= 3:
                    thread_pwm1 = threading.Thread(target=on_hit, args=(pwm1,))
                    thread_pwm1.start()
                    last_activation_time_1 = time.time()
                    points += 1
                    print("-----TARGET ONE HIT-----")

                elif not target_two_hit and time.time() - last_activation_time_2 >= 3:
                    thread_pwm2 = threading.Thread(target=on_hit, args=(pwm2,))
                    thread_pwm2.start()
                    last_activation_time_2 = time.time()
                    points += 1
                    print("-----TARGET TWO HIT-----")

        ## SET AND CONNECT TO MQTT, SEND POINTS
        mqtt_client = MQTTClient("localhost", 1883, "username", "password")
        mqtt_client.connect()
        mqtt_client.publish("topic", points)

        print("GAME FINISHED")

except KeyboardInterrupt:
    # Stop the PWM and clean up the GPIO pins
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()

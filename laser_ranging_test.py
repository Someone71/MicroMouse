import time
import sys
sys.path.insert(0, '/home/someone/Micromouse/VL53L0X_rasp_python/python')
import VL53L0X
import RPi.GPIO as GPIO

sensor1_shutdown = 20
sensor2_shutdown = 16
sensor3_shutdown = 21

tof1 = VL53L0X.VL53L0X(address=0x2B)
tof2 = VL53L0X.VL53L0X(address=0x2D)
tof3 = VL53L0X.VL53L0X(address=0x2E)

def setup():
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(sensor1_shutdown, GPIO.OUT)
	GPIO.setup(sensor2_shutdown, GPIO.OUT)
	GPIO.setup(sensor3_shutdown, GPIO.OUT)

	GPIO.output(sensor1_shutdown, GPIO.LOW)
	GPIO.output(sensor2_shutdown, GPIO.LOW)
	GPIO.output(sensor3_shutdown, GPIO.LOW)

	time.sleep(0.5)
	
	GPIO.output(sensor1_shutdown, GPIO.HIGH)
	time.sleep(0.5)
	tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

	GPIO.output(sensor2_shutdown, GPIO.HIGH)
	time.sleep(0.5)
	tof2.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
	
	GPIO.output(sensor3_shutdown, GPIO.HIGH)
	time.sleep(0.5)
	tof3.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
		
def loop():
	timing = tof1.get_timing()
	#print(timing)
	#time.sleep(2)
	if (timing < 20000):
		timing = 20000
	while True:
		distance1 = tof1.get_distance()
		print("1: " + str(distance1))
		time.sleep(0.5)
		
		# distance2 = tof2.get_distance()
		# print("2: " + str(distance2))
		# time.sleep(0.5)
		
		# distance3 = tof3.get_distance()
		# print("3: " + str(distance3))
		# time.sleep(0.5)
		
		time.sleep(timing/1000000.00)	
	
def destroy():
	tof1.stop_ranging()
	GPIO.output(sensor1_shutdown, GPIO.LOW)
	tof2.stop_ranging()
	GPIO.output(sensor2_shutdown, GPIO.LOW)
	tof3.stop_ranging()
	GPIO.output(sensor3_shutdown, GPIO.LOW)
	GPIO.cleanup()

	
	
try:
	setup()
	loop()
except KeyboardInterrupt:
	destroy()
finally:
	destroy()

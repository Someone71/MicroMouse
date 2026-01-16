# External module imports
import RPi.GPIO as GPIO
import time

import pigpio
from rotary_encoder import decoder
import rotary_encoder

from pid_c import PID

import numpy as np

P = 1
I = 0.75
D = 0.001

wcurr_L = 0
wcurr_R = 0
#
output_L = 1
output_R = 1
tsample = 0.01
taupid = 0.1

pos_L = 0
pos_R = 0
way_L = 0
way_R = 0
pin1 = 23
pin2 = 22
pin3 = 24
pin4 = 25
frequency = 100
pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)

def setup():
	print('Starting program...')
	GPIO.setup(pin1, GPIO.OUT)
	GPIO.setup(pin2, GPIO.OUT)
	GPIO.setup(pin3, GPIO.OUT)
	GPIO.setup(pin4, GPIO.OUT)
	GPIO.output(pin1, GPIO.LOW)
	GPIO.output(pin2, GPIO.LOW)
	GPIO.output(pin3, GPIO.LOW)
	GPIO.output(pin4, GPIO.LOW)
	global pwm1
	global pwm2
	global pwm3
	global pwm4
	pwm1 = GPIO.PWM(pin1, frequency)
	pwm2 = GPIO.PWM(pin2, frequency)
	pwm3 = GPIO.PWM(pin3, frequency)
	pwm4 = GPIO.PWM(pin4, frequency)
	pwm1.start(0)
	pwm2.start(0)
	pwm3.start(0)
	pwm4.start(0)
	
def loop():
	
	decoder_L = rotary_encoder.decoder(pi, 12, 13, callback_L)
	decoder_R = rotary_encoder.decoder(pi, 5, 6, callback_R)
	pid_L = PID(tsample, P, I, D, 100, -100, tau=taupid)
	pid_R = PID(tsample, P, I, D, 100, -100, tau=taupid)

	wfprev_L = 0
	wfprev_R = 0
	wfcurr_L = 0
	wfcurr_L = 0
	
	thetaprev_L = 0
	thetaprev_R = 0
	tprev = 0
	tcurr = 0
	
	tstart = time.perf_counter()
	#SPEEEEEEEED
	DEFL = 20
	DEFR = 50
	
	while True:
		#if(GPIO.output(pin1, GPIO.HIGH)):
		#	L = 1
		#elif(GPIO.output(pin2, GPIO.HIGH)):
		#	L = -1
		#else:
		#	L = 0
		L = 1
		R = 1
		
		time.sleep(tsample)
		
		tcurr = time.perf_counter() - tstart
		
		thetacurr_L = pos_L
		thetacurr_R = pos_R
		
		wcurr_L = np.pi/180 * (thetacurr_L - thetaprev_L)/(tcurr-tprev) * 5
		wcurr_R = np.pi/180 * (thetacurr_R - thetaprev_R)/(tcurr-tprev) * 5
				
		tprev = tcurr
		thetaprev_L = thetacurr_L
		thetaprev_R = thetacurr_R
		
		#print(wcurr_L)
		#print(DEFL - wcurr_L)
		#print(wcurr_R)
		#print(DEFR - wcurr_R)
		
		output_L = pid_L.control(0, wcurr_L-L*DEFL)
		output_R = pid_R.control(0, wcurr_R-R*DEFR)
		
		#print(output_L)			
		#print(output_R)
		
		if(output_L > 0):
			pwm2.ChangeDutyCycle(0)
			pwm1.ChangeDutyCycle(output_L)
		elif(output_L < 0):
			pwm1.ChangeDutyCycle(0)
			pwm2.ChangeDutyCycle(-output_L)
		else:
			pwm1.ChangeDutyCycle(0)
			pwm2.ChangeDutyCycle(0)
			
		if(output_R > 0):
			pwm4.ChangeDutyCycle(0)
			pwm3.ChangeDutyCycle(output_R)
		elif(output_R < 0):
			pwm3.ChangeDutyCycle(0)
			pwm4.ChangeDutyCycle(-output_R)
		else:
			pwm3.ChangeDutyCycle(0)
			pwm4.ChangeDutyCycle(0)
		
	"""
	GPIO.output(pin1, GPIO.HIGH)
	for x in range(30):
		print('Duty cycle: ' + str(x))
		pwm1.ChangeDutyCycle(x)
		time.sleep(0.1)
	for x in range(30, -1, -1):
		print('Duty cycle: ' + str(x))
		pwm1.ChangeDutyCycle(x)
		time.sleep(0.1)
	GPIO.output(pin1, GPIO.LOW)
	GPIO.output(pin2, GPIO.HIGH)
	for x in range(30):
		pwm2.ChangeDutyCycle(x)
		time.sleep(0.1)
	for x in range(30, -1, -1):
		pwm2.ChangeDutyCycle(x)
		time.sleep(0.1)
	GPIO.output(pin2, GPIO.LOW)	
	"""
	
	"""
	print('Motor A forward')
	GPIO.output(pin4, GPIO.LOW)
	GPIO.output(pin1, GPIO.HIGH)
	time.sleep(2)
	print('Motor A backward')
	GPIO.output(pin1, GPIO.LOW)
	GPIO.output(pin2, GPIO.HIGH)
	time.sleep(2)
	print('Motor B forward')
	GPIO.output(pin2, GPIO.LOW)
	GPIO.output(pin3, GPIO.HIGH)
	time.sleep(2)
	print('Motor B backward')
	GPIO.output(pin3, GPIO.LOW)
	GPIO.output(pin4, GPIO.HIGH)
	time.sleep(2)
	"""
	
def callback_L(way_L):
	global pos_L
	pos_L += way_L
	#print("L={}".format(pos_L))
	
def callback_R(way_R):
	global pos_R
	pos_R += way_R
	#print("R={}".format(pos_R))
	
def destroy():
	pwm1.stop()
	pwm2.stop()
	pwm3.stop()
	pwm4.stop()
	decoder_L.cancel()
	decoder_R.cancel()
	GPIO.cleanup()
	pi.stop()
	
	 
	
if __name__ == '__main__':
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()
	finally:
		destroy()

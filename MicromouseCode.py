import RPi.GPIO as GPIO
import time
import math

import pigpio
import rotary_encoder
from rotary_encoder import decoder

from pid_c import PID

import numpy as np

import smbus

import sys
sys.path.insert(0, '/home/someone/Micromouse/VL53L0X_rasp_python/python')
import VL53L0X

import threading

#sys.path.insert(0, '/home/someone/Micromouse/MinIMU-9-v5')
#from MinIMU_v5_pi import MinIMU_v5_pi

#gyro
# sys.path.insert(0, '/home/someone/Micromouse/mpu6050/mpu')
# from gyro import mpu6050
# gyroscope = mpu6050(0x68)
#IMU = MinIMU_v5_pi()

#Laser rage finder sensors, turning them on and off
sensor1_shutdown = 20 #left
sensor2_shutdown = 16 #middle
sensor3_shutdown = 21 #right
                                                                                                                                                                    
#the actual names of the sensors
tof1 = VL53L0X.VL53L0X(address=0x2B)
tof2 = VL53L0X.VL53L0X(address=0x2D)
tof3 = VL53L0X.VL53L0X(address=0x2E)

#sampling time (ms)
dt_target = 0.05

#motor speed control pid
Pm = 1.2
Im = 2
Dm = 0

#motor turning pid
Pt = 0.12 #0.12
It = 0.071 #0.1
Dt = 0 #0.0067

#more stuff for motor setup
output_L = 0
output_R = 0
thetaprev_L = 0
thetaprev_R = 0
taupid = 0.1

wcurr_L = 0
wcurr_R = 0

pos_L = 0
pos_R = 0
way_L = 0
way_R = 0

desiredEncL = 0
desiredEncR = 0

#sets up the PID
pid_L = PID(dt_target, Pm, Im, Dm, 100, -100, tau=taupid)
pid_R = PID(dt_target, Pm, Im, Dm, 100, -100, tau=taupid)

#pins for motor control
pin1 = 22
pin2 = 23
pin3 = 24
pin4 = 25
#for PWM
frequency = 100

#turning on GPIO pins and choosing the naming setup
pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)

def setup():
      #IMU.trackYaw()
      #IMU.trackAngle()
      #print('Starting program...')
      #motor shit
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
      
      #laser range finder shit
      GPIO.setup(sensor1_shutdown, GPIO.OUT)
      GPIO.setup(sensor2_shutdown, GPIO.OUT)
      GPIO.setup(sensor3_shutdown, GPIO.OUT)
      GPIO.output(sensor1_shutdown, GPIO.LOW)
      GPIO.output(sensor2_shutdown, GPIO.LOW)
      GPIO.output(sensor3_shutdown, GPIO.LOW)
      
      #activating the laser range finders
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
      
      #starting the motor encoder
      global decoder_L
      global decoder_R
      decoder_L = rotary_encoder.decoder(pi, 5, 6, callback_L)
      decoder_R = rotary_encoder.decoder(pi, 12, 13, callback_R)
      
def turnRight():
      global pos_L, pos_R
      
      resetMotor()
      
      #setup PID for turning (dt is time stamp, Dt is derivative term)
      turn_pid_L = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)
      turn_pid_R = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L + 220
      desiredEncR = pos_R - 220
      
      #timer stuff
      prev_time = time.perf_counter() - dt_target
      
      while True:
            #more timer stuff
            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            
            #print(dt)
            
            #determines the speed of the motor
            outputL = turn_pid_L.control(desiredEncL, pos_L)
            outputR = turn_pid_R.control(desiredEncR, pos_R)
            #print(outputL)
            #print(outputR)
            motorMove(outputL, outputR, dt)
            #motorMove(25, 25, dt)
            time.sleep(dt_target)
            
            #exits loop once desired turn is achieved
            if(abs(desiredEncL - pos_L) < 15 and abs(pos_R - desiredEncR) < 15):
                  resetMotor()
                  print("Broke out of while loop")
                  break
                  
def turnLeft():
      global pos_L, pos_R
      
      resetMotor()
      
      #setup PID for turning (dt is time stamp, Dt is derivative term)
      turn_pid_L = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)
      turn_pid_R = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L - 220
      desiredEncR = pos_R + 220
      
      #timer stuff
      prev_time = time.perf_counter() - dt_target
      
      while True:
            #more timer stuff
            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            
            #print(dt)
            
            #determines the speed of the motor
            outputL = turn_pid_L.control(desiredEncL, pos_L)
            outputR = turn_pid_R.control(desiredEncR, pos_R)
            #print(outputL)
            #print(outputR)
            motorMove(outputL, outputR, dt)
            #motorMove(25, 25, dt)
            time.sleep(dt_target)
            
            #exits loop once desired turn is achieved
            if(abs(desiredEncL - pos_L) < 15 and abs(pos_R - desiredEncR) < 15):
                  resetMotor()
                  print("Broke out of while loop")
                  break

def motorMove(leftMotorSpeed, rightMotorSpeed, dt):
      #print("m")
      global thetaprev_L, thetaprev_R
      global pos_L, pos_R
      global pid_L, pid_R
            
      thetacurr_L = pos_L
      thetacurr_R = pos_R
      dthetal = thetacurr_L - thetaprev_L
      dthetar = thetacurr_R - thetaprev_R

      #pi * D   dtheta/450    /   dt/1000
      #mm/sec
      wcurr_L = (np.pi * 3.8) * (dthetal / 450) / (dt)
      wcurr_R = (np.pi * 3.8) * (dthetar / 450) / (dt)
      
      thetaprev_L = thetacurr_L
      thetaprev_R = thetacurr_R
      
      #print(wcurr_L)
      #print(SpeedL - wcurr_L)
      #print(wcurr_R)
      #print(SpeedR - wcurr_R)
      
      #determines how much to change motor speed in order for the actual speed to be equal to the desired speed
      output_L = pid_L.control(leftMotorSpeed, wcurr_L)
      output_R = pid_R.control(rightMotorSpeed, wcurr_R)
      
      #print(output_L)
      #print(output_R)
      
      #changes the motor speed
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
      
def resetMotor():
      print("motors reset")
      
      #stop all motors
      pwm1.ChangeDutyCycle(0)
      pwm2.ChangeDutyCycle(0)
      pwm3.ChangeDutyCycle(0)
      pwm4.ChangeDutyCycle(0)
      
      global thetaprev_L, thetaprev_R
      global pos_L, pos_R
      global pid_L, pid_R
      
      #reset variable for motor speed calc
      thetaprev_L = 0
      thetaprev_R = 0
      #reset encoder values (not rly necessary)
      pos_L = 0
      pos_R = 0
      #reset PID for motor speed
      pid_L = PID(dt_target, Pm, Im, Dm, 100, -100, tau=taupid)
      pid_R = PID(dt_target, Pm, Im, Dm, 100, -100, tau=taupid)

#functions for getting the encoder values
def callback_L(way_L):
      global pos_L
      pos_L += way_L
      print("L={}".format(pos_L))
def callback_R(way_R):
      global pos_R
      pos_R += way_R
      print("R={}".format(pos_R))
      
#function to get the values from the laser range sensors
def tof():
      timing = tof1.get_timing()
      if (timing < 20000):
            timing = 20000
      distance1 = tof1.get_distance()
      distance2 = tof2.get_distance()
      distance3 = tof3.get_distance()
      distance4 = tof4.get_distance()
      time.sleep(timing/1000000.00)
      return distance1, distance2, distance3, distance4

#stop everything
def destroy():
      pwm1.stop()
      pwm2.stop()
      pwm3.stop()
      pwm4.stop()
      tof1.stop_ranging()
      tof2.stop_ranging()
      tof3.stop_ranging()
      tof4.stop_ranging()
      decoder_L.cancel()
      decoder_R.cancel()
      GPIO.cleanup()
      pi.stop()
      
def loop():
      time.sleep(5)
      for i in range(10):
            turnLeft()
            time.sleep(0.5)
           
      #turnRight()
      #turnLeft()
            
      # time.sleep(10)
      # turnRight()
      # print("finished turn left 1")
      # time.sleep(0.5)
      # turnRight()
      # print("finished turn left 2")
      # time.sleep(0.5)
      # turnRight()
      # print("finished turn left 3")
      # time.sleep(0.5)
      # turnRight()
      # print("finished turn left 4")
      time.sleep(60)
      
#start everything
if __name__ == '__main__':
      try:
            setup()
            loop()
      except KeyboardInterrupt:
            destroy()
      finally:
            destroy()

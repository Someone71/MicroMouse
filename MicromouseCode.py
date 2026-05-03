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

global left
global right
global front

global desiredEncL
global desiredEncR


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
Ps = 1.2
Is = 2
Ds = 0

#motor turning pid
Pt = 0.06 #0.12
It = 0.02 #0.1
Dt = 0 #0.0067

#motor move pid
Pm = 0.06 #0.12, 0.1
Im = 0.01 #0.1
Dm = 0 #0.0067

#motor sprint pid
Pv = 0.02 #0.12
Iv = 0.0014 #0.1
Dv = 0 #0.0067

#motor adjusting pid
Pa = 0.05
Ia = 0.003
Da = 0

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
pid_L = PID(dt_target, Ps, Is, Ds, 100, -100, tau=taupid)
pid_R = PID(dt_target, Ps, Is, Ds, 100, -100, tau=taupid)

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
      print('Starting program...')
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
      desiredEncL = pos_L + 215
      desiredEncR = pos_R - 215
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
            if(abs(desiredEncL - pos_L) < 4 and abs(pos_R - desiredEncR) < 4):
                  resetMotor()
                  #print("Broke out of while loop")
                  break
                                                      
def turnLeft():
      global pos_L, pos_R
      
      resetMotor()
      
      #setup PID for turning (dt is time stamp, Dt is derivative term)
      turn_pid_L = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)
      turn_pid_R = PID(dt_target, Pt, It, Dt, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L - 215
      desiredEncR = pos_R + 215
      
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
            if(abs(desiredEncL - pos_L) < 4 and abs(pos_R - desiredEncR) < 4):
                  resetMotor()
                  #print("Broke out of while loop")
                  break
                  
def turnVar(encChangeL, encChangeR):
      global pos_L, pos_R
      
      resetMotor()
      
      #setup PID for turning (dt is time stamp, Dt is derivative term)
      turn_pid_L = PID(dt_target, Pa, Ia, Da, 35, -35, tau=taupid)
      turn_pid_R = PID(dt_target, Pa, Ia, Da, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L - encChangeL
      desiredEncR = pos_R - encChangeR
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
            if(abs(desiredEncL - pos_L) < 6 and abs(pos_R - desiredEncR) < 6):
                  resetMotor()
                  #print("Broke out of while loop")
                  break

def forward1():
      global pos_L, pos_R
      global desiredEncL
      global desiredEndR
      
      resetMotor()
      
      #setup PID for motor moving
      move_pid_L = PID(dt_target, Pm, Im, Dm, 35, -35, tau=taupid)
      move_pid_R = PID(dt_target, Pm, Im, Dm, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L + 637
      desiredEncR = pos_R + 637
      
      
      #timer stuff
      prev_time = time.perf_counter() - dt_target      

      while True:
            EncL = int(mouse1.autoAdjustL(desiredEncL))
            EncR = int(mouse1.autoAdjustR(desiredEncR))
            
            desiredEncL += EncL
            desiredEncR += EncR
            desiredEncL -= EncR
            desiredEncR -= EncL
            
            #more timer stuff
            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            
            #print(dt)
            
            print(desiredEncL)
            print(desiredEncR)

            #determines the speed of the motor
            outputL = move_pid_L.control(desiredEncL, pos_L)
            outputR = move_pid_R.control(desiredEncR, pos_R)
            #print(outputL)
            #print(outputR)
            motorMove(outputL, outputR, dt)
            #motorMove(25, 25, dt)
            time.sleep(dt_target)
            
            #exits loop once desired turn is achieved
            if((abs(desiredEncL - pos_L) < 6 and abs(pos_R - desiredEncR) < 6)): #or front <= 65
                  resetMotor()
                  #print("Broke out of while loop")
                  break
def forwardVar(cells):
      global pos_L, pos_R
      global desiredEncL
      global desiredEndR
      
      resetMotor()
      
      #setup PID for motor moving
      sprint_pid_L = PID(dt_target, Pv, Iv, Dv, 35, -35, tau=taupid)
      sprint_pid_R = PID(dt_target, Pv, Iv, Dv, 35, -35, tau=taupid)

      #sets target values for the encoder 
      desiredEncL = pos_L + 637 * cells
      desiredEncR = pos_R + 637 * cells
      
      EncL = int(mouse1.autoAdjustL(desiredEncL))
      EncR = int(mouse1.autoAdjustR(desiredEncR))
      desiredEncL += EncL
      desiredEncR += EncR
      desiredEncL -= EncR
      desiredEncR -= EncL
      
      #timer stuff
      prev_time = time.perf_counter() - dt_target
      
      while True:
            #more timer stuff
            curr_time = time.perf_counter()
            dt = curr_time - prev_time
            prev_time = curr_time
            
            #print(dt)

            #determines the speed of the motor
            outputL = sprint_pid_L.control(desiredEncL, pos_L)
            outputR = sprint_pid_R.control(desiredEncR, pos_R)
            #print(outputL)
            #print(outputR)
            motorMove(outputL, outputR, dt)
            #motorMove(25, 25, dt)
            time.sleep(dt_target)
            
            #exits loop once desired turn is achieved
            if((abs(desiredEncL - pos_L) < 6 and abs(pos_R - desiredEncR) < 6)): #or front <= 65
                  resetMotor()
                  #print("Broke out of while loop")
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
      #print("motors reset")
      
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
      pid_L = PID(dt_target, Ps, Is, Ds, 100, -100, tau=taupid)
      pid_R = PID(dt_target, Ps, Is, Ds, 100, -100, tau=taupid)

#functions for getting the encoder values
def callback_L(way_L):
      global pos_L
      pos_L += way_L
      #print("L={}".format(pos_L))
def callback_R(way_R):
      global pos_R
      pos_R += way_R
      #print("R={}".format(pos_R))
      
#function to get the values from the laser range sensors
def tof():
      global left
      global right
      global front
      timing = tof1.get_timing()
      if (timing < 20000):
            timing = 20000
      left = tof1.get_distance()
      front = tof2.get_distance()
      right = tof3.get_distance()
      time.sleep(timing/1000000.00)

#stop everything
def destroy():
      pwm1.stop()
      pwm2.stop()
      pwm3.stop()
      pwm4.stop()
      tof1.stop_ranging()
      tof2.stop_ranging()
      tof3.stop_ranging()
      decoder_L.cancel()
      decoder_R.cancel()
      GPIO.cleanup()
      pi.stop()
      
global override
override = False

class Cell:
    def __init__(self, cols, rows): # constructor
        self.cols = cols
        self.rows = rows
        self.value = 99
        self.wallN = False
        self.wallS = False
        self.wallE = False
        self.wallW = False
        self.onBestPath = False

    def setOnBestPath(self): # makes something on the best path
        self.onBestPath = True
    
    def setWall(self, direction): # makes a wall at specified direction
        if direction == "N":
            self.wallN = True
        if direction == "S":
            self.wallS = True
        if direction == "E":
            self.wallE = True
        if direction == "W":
            self.wallW = True

    def updateWalls(self): # updates the walls of the cell with the walls of adjacent cells
        if self.cols < cols - 1:
            if array_2d[self.rows][self.cols + 1].wallW:
                self.wallE = True
        if self.cols > 0:
            if array_2d[self.rows][self.cols - 1].wallE:
                self.wallW = True
        if self.rows < rows - 1:
            if array_2d[self.rows + 1][self.cols].wallN:
                self.wallS = True
        if self.rows > 0:
            if array_2d[self.rows - 1][self.cols].wallS:
                self.wallN = True
    
    def setVal(self, value): # sets the value(cells from center) of the cell
        self.value = value
    
    def updateVal(self): # updates the value of the cell with the value of adjacent cells
        if self.cols < cols - 1:
            if array_2d[self.rows][self.cols + 1].value + 1 < self.value and not self.wallE:
                self.value = array_2d[self.rows][self.cols + 1].value + 1
                """
                if the cell to the right of the cell's value + 1 is less than the
                current cell's value, then it sets the current cell's value to the
                right cell's value + 1
                """
        if self.cols > 0:
            if array_2d[self.rows][self.cols - 1].value + 1 < self.value and not self.wallW:
                self.value = array_2d[self.rows][self.cols - 1].value + 1
        if self.rows < rows - 1:
            if array_2d[self.rows + 1][self.cols].value + 1 < self.value and not self.wallS:
                self.value = array_2d[self.rows + 1][self.cols].value + 1
        if self.rows > 0:
            if array_2d[self.rows - 1][self.cols].value + 1 < self.value and not self.wallN:
                self.value = array_2d[self.rows - 1][self.cols].value + 1

# setting up base values and the array itself
#rows, cols = 16, 16
rows, cols = 8, 8
array_2d = [[Cell(j, i) for j in range(cols)] for i in range(rows)]
# array_2d[7][7].setVal(0)
# array_2d[8][7].setVal(0)
# array_2d[7][8].setVal(0)
# array_2d[8][8].setVal(0)
array_2d[4][4].setVal(0)


def printArrayVals(): # prints the array with the values of the cells accounting for if it is on the best path or not and if there are walls in a specified direction
    print("\n\n")
    for i in range (rows):
        print("[ ", end = "")
        for j in range (cols):
            if(array_2d[i][j].value < 10):
                if(array_2d[i][j].wallE and j < 15):
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + "|")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + "|")  
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = " |")
                        else:
                            print(array_2d[i][j].value, end = " |")
                else:
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + " ")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "\x1B[4m" + " " + "\x1B[0m" + " ")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = "  ")
                        else:  
                            print(array_2d[i][j].value, end = "  ")
            
            else:
                if(array_2d[i][j].wallE and j < 15):
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = "|")
                        else:
                            print(array_2d[i][j].value, end = "|")
                else:
                    if(array_2d[i][j].wallS and i < 15):
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + "\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                        else:
                            print("\x1B[4m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                    else:
                        if(array_2d[i][j].onBestPath):
                            print("\x1b[35m" + str(array_2d[i][j].value) + "\x1B[0m", end = " ")
                        else:
                            print(array_2d[i][j].value, end = " ")
        print ("]")
    print("^^^")
def findDistance(self): # finds the distnce of the furthest cell in a a straight line that is on the best path and moves the mouse to that cell
    if(self.direction == "E"):
        val = 0
        for i in range (1, cols):
            if(self.col < cols - i and self.maze[self.row][self.col + i].onBestPath and not self.maze[self.row][self.col + (i - 1)].wallE):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "W"):
        val = 0
        for i in range (1, cols):
            if(self.col > i - 1 and self.maze[self.row][self.col - i].onBestPath and not self.maze[self.row][self.col - (i - 1)].wallW):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "N"):
        val = 0
        for i in range (1, rows):
            if(self.row > i - i and self.maze[self.row - i][self.col].onBestPath and not self.maze[self.row - (i - 1)][self.col].wallN):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
    if(self.direction == "S"):
        val = 0
        for i in range (1, rows):
            if(self.row < rows - i and self.maze[self.row + i][self.col].onBestPath and not self.maze[self.row + (i - 1)][self.col].wallS):
                val += 1
            else:
                break
        if(val == 1 and diag):
            print("diag")
            diagonal(self)
        else:
            self.moveForward(val)
def findDistanceDiag(self): # finds the distnce of the furthest cell in a a diagonal line that is on the best path and moves the mouse to that cell
    print(self.direction)
    if(self.direction == "E"):
        val = 0
        for i in range (1, cols):
            if(self.col < cols - i and self.maze[self.row][self.col + i].onBestPath and not self.maze[self.row][self.col + (i - 1)].wallE):
                val += 1
            else:
                turn45()
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "W"):
        val = 0
        for i in range (1, cols):
            if(self.col > i - 1 and self.maze[self.row][self.col - i].onBestPath and not self.maze[self.row][self.col - (i - 1)].wallW):
                val += 1
            else:
                turn45()
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "N"):
        val = 0
        for i in range (1, rows):
            if(self.row > i - i and self.maze[self.row - i][self.col].onBestPath and not self.maze[self.row - (i - 1)][self.col].wallN):
                val += 1
            else:
                turn45()
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
    if(self.direction == "S"):
        val = 0
        for i in range (1, rows):
            if(self.row < rows - i and self.maze[self.row + i][self.col].onBestPath and not self.maze[self.row + (i - 1)][self.col].wallS):
                val += 1
            else:
                turn45()
                break
        if(val == 1 and diag):
            print("diag (fake)")
            return True
        else:
            return False
            
def diagonal(self): # moves the mouse diagonally to the end of the diagonal line
    next = True
    while(next):
        next = mouse1.followBestPath(False)
        
def updateArrayVals(): # updates the values of the cells in the array accounting for new walls
    for s in range (99):
        for i in range (rows):
            for j in range (cols):
                array_2d[i][j].updateVal()
                
def resetArrayVals(): # resets the values of the cells in the array (called in conjunction with updateArrayVals())
    global override
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].setVal(99)
        if(not override):
            # array_2d[7][7].setVal(0)
            # array_2d[8][7].setVal(0)
            # array_2d[7][8].setVal(0)
            # array_2d[8][8].setVal(0)
            array_2d[4][4].setVal(0)
        else:
            array_2d[0][0].setVal(0)
            
def updateArrayWalls(): # updates the walls of the cells in the array
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].updateWalls()

def findBestPath(rowS, colS): # finds the best path from the mouse's current position to the center using the cell values(does not account for diagonal turns being slightly faster despite more distance)
    resetBestPath()
    rowsC = rowS
    colsC = colS
    currentCell = array_2d[rowsC][colsC]
    for i in range (99):
        currentCell.setOnBestPath()
        if(colsC < cols - 1):
            if(array_2d[rowsC][colsC + 1].value == currentCell.value - 1 and not currentCell.wallE):
                currentCell = array_2d[rowsC][colsC + 1]
        if(colsC > 0):
            if(array_2d[rowsC][colsC - 1].value == currentCell.value - 1 and not currentCell.wallW):
                currentCell = array_2d[rowsC][colsC - 1]
        if(rowsC < rows - 1):
            if(array_2d[rowsC + 1][colsC].value == currentCell.value - 1 and not currentCell.wallS):
                currentCell = array_2d[rowsC + 1][colsC]
        if(rowsC > 0):
            if(array_2d[rowsC - 1][colsC].value == currentCell.value - 1 and not currentCell.wallN):
                currentCell = array_2d[rowsC - 1][colsC]
        rowsC = currentCell.rows
        colsC = currentCell.cols
def resetBestPath(): # resets the best path of the cells in the array (called in conjunction with findBestPath())
    for i in range (rows):
        for j in range (cols):
            array_2d[i][j].onBestPath = False
class Mouse: # defines the class of mouse and its base values and methods
    def __init__(self, maze):
        self.direction = "E"
        self.row = 0
        self.col = 0
        self.wallN = False
        self.wallS = False
        self.wallE = False
        self.wallW = False
        self.wallF = False
        self.wallR = False
        self.wallL = False
        self.maze = maze
        self.currentCell = self.maze[self.row][self.col]
    def turn90(self): # turns the mouse 90 degrees to the right
        turnRight()
        if(self.direction == "N"):
            self.direction = "E"
            return
        if(self.direction == "E"):
            self.direction = "S"
            return
        if(self.direction == "S"):
            self.direction = "W"
            return
        if(self.direction == "W"):
            self.direction = "N"
            return
    def turnNeg90(self): # turns the mouse 90 degrees to the left
        turnLeft()
        if(self.direction == "N"):
            self.direction = "W"
            return
        if(self.direction == "W"):
            self.direction = "S"
            return
        if(self.direction == "S"):
            self.direction = "E"
            return
        if(self.direction == "E"):
            self.direction = "N"
            return
    def moveForward1(self): # moves the mouse forward a specified amount of cells
        forward1()
        if(self.direction == "N"):
            self.row -= 1
        if(self.direction == "S"):
            self.row += 1
        if(self.direction == "E"):
            self.col += 1
        if(self.direction == "W"):
            self.col -= 1
        self.currentCell = self.maze[self.row][self.col]
    def moveForward(self, amount): # moves the mouse forward a specified amount of cells
        forwardVar(amount)
        if(self.direction == "N"):
            self.row -= amount
        if(self.direction == "S"):
            self.row += amount
        if(self.direction == "E"):
            self.col += amount
        if(self.direction == "W"):
            self.col -= amount
        self.currentCell = self.maze[self.row][self.col]
    def movePosForward(self, amount): # moves the mouse's position forward a specified amount of cells (used for diagonal movement)
        if(self.direction == "N"):
            self.row -= amount
        if(self.direction == "S"):
            self.row += amount
        if(self.direction == "E"):
            self.col += amount
        if(self.direction == "W"):
            self.col -= amount
        self.currentCell = self.maze[self.row][self.col]
    def detectWalls(self): # detects the walls around the mouse
        global left
        global right
        global front
        tof()
        if(right < 150):
            self.wallR = True
        if(left < 150):
            self.wallL = True
        if(front < 150):
            self.wallF = True
        mouse1.updateWalls()
        self.wallF = False
        self.wallR = False
        self.wallL = False
    def updateWalls(self): # updates the walls of the cell the mouse is on with the walls the mouse detects
        if(self.wallF):
            self.currentCell.setWall(self.direction)
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
        if(self.wallR):
            if(self.direction == "N"):
                self.currentCell.setWall("E")
            if(self.direction == "W"):
                self.currentCell.setWall("N")
            if(self.direction == "S"):
                self.currentCell.setWall("W")
            if(self.direction == "E"):
                self.currentCell.setWall("S")
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
        if(self.wallL):
            if(self.direction == "N"):
                self.currentCell.setWall("W")
            if(self.direction == "W"):
                self.currentCell.setWall("S")
            if(self.direction == "S"):
                self.currentCell.setWall("E")
            if(self.direction == "E"):
                self.currentCell.setWall("N")
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
          
    def autoAdjustL(self, EncL):
        if(left < 50 and EncL < 630):
            return "1"
        return "0"
    def autoAdjustR(self, EncR):
        if(right < 50 and EncR < 630):
            return "1"
        return "0"
    def autoAdjustOnWall(self):
          if(((left > 70 and left < 120) or left < 60) and ((right > 75 and right < 120) or right < 50)):
                turnVar((left - 64)/2.5, (right - 61)/2.5)
                
    # def autoAdjustL(self, EncL):
        # if(left < 40 and right > 70): # and EncL < 300            # print("ur granddad")
            # return "2"
        # elif(left < 60 and right > 70): # and EncL < 300
            # print("ur grandmom")
            # return "2"
        # return "0"
    # def autoAdjustR(self, EncR):
        # if(right < 15 and left > 70): # and EncR < 300
            # print("ur dad")
            # return "2"
        # elif(right < 40 and left > 70): # and EncR < 300
            # print("ur mom")
            # return "2"
        # return "0"
            
    def followBestPath(self, real): # follows the best path from the mouse's current position to the center using the cell values(has different modes for mapping and diagonal movement)
        findBestPath(self.row, self.col)
        if(real):
            if(mapping):
                if(self.direction == "E"):
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.autoAdjustOnWall()
                        self.moveForward1()
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        self.moveForward1()
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turnNeg90()
                        self.moveForward1()
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        if(left < 61):
                              self.turn90()
                              time.sleep(0.5)
                              self.turn90()
                        else:
                              self.turnNeg90()
                              time.sleep(0.5)
                              self.turnNeg90()
                        self.moveForward1()
                        return
                if(self.direction == "W"):
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.autoAdjustOnWall()
                        self.moveForward1()
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turnNeg90()
                        self.moveForward1()
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        self.moveForward1()
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        if(left < 61):
                              self.turn90()
                              time.sleep(0.5)
                              self.turn90()
                        else:
                              self.turnNeg90()
                              time.sleep(0.5)
                              self.turnNeg90()
                        self.moveForward1()
                        return
                if(self.direction == "N"):
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.autoAdjustOnWall()
                        self.moveForward1()
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        self.moveForward1()
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turnNeg90()
                        self.moveForward1()
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        if(left < 61):
                              self.turn90()
                              time.sleep(0.5)
                              self.turn90()
                        else:
                              self.turnNeg90()
                              time.sleep(0.5)
                              self.turnNeg90()
                        self.moveForward1()
                        return
                if(self.direction == "S"):
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.autoAdjustOnWall()
                        self.moveForward1()
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turnNeg90()
                        self.moveForward1()
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        self.moveForward1()
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        if(left < 61):
                              self.turn90()
                              time.sleep(0.5)
                              self.turn90()
                        else:
                              self.turnNeg90()
                              time.sleep(0.5)
                              self.turnNeg90()
                        self.moveForward1()
                        return
            else:
                if(self.direction == "E"):
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        time.sleep(0.5)
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "W"):
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        time.sleep(0.5)
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "N"):
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        self.turn90()
                        time.sleep(0.5)
                        self.turn90()
                        findDistance(self)
                        return
                if(self.direction == "S"):
                    if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                        findDistance(self)
                        return
                    if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                        self.turnNeg90()
                        findDistance(self)
                        return
                    if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                        self.turn90()
                        findDistance(self)
                        return
                    if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                        self.turn90()
                        time.sleep(0.5)
                        self.turn90()
                        findDistance(self)
                        return
        else:
            if(self.direction == "E"):
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "W"):
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "N"):
                if(self.row > 0 and self.maze[self.row - 1][self.col].onBestPath and not self.maze[self.row][self.col].wallN):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
            if(self.direction == "S"):
                if(self.row < rows - 1 and self.maze[self.row + 1][self.col].onBestPath and not self.maze[self.row][self.col].wallS):
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col < cols - 1 and self.maze[self.row][self.col + 1].onBestPath and not self.maze[self.row][self.col].wallE):
                    self.turnNeg90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                if(self.col > 0 and self.maze[self.row][self.col - 1].onBestPath and not self.maze[self.row][self.col].wallW):
                    self.turn90()
                    next = findDistanceDiag(self)
                    self.movePosForward(1)
                    return next
                    
def writeMazeToFile():
    file = open("maze.txt", "w")
    thingsToAdd = []
    for i in range(rows):
        for j in range(cols):
            if(array_2d[i][j].wallN == True):
                file.write(str(i)+str(j)+"N")
            if(array_2d[i][j].wallE == True):
                file.write(str(i)+str(j)+"E")
            if(array_2d[i][j].wallS == True):
                file.write(str(i)+str(j)+"S")
            if(array_2d[i][j].wallW == True):
                file.write(str(i)+str(j)+"W")
    file.close()
def readMazeFromFile():
    file = open("maze.txt", "r")
    fileString = file.read()
    file.close()
    for i in range(len(fileString)):
        if(i % 3 == 0):
            row = int(fileString[i])
        elif(i % 3 == 1):
            col = int(fileString[i])
        else:
            direction = fileString[i]
        array_2d[col][row].setWall(direction)  
        
mouse1 = Mouse(array_2d)


updateArrayWalls()
resetArrayVals()
updateArrayVals()
findBestPath(mouse1.row, mouse1.col)
printArrayVals()

mapping = True
diag = False
print("Gurt: Yo")
def loop():
    time.sleep(10)
    print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    global override
    for i in range (99): # main loop
        printArrayVals()
        print(mouse1.row, mouse1.col, mouse1.currentCell.value, mouse1.currentCell.rows, mouse1.currentCell.cols, mouse1.direction)
        if(mapping):
            mouse1.detectWalls()
            updateArrayWalls()
            resetArrayVals()
            updateArrayVals()
        if(mouse1.currentCell.value == 0):
            time.sleep(3)
            override = True
            resetArrayVals()
            updateArrayVals()
        mouse1.followBestPath(True)

# Turn 45 implementation
# exiting diagonal turns
# turns during diagonals


#                                           def loop():
      # time.sleep(10)
      # for i in range(10):
            # turnLeft()
            # time.sleep(1)
      # time.sleep(60)
           
      # #turnRight()
      # #turnLeft()
      # forward1()
            
      # # time.sleep(10)
      # # turnRight()      # print("finished turn left 1")
      # # time.sleep(0.5)
      # # turnRight()
      # # print("finished turn left 2")
      # # time.sleep(0.5)
      # # turnRight()
      # # print("finished turn left 3")
      # # time.sleep(0.5)
      # # turnRight()
      # # print("finished turn left 4")
      # time.sleep(60)
      
#start everything
if __name__ == '__main__':
      try:
            setup()
            loop()
      except KeyboardInterrupt:
            destroy()
      finally:
            destroy()

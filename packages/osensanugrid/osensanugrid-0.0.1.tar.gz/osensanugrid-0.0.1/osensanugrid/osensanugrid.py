import spidev
import RPi.GPIO as GPIO
import time
from osensapy import osensapy
import Adafruit_ADS1x15
import Adafruit_MCP4725
from math import log, exp 

class MainBoard():
	#initializes everything as soon as you create a board object
	def __init__(self):
		global spiAdc, spiBoards, ldac, clr, cnv, cnv_board, transmitter1, transmitter2, transmitter3, t1, t2, t3, led_on, led1, led2, led3, led4,tec_dac, led_dac, tec_adc 
		#SPI setup
		spiAdc = spidev.SpiDev()
		spiBoards = spidev.SpiDev()
		spiAdc.open(0,0)
		spiBoards.open(0,1)
		spiAdc.max_speed_hz = 10000000
		spiBoards.max_speed_hz = 10000000

		#GPIO setup
		ldac= 26  #19 #DAC pin	#these 19 pins will have to change to say 13.
		cnv = 19 #ADC pin, onboard ADC
		clr = 13 #DAC pin for extra board
		cnv_board = 26 #ADC pin for extra ADC
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(19,GPIO.OUT)
		GPIO.setup(13,GPIO.OUT)
		GPIO.setup(26,GPIO.OUT)

		#1Ch modules setup
		transmitter1 = osensapy.Transmitter("/dev/ttyS0", 247, 115200, 1)
		transmitter2 = osensapy.Transmitter("/dev/ttyS0", 246, 115200, 1)
		transmitter3 = osensapy.Transmitter("/dev/ttyS0", 245, 115200, 1)
		t1 = 23
		t2 = 4
		t3 = 27
		GPIO.setup(t1, GPIO.OUT) #CS for t1
		GPIO.setup(t2, GPIO.OUT) #for t2
		GPIO.setup(t3, GPIO.OUT) #for t3
		GPIO.output(t1,GPIO.HIGH)
		GPIO.output(t2,GPIO.HIGH)
		GPIO.output(t3,GPIO.HIGH)

		#TEC+LED unit setup
		led_on = 17 #this will have to change to say 22. Remaining status LEDs will have to be BCM 0,5,6,26?
		GPIO.setup(led_on, GPIO.OUT)
		GPIO.output(led_on, GPIO.HIGH)
		#for I2C ADC for TEC
		tec_adc = Adafruit_ADS1x15.ADS1015()
		#for I2C DAC for TEC
		tec_dac = Adafruit_MCP4725.MCP4725(address=0x63)
		tec_dac.set_voltage(300) #initially set that DAC to reach 24-25C
		#for I2C DAC for TEC LED
		led_dac = Adafruit_MCP4725.MCP4725()
		led_dac.set_voltage(0) #initially have that DAC be 0V

		#status LEDs
		led1 = 24
		led2 = 22
		led3 = 25
		led4 = 5
		GPIO.setup(led1, GPIO.OUT)
		GPIO.setup(led2, GPIO.OUT)
		GPIO.setup(led3, GPIO.OUT)
		GPIO.setup(led4, GPIO.OUT)
		GPIO.output(led1, 0)
		GPIO.output(led2, 0)
		GPIO.output(led3, 0)
		GPIO.output(led4, 0)

	#read photodiodes in pairs, with "phase" = channel pair. Will return a list of two values.
	def read_photodiode(self,phase):
		GPIO.output(cnv,GPIO.HIGH)
		#the first 3 bytes to xfer are the "Softspan" words, the other bytes (0s) are to receive the previous conversion's results 
		r = spiAdc.xfer([0b00100100,0b10010010,0b01001001,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
		GPIO.output(cnv,GPIO.LOW)
		if phase == 1:
			intVal1 = (r[0]<<8) + r[1]
			intVal2 = (r[3]<<8) + r[4] 
		elif phase == 2:
			intVal1 = (r[6]<<8) + r[7] 
			intVal2 = (r[9]<<8) + r[10] 
		else:
			intVal1 = (r[12]<<8) + r[13] 
			intVal2 = (r[15]<<8) + r[16] 		
		voltage1 = intVal1 * float(5.12) / 65536
		voltage2 = intVal2 * float(5.12) / 65536

		#error checking 
		if (r[2]!=0b00000001 or r[5]!=0b00001001 or r[8]!=0b00010001 or r[11]!=0b00011001 or r[14]!=0b00100001 or r[17]!=0b00101001):
			errorChannel = 0b000000
			if(r[2]!=0b00000001):
				errorChannel=errorChannel + 0b000001
			if(r[5]!=0b00001001):
				errorChannel=errorChannel+0b000010
			if(r[8]!=0b00010001):
				errorChannel=errorChannel+0b000100
			if(r[11]!=0b00011001):
				errorChannel=errorChannel+0b001000
			if(r[14]!=0b00100001):
				errorChannel=errorChannel+0b010000
			if(r[17]!=0b00101001):
				errorChannel=errorChannel+0b100000
			raise ValueError("There were errors in reading channels: {:06b}".format(errorChannel)) 
		return voltage1,voltage2 

	#to use this, you will need to not use the DAC at the same time (on the Pi)
	def read_adc(self,phase):
		GPIO.output(cnv_boards, GPIO.HIGH)
		#the 3 first bytes are "softspan words", 3 bits per channel. The last 0s are to enable a transaction (fill the buffer with 0s, have values returned)
		r = spiBoards.xfer([0b00000000,0b00000001,0b10110110,0,0,0,0,0,0])
		GPIO.output(cnv_boards,GPIO.LOW)
		if phase == 0:
			intVal = self.getIntVal(r[0], r[1])
		elif phase == 1:
			intVal = self.getIntVal(r[2], r[3])
		else:
			intVal = self.getIntVal(r[4], r[5])
		voltage = intVal * float(10) / 32768
		return voltage

	#intermediate step in reading ADC
	def getIntVal(self,r0, r1):
		r = (r0 << 8) + r1
		if (r & (1 << 15)) != 0:
			r = r - (1 << 16)
		return r

	#write a specific value (within +/-10V) to one DAC channel
	def set_dac(self,phase, voltage):
		GPIO.output(clr,GPIO.LOW)
		GPIO.output(clr,GPIO.HIGH)
		GPIO.output(ldac,GPIO.HIGH)
		spiBoards.xfer([0b10001111,0b00000000,0b00000011])
		GPIO.output(ldac,GPIO.LOW)
		GPIO.output(ldac,GPIO.HIGH)
		byte1, byte2 = self.valueToBytes(voltage)
		if phase == 0:
			t = spiBoards.xfer([0b00110000,byte1,byte2])
		elif phase == 1:
			t = spiBoards.xfer([0b00110010,byte1,byte2])
		elif phase == 2:
			t = spiBoards.xfer([0b00110100,byte1,byte2])
		GPIO.output(ldac,GPIO.LOW)
		GPIO.output(ldac,GPIO.HIGH)	
	
	#intermediate step in writing to DAC
	def valueToBytes(self,value):
		value = float(10 + value) / 20
		value = int(value * 65535)
		firstByte = (value >> 8) & 0xFF
		secondByte = value & 0xFF
		return firstByte, secondByte

	#set the setpoint for LED current for the eLED in mA. Max 120mA. 
	def set_LEDCurrent(self,current):
		valueToWrite = int(float(current) / 120 * 4096)
		led_dac.set_voltage(valueToWrite)
		print("Set eLED current to {}".format(current))	

	#read TEC temperature
	def read_TECTemperature(self):
		voltage = tec_adc.read_adc(0, gain=1)
		#transfer function to convert ADC reading to temp
		voltage = float(voltage)/2048 * 4.096
		Rth = (float(3.3)/voltage * 1240) - 1240
		temp = log(float(Rth)/10000)* 1/float(3450) + 1/float(298)
		temp = float(1)/temp - 273
		return temp

	def set_TECTemperature(self,setpoint):
		#reversing the transfer function to get V
		#there isn't a clear proportional relation between V and the temperature despite the known equation, so adding proportional constants here
		if setpoint>22 and setpoint<=25:
			k = 0.5
		elif setpoint <= 22:
			k = 0.1
		else:
			k = 1
		setpointInK = k*setpoint + 273 
		RthForSetpoint = 10000*exp(3450*(float(1)/setpointInK - float(1)/298))
		VForSetpointReading = float(3.3*1240)/(RthForSetpoint + 1240)
		print("V for setpoint: {}".format(VForSetpointReading))
		VForSetpointReading = int(float(VForSetpointReading)/3.3 * 4096)
		tec_dac.set_voltage(VForSetpointReading)
		

	#read 1ch temperature
	def read_temperatureSensor(self,phase):
		if phase == 1:
			GPIO.output(t1,GPIO.LOW)
			temp = transmitter1.read_channel_temp()
			GPIO.output(t1,GPIO.HIGH)
		elif phase == 2:
			GPIO.output(t2,GPIO.LOW)
			temp = transmitter2.read_channel_temp()
			GPIO.output(t2,GPIO.HIGH)
		else:
			GPIO.output(t3,GPIO.LOW)
			temp = transmitter3.read_channel_temp()
			GPIO.output(t3,GPIO.HIGH)
		return temp

	#turn indicator LEDs on or off
	def set_indicator_LED(self,led, state):
		if led == 1:
			GPIO.output(led1, state)
		elif led == 2:
			GPIO.output(led2, state)
		elif led == 3:
			GPIO.output(led3, state)
		else:
			GPIO.output(led4, state)

	def quit(self):
		GPIO.cleanup()
		spiAdc.close()
		spiBoards.close()

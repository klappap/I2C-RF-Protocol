# i2c.py

import smbus
import time
import sys
import math
import os
import RPi.GPIO as GPIO
import csv

# Variables
freq = 10 # in seconds
dur = 1.0/freq

bus = smbus.SMBus(1)
RF_ADDRESS = 0x36 # 7 bit address will shift for read/write bit
config = 0b01100001 # AIN0
#config = 0b01100011 # AIN1

def writeRF(register,value):
	bus.write_byte_data(RF_ADDRESS, register, value)
	return -1

def readRF():
	msg = bus.read_word_data(RF_ADDRESS, config)

	# First In/First Out
	# prints as [lsb][msb] NEED TO CONVERT
	RF_combined = (((msg & 0xFF) << 8) | ((msg & 0xFF00) >> 8)) - 64512
	# 2 Bytes: 6 are high | Then MSB to LSB consecutively
	
	return RF_combined

def initRF():
        
	#initialise the RF Sensor
	writeRF(RF_ADDRESS, config)  #RF Enabled, continuous update,  22.2ksps conversion rate

# Decide what bus to use depending on version of RPi
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
	bus = smbus.SMBus(1)
else:
	bus = smbus.SMBus(0)

# I2C Slave Address
rf = 0x36 # Hexadecimal
sa = 0b0110110 # Binary

# Setup Byte data (8 bits)
# AIN0 + | AIN1 -
# Use 0x00 for Register bit (Table 1 & 2)
setup = 0b10000011 # Internal Clock
hs_mode = 0b00001111 #0000 1XXXX 

# Data Logging
gg = 0
while os.path.exists("/home/pi/Documents/rf/Log_Files/rf_log%s.csv" % gg):
	gg+=1

header_string = "time_now,Output\n"
fh = open("/home/pi/Documents/rf/Log_Files/rf_log%s.csv" % gg,"a")
print('rf_log%s.csv' % gg)
fh.write(header_string)
fh.close()

time_start = time.time()
timer = 0
if __name__ == "__main__":
	print "Starting Main..."
	
	try:	
		initRF()
		time.sleep(1)
		while True:
			time_now = time.time()-time_start # pi time zeroed
			if ((time_now-timer) > dur):
				RF_combined = readRF()
					
				print
				print '  RF Output New '
				print '__________________'
				print 'Time %.2f seconds' % time_now	
				print '10 bits: {0:04X}'.format(RF_combined)
				print 'Decimal Output %d' % RF_combined
				print '__________________'
				print

				log_data = [time_now,RF_combined] # log pi time and bit data
				
				# Write to file
				fh = open("/home/pi/Documents/rf/Log_Files/rf_log%s.csv" % gg, "a")
				with fh:
					writer = csv.writer(fh)
					writer.writerow(log_data)
				fh.close()
				
				timer = time_now
			
	except KeyboardInterrupt:
		sys.exit()


#!/usr/bin/env python

#
# Copyright 2013 Michael Saunby
# Copyright 2013-2015 Thomas Ackermann
# Copyright 2015 Junkai Lu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Read sensors from the TI SensorTag CC 2650. It's a
# BLE (Bluetooth low energy) device so by
# automating gatttool (from BlueZ 5.4) with
# pexpect (2.3).
#
# Usage: sensortag_test.py BLUETOOTH_ADR
#
# To find the address of your SensorTag run 'sudo hcitool lescan'
# To power up your bluetooth dongle run 'sudo hciconfig hci0 up'
#

#
# SensorTag CC2650 handles
#
# IR Temperature: char-write-cmd 0x24 01: enable IR temperature sensor
#		  char-read-hnd 0x21: read IR temperature data
#       Humidity: char-write-cmd 0x2c 01: enable humidity sensor
#  	          char-read-hnd 0x29: read humidity data
#      Barometer: char-write-cmd 0x34 01: enable barometer
#                 char-read-hnd 0x31: read barometer data
#  Ambient Light: char-write-cmd 0x44 01: enable light sensor
#                 char-read-hnd 0x41: read light sensor data
#

import os
import sys
import time
import pexpect
from datetime import datetime

sys.path.append('../.')
from sensortag_funcs import *

adr = sys.argv[1]

logdir = "/tmp/pihome"
try:
  os.mkdir(logdir)
except:
  pass

cnt = 0
it = 0
at = 0
ht = 0
pt = 0
hu = 0
pr = 0
lt = 0
exc = 0
act = 0
post = ""
stamp = ""
handle = ""

def log_values():
  print adr, " IRTMP %.1f" % it
  print adr, " AMTMP %.1f" % at
  print adr, " HUMID %.1f" % hu
  print adr, " BAROM %.1f" % pr
  print adr, " AMTLT %.1f" % lt
  print adr, " STAMP '%s'" % stamp

  # data = open(logdir+"/"+adr, "w")
  # data.write(" POST 0x%s\n" % post)
  # data.write("IRTMP %.1f\n" % it)
  # data.write("AMTMP %.1f\n" % at)
  # data.write("HMTMP %.1f\n" % ht)
  # data.write("BRTMP %.1f\n" % pt)
  # data.write("HUMID %.0f\n" % hu)
  # data.write("BAROM %.0f\n" % pr)
  # data.write("EXCPT %d\n" % exc)
  # data.write("ACTEX %d\n" % act)
  # data.write("STAMP '%s'\n" % stamp)
  # data.close()

while True:

  try:
  	
    print adr, " Trying to connect. You might need to press the side button ..."
    pexpect.spawn('hcitool lecc ' + adr)
    tool = pexpect.spawn('gatttool -b ' + adr + ' --interactive')
    tool.expect('\[LE\]>')
    tool.sendline('connect')

    print adr, " Enabling sensors ..."

    # enable IR temperature sensor
    tool.sendline('char-write-cmd 0x24 01')
    tool.expect('\[LE\]>')

    # enable humidity sensor
    tool.sendline('char-write-cmd 0x2c 01')
    tool.expect('\[LE\]>')

    # enable barometric pressure sensor
    tool.sendline('char-write-cmd 0x34 01')
    tool.expect('\[LE\]>')
    
    # enable ambient light sensor
    tool.sendline('char-write-cmd 0x44 01')
    tool.expect('\[LE\]>')

    # wait for the sensors to become ready
    time.sleep(1)

    while True:

        # read IR temperature sensor
        tool.sendline('char-read-hnd 0x21')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawObjT = long(float.fromhex(v[2] + v[1]))
        rawAmbT = long(float.fromhex(v[4] + v[3]))
        (at, it) = calcTmp(rawAmbT, rawObjT)

        # read humidity sensor
        tool.sendline('char-read-hnd 0x29')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawT = long(float.fromhex(v[2] + v[1]))
        rawH = long(float.fromhex(v[4] + v[3]))
        (ht, hu) = calcHum(rawT, rawH)

        # read barometric pressure sensor
        tool.sendline('char-read-hnd 0x31')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawP = long(float.fromhex(v[6] + v[5] + v[4]))
        pr = calcBaro(rawP)

        # read ambient light sensor
        tool.sendline('char-read-hnd 0x41')
        tool.expect('descriptor: .*? \r') 
        v = tool.after.split()
        rawL = long(float.fromhex(v[2] + v[1]))
        lt = calcLight(rawL)		
		
        cnt = cnt + 1

        stamp = datetime.now().ctime()
        act = 0

        log_values()

        time.sleep(3)

  except KeyboardInterrupt:
    tool.sendline('quit')
    tool.close()
    sys.exit()

  except:
    if handle != "":
        pexpect.run('sudo hcitool ledc ' + handle)
    tool.sendline('quit')
    tool.close(force=True)
    exc = exc + 1
    act = 1
    log_values()


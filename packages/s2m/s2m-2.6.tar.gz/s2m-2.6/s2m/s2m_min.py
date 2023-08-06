"""
 Copyright (c) 2017-2018 Alan Yorinks All rights reserved.
 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import argparse
import atexit
import binascii
import glob
import os
import subprocess
import sys
import time
from argparse import RawTextHelpFormatter
from subprocess import Popen
import psutil
import serial
try:
 from s2m.s2m_http_server import start_server
except ImportError:
 from s2m_http_server import start_server
class S2M:
 def __init__(self,client=None,com_port=None,scratch_executable=None,base_path=None,display_base_path=False,language='0'):
  self.daemon=True
  self.client=client
  self.com_port=com_port
  self.scratch_executable=scratch_executable
  self.base_path=base_path
  self.display_base_path=display_base_path
  self.language=language
  self.scratch_pid=None
  self.scratch_project=None
  self.ser=None
  self.last_z=0
  self.ignore_poll=True
  self.last_poll_result=None
  self.micro_bit_serial=None
  self.image_map={"01":"HAPPY","02":"SAD","03":"ANGRY","04":"SMILE","05":"HEART","06":"CONFUSED","07":"ASLEEP","08":"SURPRISED","09":"SILLY","10":"FABULOUS","11":"MEH","12":"YES","13":"NO","14":"TRIANGLE","15":"DIAMOND","16":"DIAMOND_SMALL","17":"SQUARE","18":"SQUARE_SMALL","19":"TARGET","20":"STICKFIGURE","21":"RABBIT","22":"COW","23":"ROLLERSKATE","24":"HOUSE","25":"SNAKE","26":"ARROW_N","27":"ARROW_NE","28":"ARROW_E","29":"ARROW_SE","30":"ARROW_S","31":"ARROW_SW","32":"ARROW_W","33":"ARROW_NW"}
  print('\ns2m version 2.5  Copyright(C) 2018 Alan Yorinks  All rights reserved.')
  print("\nPython Version %s"%sys.version)
  atexit.register(self.all_done)
  if com_port is None:
   print('Autodetecting serial port. Please wait...')
   if sys.platform.startswith('darwin'):
    locations=glob.glob('/dev/tty.[usb*]*')
    locations=glob.glob('/dev/tty.[wchusb*]*')+locations
    locations.append('end')
   else:
    locations=['dev/ttyACM0','/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyACM4','/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3','/dev/ttyUSB4','/dev/ttyUSB5','/dev/ttyUSB6','/dev/ttyUSB7','/dev/ttyUSB8','/dev/ttyUSB9','/dev/ttyUSB10','/dev/ttyS0','/dev/ttyS1','/dev/ttyS2','/dev/tty.usbserial','/dev/tty.usbmodem','com2','com3','com4','com5','com6','com7','com8','com9','com10','com11','com12','com13','com14','com15','com16','com17','com18','com19','com20','com21','com22','com23','com24','com25','com26','com27','com28','com29','com30','com31','com32','com33','com34','com35','com36','com1','end']
   detected=None
   for device in locations:
    try:
     self.micro_bit_serial=serial.Serial(port=device,baudrate=115200,timeout=.1)
     detected=device
     break
    except serial.SerialException:
     if device=='end':
      print('Unable to find Serial Port, Please plug in ' 'cable or check cable connections.')
      detected=None
      exit()
    except OSError:
     pass
   self.com_port=detected
   self.micro_bit_serial.close()
   self.micro_bit_serial.open()
   time.sleep(.05)
  else:
   try:
    self.micro_bit_serial=serial.Serial(port=self.com_port,baudrate=115200,timeout=.1)
   except serial.SerialException:
    print('Unable to find Serial Port, Please plug in ' 'cable or check cable connections.')
    exit()
   except OSError:
    pass
   time.sleep(.05)
  cmd='g\n'
  cmd=bytes(cmd.encode())
  self.micro_bit_serial.write(cmd)
  time.sleep(2)
  sent_time=time.time()
  while not self.micro_bit_serial.inWaiting():
   if time.time()-sent_time>2:
    print('Unable to detect Serial Port, Please plug in ' 'cable or check cable connections.')
    sys.exit(0)
  self.last_poll_result=self.micro_bit_serial.readline().decode().strip()
  print('{}{}\n'.format('Using COM Port:',self.com_port))
  cmd='v\n'
  cmd=bytes(cmd.encode())
  self.micro_bit_serial.write(cmd)
  time.sleep(2)
  sent_time=time.time()
  while not self.micro_bit_serial.inWaiting():
   if time.time()-sent_time>2:
    print('Unable to retrieve version s2mb.py on the micro:bit.')
    print('Have you flashed the latest version?')
    sys.exit(0)
  v_string=self.micro_bit_serial.readline().decode().strip()
  print('{}{}\n'.format('s2mb Version: ',v_string))
  if self.client=='scratch':
   self.find_base_path()
   print('Auto launching Scratch')
   self.auto_load_scratch()
  else:
   print('Please start Scratch.')
  self.ignore_poll=False
  try:
   start_server(self)
  except KeyboardInterrupt:
   sys.exit(0)
 def find_base_path(self):
  if not self.base_path:
   path=sys.path
   if not sys.platform.startswith('darwin'):
    prefix=sys.prefix
    for p in path:
     if prefix in p:
      s_path=p+'/s2m'
      if os.path.isdir(s_path):
       self.base_path=p+'/s2m'
   else:
    for p in path:
     s_path=p+'/s2m'
     if os.path.isdir(s_path):
      self.base_path=p+'/s2m'
   if not self.base_path:
    print('Cannot locate s2m files on path.')
    print('Python path = '+str(self.base_path))
    sys.exit(0)
   if self.display_base_path:
    print('Python path = '+str(self.base_path))
    sys.exit(0)
 def auto_load_scratch(self):
  if self.scratch_executable=='default':
   if sys.platform.startswith('win32'):
    self.scratch_executable="C:/Program Files (x86)/Scratch 2/Scratch 2.exe"
   elif sys.platform.startswith('darwin'):
    self.scratch_executable="/Applications/Scratch\ 2.app/Contents/MacOS/Scratch\ 2"
   else:
    self.scratch_executable="/opt/Scratch\ 2/bin/Scratch\ 2"
  if self.language=='0':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m.sb2"
  elif self.language=='1':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ja.sb2"
  elif self.language=='ja':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ja.sb2"
  elif self.language=='2':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ko.sb2"
  elif self.language=='ko':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ko.sb2"
  elif self.language=='3':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_tw.sb2"
  elif self.language=='tw':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_tw.sb2"
  elif self.language=='4':
   self.scratch_project=self.base_path+"/scratch_files/projects/motion_tw.sb2"
  elif self.language=='tws':
   self.scratch_project=self.base_path+"/scratch_files/projects/motion_tw.sb2"
  elif self.language=='5':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ptbr.sb2"
  elif self.language=='ptbr':
   self.scratch_project=self.base_path+"/scratch_files/projects/s2m_ptbr.sb2"
  elif self.language=='6':
   self.scratch_project=self.base_path+"/scratch_files/projects/motion_ptbr.sb2"
  elif self.language=='ptbrs':
   self.scratch_project=self.base_path+"/scratch_files/projects/motion_ptbr.sb2"
  exec_string=self.scratch_executable+' '+self.scratch_project
  if self.scratch_executable and self.scratch_project:
   if sys.platform.startswith('win32'):
    scratch_proc=Popen(exec_string,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    self.scratch_pid=scratch_proc.pid
   else:
    exec_string=self.scratch_executable+' '+self.scratch_project
    scratch_proc=Popen(exec_string,shell=True)
    self.scratch_pid=scratch_proc.pid
  else:
   print('You must provide scratch executable information')
 def handle_poll(self):
  self.ignore_poll=True
  resp=self.send_command('g')
  resp=resp.lower()
  reply=resp.split(',')
  if len(reply)!=12:
   print('the reply',reply)
   return ''
  resp=self.build_poll_response(reply)
  print('poll response',resp)
  return resp
 def handle_display_image(self,data):
  key=data
  if len(data)>2:
   if data[2]=='_':
    key=data[:2]
  if key in self.image_map:
   data=self.image_map[key]
  self.send_command('d,'+data)
 def handle_scroll(self,data):
  data=self.scratch_fix(data)
  self.send_command('s,'+data)
 def handle_write_pixel(self,data):
  self.send_command('p,'+data)
 def handle_display_clear(self):
  self.send_command('c')
 def handle_digital_write(self,data):
  self.send_command('t,'+data)
 def handle_analog_write(self,data):
  self.send_command('a,'+data)
 def handle_reset_all(self):
  self.send_command('t,0,0')
  self.send_command('t,1,0')
  self.send_command('t,2,0')
  self.send_command('a,0,0')
  self.send_command('a,1,0')
  self.send_command('a,2,0')
  self.send_command('c')
 def build_poll_response(self,data_list):
  reply=''
  x=int(data_list[0])
  y=int(data_list[1])
  z=int(data_list[2])
  if x>0:
   right='true'
   left='false'
  else:
   right='false'
   left='true'
  if y>0:
   up='true'
   down='false'
  else:
   up='false'
   down='true'
  z_diff=abs(z-self.last_z)
  if z_diff>2000:
   reply+='shaken true\n'
  else:
   reply+='shaken false\n'
  self.last_z=z
  reply+='tilted_right '+right+'\n'
  reply+='tilted_left '+left+'\n'
  reply+='tilted_up '+up+'\n'
  reply+='tilted_down '+down+'\n'
  reply+='button_a_pressed '+data_list[3]+'\n'
  reply+='button_b_pressed '+data_list[4]+'\n'
  reply+='digital_read/0 '+data_list[5]+'\n'
  reply+='digital_read/1 '+data_list[6]+'\n'
  reply+='digital_read/2 '+data_list[7]+'\n'
  reply+='analog_read/0 '+data_list[8]+'\n'
  reply+='analog_read/1 '+data_list[9]+'\n'
  reply+='analog_read/2 '+data_list[10]+'\n'
  return reply
 def send_command(self,command):
  try:
   cmd=command+'\n'
   self.micro_bit_serial.write(cmd.encode())
  except serial.SerialTimeoutException:
   return command
  if command=='g':
   while not self.micro_bit_serial.inWaiting():
    pass
   data=self.micro_bit_serial.readline().decode().strip()
   print('poll return',data)
   return data
 def all_done(self):
  if self.scratch_pid:
   proc=psutil.Process(self.scratch_pid)
   proc.kill()
 def scratch_fix(self,sst):
  result=''
  x=0
  while x<len(sst):
   if sst[x]=='%':
    sx=sst[x+1]+sst[x+2]
    z=binascii.unhexlify(sx)
    try:
     result+=z.decode("utf-8")
    except UnicodeDecodeError:
     print('Warning: Scroll text must be in Roman characters')
     return 'Scroll text must be in Roman characters'
    x+=3
   else:
    result+=sst[x]
    x+=1
  return result
def main():
 parser=argparse.ArgumentParser(description='s2m',formatter_class=RawTextHelpFormatter)
 parser.add_argument("-b",dest="base_path",default="None",help="Python File Path - e.g. /usr/local/lib/python3.5/dist-packages/s2m")
 parser.add_argument("-c",dest="client",default="scratch",help="default = scratch [scratch | no_client]")
 parser.add_argument("-d",dest="display",default="None",help='Show base path - set to "true"')
 parser.add_argument("-l",dest="language",default="0",help="Select Language: \n0 = English(default)\n1 or ja = Japanese\n" "2 or ko = Korean\n3 or tw = Traditional Chinese" "\n4 or tws = Traditional Chinese Sample Project" "\n5 or ptbr = Brazilian Portuguese" "\n6 or ptbrs = Brazilian Portugues Sample Project")
 parser.add_argument("-p",dest="comport",default="None",help="micro:bit COM port - e.g. /dev/ttyACMO or COM3")
 parser.add_argument("-r",dest="rpi",default="None",help="Set to TRUE to run on a Raspberry Pi")
 parser.add_argument("-s",dest="scratch_exec",default="default",help="Full path to Scratch executable")
 args=parser.parse_args()
 if args.base_path=='None':
  user_base_path=None
 else:
  user_base_path=args.base_path
 if args.display=='None':
  display=False
 else:
  display=True
 client_type=args.client
 if args.comport=='None':
  comport=None
 else:
  comport=args.comport
 valid_languages=['0','1','ja','2','ko','3','tw','4','tws','5','ptbr','6','ptbrs']
 lang=args.language
 if lang not in valid_languages:
  lang='0'
 scratch_exec=args.scratch_exec
 if args.rpi!='None':
  scratch_exec='/usr/bin/scratch2'
 S2M(client=client_type,com_port=comport,scratch_executable=scratch_exec,base_path=user_base_path,display_base_path=display,language=lang)
if __name__=="__main__":
 try:
  main()
 except KeyboardInterrupt:
  sys.exit(0)
# Created by pyminifier (https://github.com/liftoff/pyminifier)

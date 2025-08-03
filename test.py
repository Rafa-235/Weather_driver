#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test.py
#  
#  Copyright 2024  <rafa@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
from smbus2 import SMBus
import time

bus = SMBus(1)
addr1 = 0x20
addr2 = 0x24
IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13

#bus.write_byte_data(addr1, IODIRA, 0x00)
#bus.write_byte_data(addr1, IODIRB, 0x00)

#bus.write_byte_data(addr2, IODIRA, 0x00)
#bus.write_byte_data(addr2, IODIRB, 0x00)
digit_ports = [1, 2, 4, 8]
# segment patterns (1 means segment should be on/low)
segment_patterns = {

    0: ~(0b10111111),
    1: ~(0b110),
    2: ~(0b1011011),
    3: ~(0b1001111),
    4: ~(0b1100110),
    5: ~(0b1101101),
    6: ~(0b11111101),
    7: ~(0b111),
    8: ~(0b101111111),
    9: ~(0b11101111),
    'H': ~(0b1110110),
    'L': ~(0b111000),
    'I': ~(0b110000),
    '-': ~(0b1000000)
    
    }
        
def turn_segment1(pattern, stop_event=None):
    hz = 1/1000000
    hz_off = 1/2000
    

    for i in range(4):
        
        if stop_event and stop_event.is_set():
            return
            
            
        bus.write_byte_data(addr1, GPIOA, 0xFF)
            
        bus.write_byte_data(addr1, GPIOB, pattern[i])
        time.sleep(hz_off)
            
        bus.write_byte_data(addr1, GPIOA, ~digit_ports[i]) #turns one digit on at a time
        time.sleep(hz)

def turn_segment2(pattern, stop_event=None):
    hz = 1/1000000
    hz_off = 1/2000
    
    for i in range(4):
        
        if stop_event and stop_event.is_set():
            return
            
        bus.write_byte_data(addr2, GPIOA, 0xFF)
            
        bus.write_byte_data(addr2, GPIOB, pattern[i])
        time.sleep(hz_off)
            
        bus.write_byte_data(addr2, GPIOA, ~digit_ports[i]) #turns one digit on at a time
        time.sleep(hz)


def clear_seg1():
    bus.write_byte_data(addr1, IODIRA, 0x00)
    bus.write_byte_data(addr1, IODIRB, 0x00)
    
    
def clear_seg2():
    bus.write_byte_data(addr2, IODIRA, 0x00)
    bus.write_byte_data(addr2, IODIRB, 0x00)



def clear_all():
    clear_seg1()
    clear_seg2()


#def main():
 #   while True:
  #      pattern1 = [
   #             segment_patterns[0],
    #            segment_patterns[2],
     #           segment_patterns[3],
      #          segment_patterns[4]]
       # turn_segment2(pattern1)



    
if __name__ == '__main__':
    main()



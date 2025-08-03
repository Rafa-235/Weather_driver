from bs4 import BeautifulSoup
import requests
from RPLCD import CharLCD, cleared, cursor
import RPi.GPIO as GPIO
import time
from test import *
import threading
import schedule

#Global vars

stop_event = threading.Event()
active_threads = []
display_active = False

GPIO.setwarnings(False)
lcd = CharLCD(cols=16,rows=2, pin_rs=26, pin_e=19, pins_data=[14, 15, 18, 23, 24, 25, 8, 7], pin_backlight=13, numbering_mode = GPIO.BCM, compat_mode=True)

def get_weather():
	doc = "https://weather.com/weather/today/l/53db9aa91a002e6647abce4740fdb46a005b696c15e7c56177bedafa7674dab8"
	response = requests.get(doc)
	soup = BeautifulSoup(response.text, 'html.parser')

	temps = soup.find_all('span', attrs={'data-testid': 'TemperatureValue'})
	curr = temps[0]
	curr_temp = clean_string(str(curr.text.split()))

	high = temps[1]
	high_temp = clean_string(str(high.text.split()))

	low = temps[2]
	low_temp = clean_string(str(low.text.split()))

	cond = soup.find('div', attrs={'data-testid': 'wxPhrase'})
	curr_conditions = clean_string(cond.text.split())

	feels = temps[7]
	feels_like_temp = clean_string(str(feels.text.split()))
	


	return curr_temp, high_temp, low_temp, feels_like_temp, curr_conditions


def clean_string(string):
	if isinstance(string, list):
		if (len(string) > 1):
			y = string[0] + " " + string[1]
		else:
			y = string[0]
	if isinstance(string, str):
		x = string.lstrip('[\'')
		y = x.rstrip(chr(176)+'\']')
	return y

def split(high, low):
	high_list = [int(digit) for digit in high]
	if (len(high_list) > 2):
		high_list[0], high_list[1] = 9
	low_list = [int(digit) for digit in low]
	return high_list, low_list

def write_display(*args):
	degree = (
		0b01100,
		0b10010,
		0b10010,
		0b01100,
		0b00000,
		0b00000,
		0b00000,
		0b00000
		)
	lcd.create_char(0, degree)
	lcd.clear()
	lcd.cursor_pos = (0,1)
	if len(args) == 3:
		lcd.cursor_pos = (0,3)
		lcd.write_string("Curr Time:")
		print(args[0])
		lcd.cursor_pos = (1,4)
		lcd.write_string(args[0])
		time.sleep(5)
		lcd.clear()
	if len(args) == 1:
		lcd.write_string("Curr Temp is:")
		lcd.cursor_pos = (1,6)
		lcd.write_string(args[0] + chr(0) + "F")
		print(args[0])
		time.sleep(5)
		lcd.clear()
	if len(args) == 2:
		lcd.cursor_pos = (0,0)
		lcd.write_string("Curr Conditions:")
		lcd.cursos_pos = (1,0)
		lcd.write_string(args[1])
		print(args[1])
		time.sleep(5)
		lcd.clear()
		lcd.cursor_pos = (0,2)
		lcd.write_string("Feels like:")
		lcd.cursor_pos = (1,6)
		lcd.write_string(args[0] + chr(0) + "F")
		print(args[0])
		time.sleep(4)
	
def loop_lcd():
	last_update = 0
	day_curr = day_feels_like = day_conditions = ''
	while not stop_event.is_set():
		time_24 = time.ctime().split()[3]
		hour, minute, second = time_24.split(':')
		hour = int(hour)
		if hour == 0:
			current_time = f"12:{minute} AM"
		elif hour < 12:
			current_time = f"12:{minute} AM"
		elif hour == 12:
			current_time = f"12:{minute} PM"
		else:
			current_time = f"{hour-12}:{minute} PM"
		if time.time() - last_update > 60:
			day_curr, day_high, day_low, day_feels_like, day_conditions = get_weather()
			last_update = time.time()
		write_display(current_time, day_curr, day_feels_like)
		time.sleep(.1)
		write_display(day_curr)
		time.sleep(.1)
		write_display(day_feels_like, day_conditions)
		time.sleep(.1)

def loop_seg1():
	last_update = 0
	day_high = day_low = ''
	while not stop_event.is_set():
		if time.time() - last_update > 60:
			day_curr, day_high, day_low, day_feels_like, day_conditions = get_weather()
			last_update = time.time()
		high_temp, low_temp = split(day_high, day_low)
		pattern1 = [
			segment_patterns['H'],
			segment_patterns['I'],
			segment_patterns[high_temp[0]],
			segment_patterns[high_temp[1]]
		]
		turn_segment1(pattern1, stop_event)

	
	
def loop_seg2():
	last_update = 0
	day_high = day_low = ''
	while not stop_event.is_set():
		if time.time() - last_update > 60:
			day_curr, day_high, day_low, day_feels_like, day_conditions = get_weather()
			last_update = time.time()
		high_temp, low_temp = split(day_high, day_low)
		pattern2 = [
			segment_patterns['L'],
			segment_patterns[0],
			segment_patterns[low_temp[0]],
			segment_patterns[low_temp[1]]
		]
		turn_segment2(pattern2, stop_event)
	

def lcd_off():
	lcd.clear()
	GPIO.setmode(GPIO.BCM)
	backlight_pin = 13
	GPIO.setup(backlight_pin, GPIO.OUT)
	GPIO.output(backlight_pin, GPIO.LOW)
	
def lcd_on():
	backlight_pin = 13
	GPIO.setup(backlight_pin, GPIO.OUT)
	GPIO.output(backlight_pin, GPIO.HIGH)

def leds_off():
	bus.write_byte_data(addr1, IODIRA, 0xFF)
	bus.write_byte_data(addr1, IODIRB, 0xFF)

	bus.write_byte_data(addr2, IODIRA, 0xFF)
	bus.write_byte_data(addr2, IODIRB, 0xFF)


def toggle_display():
	global display_active
	
	if display_active:
		function_off()
		display_active = False
		
	else:
		main_func()
		display_active = True



def main_func():
	global active_threads
	stop_event.clear()
	
	lcd_on()
	bus.write_byte_data(addr1, IODIRA, 0x00)
	bus.write_byte_data(addr1, IODIRB, 0x00)

	bus.write_byte_data(addr2, IODIRA, 0x00)
	bus.write_byte_data(addr2, IODIRB, 0x00)
	
	
	thread1 = threading.Thread(target=loop_lcd)
	thread2 = threading.Thread(target=loop_seg1)
	thread3 = threading.Thread(target=loop_seg2)
	
	active_threads = [thread1, thread2, thread3]
	print(active_threads)
	thread1.start()
	thread2.start()
	thread3.start()
	
	
def stop_threads():
	global active_threads
	stop_event.set()
	for thread in active_threads:
		if thread.is_alive():
			thread.join(timeout=5)
	active_threads = []
	print(active_threads)


def function_off():
	display_active = False;
	stop_threads()
	lcd_off()
	leds_off()



def main():
	function_off()
	#display_active = False;
	
	START_TIME = '09:00'
	END_TIME = '10:00'
	
	schedule.every().day.at(START_TIME).do(main_func)
	
	schedule.every().day.at(END_TIME).do(function_off)
	
	
	while True:
		schedule.run_pending()
		time.sleep(1)


if __name__ == "__main__":
	main()

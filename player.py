#-*- coding: utf-8 -*-

import os
import re
import time

last_URI=''
play_conf='/root/play/plt.txt'

def is_running():
	
	return True

def stop_player():
	cmdstr='killall tvplayer.sh'
	os.system(cmdstr)
	cmdstr='killall omxplayer.bin'
	os.system(cmdstr)
	time.sleep(1)
	

def start_player(URI):
	stop_player()
	last_URI=URI
	if len(URI)>0:		
		if URI == 'TV':
			os.system('/root/play/tvplayer.sh http://localhost/index.m3u8 &')			
		else:
			playcmd='/root/play/tvplayer.sh %s &'%URI
			os.system(playcmd)
			

def start_check_player():
	last_info=''
	while True:
		if os.path.exists(play_conf):
			f.open(play_conf,'r')
			info=f.read(300)
			f.close()
			if info != last_info:
				last_info = info
				if len(info)>0:
					start_player(info)
				else:
					stop_player()
			else:
				time.sleep(1)
				
			
		
					
				 
	
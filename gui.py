#-*- coding=utf-8 -*-
# Import a library of functions called 'pygame'
import pygame
import Image
import re
import os
import time
import httplib2
import player
import getvideoinfos
import json
import random
import PPlive
import evdev
import threading
import download

	
windows_infos={}
menu_infos=[]
pic_infos=[]
menu_type_list=['hlstv',"qq","youku","tudou"]
menu_focus= 0;

pic_focus = 0;
pic_w = 96
pic_h = 96
pic_size=(pic_w,pic_h)
pic_start_index = 0
pic_end_index = 0
total_pic_infos = 0
menu_w = 96
menu_h = 32
menu_size=(menu_w,menu_h)

ratio_w = 1.0
ratio_h = 1.0

menu_start =(50,8)
pic_start = (50,76)
search_bar_start =(360,44)

word_offset_x = 0
word_offset_y = 0

black = [  0,  0,  0]
white = [255,255,255]
blue =  [  0,  0,255]
green = [  0,255,  0]
red =   [255,  0,  0]

pi=3.141592653

keywords="qwertyuiop asdfghjkl* zxcvbnm "
kb_startx= 160
kb_starty = 200
key_w = 32
key_h = 32
is_key_show = 0
kb_pos = 0;
kb_total_num = 0;

kb_input_vals=''
kb_out_words=''
kb_out_words_pos=0
kb_ch_words = []
kb_ch_pos = []
search_words=''

sougou_key_url = 'http://web.pinyin.sogou.com/web_ime/patch.php'
sougou_input_url='http://web.pinyin.sogou.com/api/py?key=938cdfe9e1e39f8dd5da428b1a6a69cb&query='

qq_key_url = 'http://ime.qq.com/fcgi-bin/getkey?cb=window.QQWebIME.keyback696'
qq_input_url = 'http://ime.qq.com/fcgi-bin/getword?key=%s&cb=window.QQWebIME.callback696&q=%s'
qq_key_s = ''


videos=[]
pygame_init=False
download_manage=download.ThreadDownloadManage()

def get_kbelement_by_pos(x,y):
	global kb_startx
	global kb_starty
	global search_bar_start
	s_x,s_y = search_bar_start

	if x>s_x and y>s_y and x<s_x+200 and y<s_y+26:
		return "search_bar"
	elif x>kb_startx and y>kb_starty and x<kb_startx+11*key_w and y<kb_starty+32*3:
		return "kb"
	elif x>kb_startx and y>kb_starty-64 and x<kb_startx+342 and y<kb_starty-32:
		return "kw"
	else :
		return ""
		
def get_kbelement_index_by_pos(x,y,t):
	global kb_startx
	global kb_starty
	global kb_ch_pos
	if 'kb' == t:
		x = (x-kb_startx)/32
		y= (y-kb_starty)/32
		i=(x+11*y)
		if i >= len(keywords):
			i=len(keywords)-1
		return i
	elif 'kw'==t:
		i=0
		x=x-kb_startx
		for kw_pos in kb_ch_pos:
			sx,ex=kw_pos			
			if x>sx and x<ex:				
				return i
			i += 1
		return i-1
	else:
		return 0
		
def get_element_by_pos(x,y):
	global pic_start
	global menu_start
	global search_bar_start
	p_x,p_y = pic_start
	m_x,m_y = menu_start
	s_x,s_y = search_bar_start
	if x>m_x and y>m_y and x<m_x+menu_w*len(menu_infos) and y<m_y+menu_h:
		return "menu"
	elif x>s_x and y>s_y and x<s_x+200 and y<s_y+26:
		return "search_bar"
	elif x>s_x+200 and y>s_y and x<s_x+200+26 and y<s_y+26:
		return "search_button"
	elif x>p_x and y>p_y and x<p_x+500 and y<p_y+100*((len(pic_infos)+4)/5):
		return "pic"
	else :
		return ""
	
def get_element_index_by_pos(x,y,t):
	global pic_start
	global menu_start
	global search_bar_start
	p_x,p_y = pic_start
	m_x,m_y = menu_start
	s_x,s_y = search_bar_start
	if 'menu' == t:
		x = x-m_x
		return x/menu_w
	elif 'pic' == t:
		x = (x-p_x)/100
		y= (y-p_y)/100
		return (x+5*y)
	else:
		return 0
		
def query_input(strings):
	global qq_key_s
	global kb_input_vals
	global kb_out_words
	global kb_ch_words
	h=httplib2.Http()
	ret = []
	if len(qq_key_s) < 5:		
		resp,content=h.request(qq_key_url)
		if resp.status==200:
			js = re.findall('^.*\(([^)]*)\)',content)
			print js
			j = json.loads(js[0])
			qq_key_s = j["key"]
			print qq_key_s
		else:
			return ret
	if len(qq_key_s) < 5:
		print 'get keystring error'
		return ret
	real_url = qq_input_url%(qq_key_s,strings)
	resp,content=h.request(real_url)
	if resp.status==200:
		js = re.findall('^.*\(([^)]*)\)',content)
		j = json.loads(js[0])
		return j["rs"]
	else:
		qq_key_s=''
		print 'real_url error'
		return kb_ch_words


def get_py_str(font,str):
	global kb_out_words
	global kb_ch_words
	global kb_ch_pos
	
	if len(str)<1:
		kb_out_words=''
		return kb_out_words
	kb_ch_words=query_input(str)
	i=1
	del kb_ch_pos[:]
	kb_out_words = ""
	start_ox=0
	end_ox=0
	for word in kb_ch_words:
		word = word.encode("utf-8")
		tmp = "%d."%i+word+" "
		unicode_str=unicode(tmp,'utf-8')
		word_w,word_h=font.size(unicode_str)
		end_ox=start_ox+word_w
		kb_ch_pos.append((start_ox,end_ox))
		start_ox = end_ox
		kb_out_words = kb_out_words+tmp		
		i = i+1
		if i>=9:
			break			
	return kb_out_words
	#draw_search_bar(kb_out_words)
	

def draw_search_bar(screen,font,str):
	global search_bar_start
	wx,wy = search_bar_start
	rect=[wx,wy,200,26]
	pygame.draw.rect(screen,white,rect)	
	if len(str)>0:
		unicode_str = str
		text = font.render(unicode_str,False,black,white)
		word_w,word_h=font.size(unicode_str)
		word_x=wx+4
		word_y=wy+4
		screen.blit(text, [word_x,word_y],[0,0,word_w,word_h])		
	pygame.draw.rect(screen,blue,rect,2)
	img='./search.png'
	pos=[wx+200,wy]
	img_mode,img_str=resizepic(img,(26,26))
	pyim = pygame.image.fromstring(img_str,(26,26),img_mode).convert()
	screen.blit(pyim,pos)	

def handle_kb_event(screen,font,event):
	global kb_input_vals
	global is_key_show
	global kb_pos
	global kb_total_num	
	global kb_out_words
	global kb_ch_words
	global search_words
	
	if is_key_show == 0:
		return		
	if event.type==pygame.KEYDOWN:
		if event.key == pygame.K_RIGHT:
			kb_lose_focus(screen,font,kb_pos)
			kb_pos = kb_pos +1	
			if kb_pos >= kb_total_num:
				kb_pos = 0
			draw_kb_focus(screen,font,kb_pos)
		elif event.key == pygame.K_LEFT:
			kb_lose_focus(screen,font,kb_pos)
			kb_pos = kb_pos -1
			if kb_pos < 0:
				kb_pos=kb_total_num-1
			draw_kb_focus(screen,font,kb_pos)
		elif event.key == pygame.K_UP:
			line=kb_pos/11
			col=kb_pos%11
			kb_lose_focus(screen,font,kb_pos)
			if line>0:
				line = line-1
			else:
				line = 2
			kb_pos = 11*line+col
			if kb_pos>len(keywords):
				if line>0:
					line = line-1
				else:
					line = 0
				kb_pos = 11*line+col
			draw_kb_focus(screen,font,kb_pos)		
		elif event.key == pygame.K_DOWN:
			line=kb_pos/11
			col=kb_pos%11
			kb_lose_focus(screen,font,kb_pos)
			if line<2:
				line = line+1
			else:
				line = 0
			kb_pos = 11*line+col
			if kb_pos>=len(keywords):
				if line<2:
					line = line+1
				else:
					line = 0
				kb_pos = 11*line+col
			draw_kb_focus(screen,font,kb_pos)
		elif 	event.key == pygame.K_RETURN:
			key = keywords[kb_pos]
			if key == ' ' and kb_pos == 10:
				kb_input_vals = kb_input_vals[0:-1]	
			elif key == ' ' and kb_pos == 21:
				#kb_input_vals = ''
				if len(kb_ch_words)>0:
					search_words  = search_words+kb_ch_words[0]
				kb_input_vals =''
				kb_out_words = ''
				print 'K_RETURN ',search_words
				draw_search_bar(screen,font,search_words)
			elif key == ' ':
				print 'space key'
			else:
				kb_input_vals = kb_input_vals+key
			outs = get_py_str(font,kb_input_vals)
			draw_input_words(screen,font,kb_input_vals)
			draw_output_words(screen,font,outs)
		elif event.key>= 97 and event.key <= 122:
			kb_input_vals = kb_input_vals+chr(event.key)
			outs = get_py_str(font,kb_input_vals)
			draw_input_words(screen,font,kb_input_vals)
			draw_output_words(screen,font,outs)	
	elif event.type==pygame.MOUSEBUTTONDOWN or event.type==pygame.MOUSEBUTTONUP or event.type==pygame.MOUSEMOTION:
		deal_mouse_event(screen,font,event)
	 		
			
def kb_lose_focus(screen,font,focus):
	global kb_startx
	global kb_starty
	global key_w
	global key_h
	wx=kb_startx+(focus%11)*key_w
	wy=kb_starty+(focus/11)*key_h
	rect=[wx,wy,key_w,key_h]
	pygame.draw.rect(screen,black,rect,2)
	
def draw_kb_focus(screen,font,focus):
	global kb_startx
	global kb_starty
	global key_w
	global key_h
	wx=kb_startx+(focus%11)*key_w
	wy=kb_starty+(focus/11)*key_h
	rect=[wx,wy,key_w,key_h]
	pygame.draw.rect(screen,blue,rect,2)

def draw_enter(screen,x,y):
	x1=x+8
	y1=y+18
	
	x2=x1+6
	y2=y1-4
	x3=x2
	y3=y1+4
	points=[(x1,y1),(x2,y2),(x3,y3)]
	pygame.draw.polygon(screen,black,points)
	pygame.draw.line(screen,black,(x2,y1),(x2+12,y1),2)
	pygame.draw.line(screen,black,(x2+12,y1-8),(x2+12,y1),2)
	
	
def draw_space(screen,x,y):
	x1=x+8
	y1=y+24	
	x2=x1
	y2=y1-4	
	x3=x2+16
	y3=y2
	pygame.draw.line(screen,black,(x2,y2),(x2,y1))
	pygame.draw.line(screen,black,(x3,y3),(x3,y1))
	pygame.draw.line(screen,black,(x2,y1),(x3,y1),2)
	
def draw_backspace(screen,x,y):
	x1=x+8
	y1=y+16
	
	x2=x1+6
	y2=y1-4
	x3=x2
	y3=y1+4
	points=[(x1,y1),(x2,y2),(x3,y3)]
	pygame.draw.polygon(screen,black,points)
	pygame.draw.line(screen,black,(x2,y1),(x2+12,y1),2)

def draw_input_words(screen,font,words):
	global kb_startx
	global kb_starty
	global kb_input_vals
	
	rect = [kb_startx,kb_starty-32,11*key_w,key_h]
	
	pygame.draw.rect(screen,white,rect)
	if len(words)>0:
		unicode_str = unicode(words,'utf-8')
		text = font.render(unicode_str,False,black,white)
		word_w,word_h=font.size(unicode_str)
		word_x= kb_startx+6
		word_y= kb_starty-32+6
		screen.blit(text, [word_x,word_y],[0,0,word_w,word_h])
	pygame.draw.rect(screen,black,rect,2)
	
	
	

def draw_output_words(screen,font,words):
	global kb_startx
	global kb_starty
	global kb_ch_words
	global kb_out_words_pos
	
	rect = [kb_startx,kb_starty-2*32,11*key_w,key_h]
	
	pygame.draw.rect(screen,white,rect)
	if len(words)>0:
		unicode_str = unicode(words,'utf-8')
		text = font.render(unicode_str,False,black,white)
		word_w,word_h=font.size(unicode_str)
		word_x= kb_startx+6
		word_y= kb_starty-2*32+6
		if word_w>344:
			word_w = 344		
		screen.blit(text, [word_x,word_y],[0,0,word_w,word_h])
		if kb_out_words_pos<len(kb_ch_words):
			s="%d."%(kb_out_words_pos+1)+kb_ch_words[kb_out_words_pos]
			s=s.encode('utf-8')
			ss=words
			rs=re.split(s,ss)
			if kb_out_words_pos>0:
				unicode_str = unicode(rs[0],'utf-8')
				of_w,of_h=font.size(unicode_str)
				if of_w>word_w:
					of_w = 0
					kb_out_words_pos=0
					s="%d."%(kb_out_words_pos+1)+kb_ch_words[kb_out_words_pos]
					s=s.encode('utf-8')
			else:
				of_w = 0
				of_h = 0
			unicode_str = unicode(s,'utf-8')
			word_w,word_h=font.size(unicode_str)
			text = font.render(unicode_str,False,blue,white)
			screen.blit(text, [word_x+of_w,word_y],[0,0,word_w,word_h])
		
	pygame.draw.rect(screen,black,rect,2)
	

def draw_kb(screen,font):
	global is_key_show
	global kb_total_num
	global kb_startx
	global kb_starty
	global kb_pos
	global search_words
	
	i=0;
	search_words=''
	if is_key_show != 0:
		return
	is_key_show = 1
	for key in keywords:
		wx=kb_startx+(i%11)*key_w
		wy=kb_starty+(i/11)*key_h
		i = i+1
		kb_total_num = i
		txt_w,txt_h=font.size(key)
		rect=[wx,wy,key_w,key_h]
		pygame.draw.rect(screen,white,rect)
		pygame.draw.rect(screen,black,rect,2)
		if i==11:
			draw_backspace(screen,wx,wy)
		elif i==22:
			draw_enter(screen,wx,wy)
		elif key== ' ':
			draw_space(screen,wx,wy)
		else:
			txt=font.render(key,False,black)	
			pos = (wx+((key_w-txt_w)/2),wy+((key_h-txt_h)/2))		
			screen.blit(txt,pos)
		##draw input words
		rect = [kb_startx,kb_starty-32,11*key_w,key_h]
		pygame.draw.rect(screen,white,rect)
		pygame.draw.rect(screen,black,rect,2)
		##draw output words
		rect = [kb_startx,kb_starty-2*32,11*key_w,key_h]
		pygame.draw.rect(screen,white,rect)
		pygame.draw.rect(screen,black,rect,2)
		draw_kb_focus(screen,font,kb_pos)
		
def hidden_kb(screen,font):
	global is_key_show
	global pic_focus
	if is_key_show == 0:
		return
	is_key_show	 = 0
	update_pic_info(screen,font,pic_infos)


def getimgmode(file):
	if os.path.exists(file):
		img=Image.open(file)
		return img.mode
	else:
		return ""

def resizepic(file,size):
	if os.path.exists(file):
		img=Image.open(file)
		basename,ext = os.path.splitext(file)		
		extname=ext.replace('.','').lower()
		extname = extname.replace("jpg","jpeg")
		pic_w,pic_h=size
		target = img.resize(size,Image.ANTIALIAS)		
		#savename=basename+"_%dX%d"%(pic_w,pic_h)+ext
		#target.save(savename,extname)
		return [target.mode,target.tostring()]

def pic_lose_focus(screen,font,pic_index):
	global pic_infos
	if pic_index < len(pic_infos):
		rect=[pic_infos[pic_index]["x"]-2,pic_infos[pic_index]["y"]-2,pic_infos[pic_index]["w"]+4,pic_infos[pic_index]["h"]+4]	
		img=pic_infos[pic_index]["pic"]
		if len(img)>1:
			pos=(pic_infos[pic_index]["x"],pic_infos[pic_index]["y"])
			img_mode,img_str=resizepic(img,pic_size)
			#img_mode=getimgmode(img)
			pyim = pygame.image.fromstring(img_str,pic_size,img_mode).convert()
			screen.blit(pyim,pos)
		else:
			pygame.draw.rect(screen,black,rect)	
		pygame.draw.rect(screen,white,rect,2)	

def pic_get_focus(screen,font,pic_index):
	global pic_infos
	if pic_index < len(pic_infos):
		rect=[pic_infos[pic_index]["x"]-2,pic_infos[pic_index]["y"]-2,pic_infos[pic_index]["w"]+4,pic_infos[pic_index]["h"]+4]	
		pygame.draw.rect(screen,blue,rect,2)

#pygame.USEREVENT
def update_pic_word(screen,font,pic_index):
	global total_pic_infos
	global is_key_show
	global pic_infos
	global word_offset_x
	
	if is_key_show > 0:	
		return
	elif total_pic_infos<1: 
		return
	if pic_index>=len(pic_infos):
		pic_index=0
		
	words=pic_infos[pic_index]["words"]
	unicode_str = unicode(words,'utf-8')
	text = font.render(unicode_str,False,black,white)
	word_w,word_h=font.size(unicode_str)
	word_x=pic_infos[pic_index]["x"]+2
	word_y=pic_infos[pic_index]["y"]+pic_infos[pic_index]["h"]-word_h-2	
	
	word_offset_x = word_offset_x+2
	if 	word_w>pic_infos[pic_index]["w"]:
		if word_w > word_offset_x+pic_infos[pic_index]["w"]-4:
			screen.blit(text, [word_x,word_y],[word_offset_x,0,pic_infos[pic_index]["w"]-4,word_h])
		else:
			screen.blit(text, [word_x,word_y],[word_offset_x,0,word_w-word_offset_x,word_h])
			word_offset_x = 0
	else:
		screen.blit(text, [word_x,word_y],[0,0,word_w,word_h])
	pic_get_focus(screen,font,pic_index)

	
def draw_pic_info(screen,font,pic_index):
	global pic_infos
	if pic_index < len(pic_infos):
		rect=[pic_infos[pic_index]["x"]-2,pic_infos[pic_index]["y"]-2,pic_infos[pic_index]["w"]+4,pic_infos[pic_index]["h"]+4]	
		img=pic_infos[pic_index]["pic"]
		if len(img)>1 and os.path.exists(img):
			pos=[pic_infos[pic_index]["x"],pic_infos[pic_index]["y"]]
			img_mode,img_str=resizepic(img,pic_size)
			pyim = pygame.image.fromstring(img_str,pic_size,img_mode).convert()
			screen.blit(pyim,pos)
		else:
			pygame.draw.rect(screen,black,rect)	
		#rect=[pic_infos[pic_index]["x"]-2,pic_infos[pic_index]["y"]-2,pic_infos[pic_index]["w"]+4,pic_infos[pic_index]["h"]+4]	
		pygame.draw.rect(screen,white,rect,2)	
	
def update_windows(screen,font):
	global search_words
	screen.fill(white)
	#screen.blit(background,[0,0])
	update_menu_info(screen,font)
	draw_search_bar(screen,font,search_words)
	update_pic_info(screen,font,pic_infos)
	
	


#更新所有图片列表信息
def update_pic_info(screen,font,picinfos):
	for i in range(len(picinfos)):
		draw_pic_info(screen,font,i)
	
	
def draw_menu_info(screen,menu_font,menu_index):
	global menu_infos
	if menu_index < len(menu_infos):
		bk=menu_infos[menu_index]["bkimg"]
		titles=menu_infos[menu_index]["title"]
		unicode_str = unicode(titles,'utf-8')
		txt_w,txt_h=menu_font.size(unicode_str)
		txt = menu_font.render(unicode_str,False,black)		
		bk_size=(menu_w,menu_h)
		img_mode,img_str=resizepic(bk,bk_size)
		#img_mode=getimgmode(bk)
		pyim = pygame.image.fromstring(img_str,bk_size,img_mode).convert()
		pos=(menu_start[0]+menu_index*menu_w,menu_start[1])
		screen.blit(pyim,pos)
		offset_x = (menu_w-txt_w)/2
		offset_y = (menu_h-txt_h)/2
		pos = (menu_start[0]+menu_index*menu_w+offset_x,menu_start[1]+offset_y)
		screen.blit(txt,pos)

def update_menu_info(screen,font):
	global menu_infos
	global menu_focus
	for i in range(len(menu_infos)):
		draw_menu_info(screen,font,i)
	menu_get_focus(screen,font,menu_focus)
		

def menu_lose_focus(screen,menu_font,menu_index):
	global menu_infos
	if menu_index < len(menu_infos):
		bk=menu_infos[menu_index]["ftimg"]
		titles=menu_infos[menu_index]["title"]
		unicode_str = unicode(titles,'utf-8')
		txt_w,txt_h=menu_font.size(unicode_str)
		txt = menu_font.render(unicode_str,False,black)		
		bk_size=(menu_w,menu_h)
		img_mode,img_str=resizepic(bk,bk_size)
		#img_mode=getimgmode(bk)
		pyim = pygame.image.fromstring(img_str,bk_size,img_mode).convert()
		pos=(menu_start[0]+menu_index*menu_w,menu_start[1])
		screen.blit(pyim,pos)
		offset_x = (menu_w-txt_w)/2
		offset_y = (menu_h-txt_h)/2
		pos = (menu_start[0]+menu_index*menu_w+offset_x,menu_start[1]+offset_y)
		screen.blit(txt,pos)

def menu_get_focus(screen,menu_font,menu_index):
	global menu_infos
	if menu_index < len(menu_infos):
		bk=menu_infos[menu_index]["fcimg"]
		titles=menu_infos[menu_index]["title"]
		unicode_str = unicode(titles,'utf-8')
		txt_w,txt_h=menu_font.size(unicode_str)
		txt = menu_font.render(unicode_str,False,black)		
		bk_size=(menu_w,menu_h)
		img_mode,img_str=resizepic(bk,bk_size)
		#img_mode=getimgmode(bk)
		pyim = pygame.image.fromstring(img_str,bk_size,img_mode).convert()
		pos=(menu_start[0]+menu_index*menu_w,menu_start[1])
		screen.blit(pyim,pos)
		offset_x = (menu_w-txt_w)/2
		offset_y = (menu_h-txt_h)/2
		pos = (menu_start[0]+menu_index*menu_w+offset_x,menu_start[1]+offset_y)
		screen.blit(txt,pos)

def change_menu_focus(old,new):	
	print "change_menu_focus"
	

def getmenu_info(str):
	menuinfo={}	
	menuinfo["bkimg"]="1.png"#normal img
	menuinfo["seimg"]="2.png"#select img
	menuinfo["fcimg"]="3.png"#focus img
	menuinfo["title"]=str	
	return menuinfo

def gen_pic_info(index):
	pic_info={}
	pic_info["words"]="this is a test words...你好v."
	pic_info["url"] = "http://hello.com"
	pic_info["pic"]="1.jpg"
	pic_info["x"] = pic_start[0]+(pic_w+4)*(index%5)
	pic_info["y"] = pic_start[1]+(pic_h+4)*(index/5)
	pic_info["w"] = pic_w
	pic_info["h"] = pic_h
	return pic_info

def write_pic(url,filename):
	f=open(filename,"wb")
	h=httplib2.Http()
	resp,content=h.request(url)
	if resp.status==200:
		f.write(content)	
	f.close()
	
def deal_key_event(screen,font,event):
	global pic_focus
	global is_key_show
	if is_key_show >0:
		return
	if event.type==pygame.KEYDOWN:
		if event.key==pygame.K_SPACE:
			done=True
		elif event.key==pygame.K_TAB:
			if menu_focus == 0:
				menu_focus=1
				gen_video_infos_by_type('qq')
			else:
				menu_focus=0
				gen_video_infos_by_type('hlstv')
				
			update_windows(screen,font)
			
		elif event.key==pygame.K_LEFT:
			pic_lose_focus(screen,font,pic_focus)
			pic_focus = pic_focus-1
			if pic_focus<0:
				pic_focus = 19
				update_pic_word(screen,font,pic_focus)
				pic_get_focus(screen,font,pic_focus)
		elif event.key==pygame.K_RIGHT:			
			pic_lose_focus(screen,font,pic_focus)
			pic_focus = pic_focus+1
			if pic_focus>=len(pic_infos):
				pic_focus = 0
				update_pic_word(screen,font,pic_focus)
				pic_get_focus(screen,font,pic_focus)	
		elif event.key == pygame.K_UP:
			pic_lose_focus(screen,font,pic_focus)
			pic_focus = pic_focus-5
			if pic_focus<0:
				pic_focus = pic_focus+len(pic_infos)
				update_pic_word(screen,font,pic_focus)
				pic_get_focus(screen,font,pic_focus)	
		elif event.key == pygame.K_DOWN:
			pic_lose_focus(screen,font,pic_focus)	
			pic_focus = pic_focus+5
			if pic_focus>=len(pic_infos):
				pic_focus = pic_focus -len(pic_infos)
				update_pic_word(screen,font,pic_focus)
				pic_get_focus(screen,font,pic_focus)
		elif event.key == pygame.K_PAGEDOWN:
			if(pic_end_index <total_pic_infos):
				gen_pic_infos(videos,pic_start_index+20)
				update_windows(screen,font)
		elif event.key == pygame.K_PAGEUP:
			if(pic_start_index >= 0):
				if(pic_start_index>20):
					gen_pic_infos(videos,pic_start_index-20)
				else:
					gen_pic_infos(videos,0)
				update_windows(screen,font)
		elif 	event.key == pygame.K_RETURN:
			print 'key play movie :',pic_infos[pic_focus]['url']
			set_play_param(pic_infos[pic_focus]['url'])			
			exit_pygame()
			
	elif event.type==pygame.MOUSEBUTTONDOWN or event.type==pygame.MOUSEBUTTONUP or event.type==pygame.MOUSEMOTION:
		deal_mouse_event(screen,font,event)
	elif event.type==pygame.QUIT:
		done = True
	elif event.type == pygame.USEREVENT:
		update_pic_word(screen,font,pic_focus)	

last_m_pos = (0,0)
last_m_key = (0,0,0)
last_element= ''

def deal_mouse_event(screen,font,event):
	global last_m_key
	global last_m_pos
	global menu_focus
	global pic_focus
	global kb_input_vals
	global is_key_show
	global kb_pos
	global kb_total_num	
	global kb_out_words
	global kb_ch_words
	global search_words
	global kb_out_words_pos
	
	m_pos=pygame.mouse.get_pos()
	m_key=pygame.mouse.get_pressed()
	m_x,m_y=m_pos
	m_b1,m_b2,m_b3=m_key
	if is_key_show >0:
		if last_m_pos != m_pos:
			last_m_pos = m_pos
			ke=get_kbelement_by_pos(m_x,m_y)
			ki=get_kbelement_index_by_pos(m_x,m_y,ke)
			if ke=='kb' and ki != kb_pos:
				kb_lose_focus(screen,font,kb_pos)
				kb_pos = ki
				draw_kb_focus(screen,font,kb_pos)
			elif ke=='kw' and ki != kb_out_words_pos:
				kb_out_words_pos = ki
				draw_output_words(screen,font,kb_out_words)
		elif 	m_key != last_m_key:	
			b1,b2,b3=last_m_key
			last_m_key = m_key
			ke=get_kbelement_by_pos(m_x,m_y)
			ki=get_kbelement_index_by_pos(m_x,m_y,ke)
			if b1 != m_b1:
				if m_b1 == 1:
					if ke == 'kb':
						key = keywords[kb_pos]
						if key == ' ' and kb_pos == 10:
							kb_input_vals = kb_input_vals[0:-1]	
						elif key == ' ' and kb_pos == 21:
							#kb_input_vals = ''
							if len(kb_ch_words)>0:
								search_words  = search_words+kb_ch_words[kb_out_words_pos]
							kb_input_vals =''
							kb_out_words = ''
							kb_out_words_pos = 0
							draw_search_bar(screen,font,search_words)
						elif key == ' ':
							if len(kb_ch_words)>0:
								search_words  = search_words+kb_ch_words[kb_out_words_pos]
							kb_input_vals =''
							kb_out_words = ''
							kb_out_words_pos =0
							draw_search_bar(screen,font,search_words)
						else:
							kb_input_vals = kb_input_vals+key
						outs = get_py_str(font,kb_input_vals)
						draw_input_words(screen,font,kb_input_vals)
						draw_output_words(screen,font,outs)
					elif ke == 'kw':
						if len(kb_ch_words)>0:
							search_words  = search_words+kb_ch_words[kb_out_words_pos]
						kb_input_vals =''
						kb_out_words = ''
						kb_out_words_pos=0
						draw_search_bar(screen,font,search_words)
					elif ke == 'search_button':
						print 'do search...',search_words
						hidden_kb(screen,font)
					else:
						hidden_kb(screen,font)						
	else:
		if last_m_key == m_key and last_m_pos == m_pos and hasattr(event,'button'):		
			if event.button == 4:
				print 'roll up'
				if(pic_start_index >= 0):
					if(pic_start_index>20):
						gen_pic_infos(videos,pic_start_index-20)
					else:
						gen_pic_infos(videos,0)
					update_windows(screen,font)
			elif event.button == 5:
				if(pic_end_index <total_pic_infos):
					gen_pic_infos(videos,pic_start_index+20)
					update_windows(screen,font)
		elif last_m_pos != m_pos:
			last_m_pos = m_pos
			e=get_element_by_pos(m_x,m_y)
			i = get_element_index_by_pos(m_x,m_y,e)
			
			if len(e)>1:
				last_element = e
				if e=='pic' and pic_focus != i:				
					pic_lose_focus(screen,font,pic_focus)
					pic_focus = i
					pic_get_focus(screen,font,i)		
		elif m_key != last_m_key:
			b1,b2,b3=last_m_key
			last_m_key = m_key
			e=get_element_by_pos(m_x,m_y)
			i = get_element_index_by_pos(m_x,m_y,e)
			if b1 != m_b1:
				if m_b1 == 1:
					if e == 'search_bar':
						draw_kb(screen,font)
					elif e=='pic':
						print 'play movie.url:',pic_infos[pic_focus]['url']
						hidden_kb(screen,font)
						set_play_param(pic_infos[pic_focus]['url'])			
						exit_pygame()
					elif  e=='search_button':
						print 'do search :',search_words
						hidden_kb(screen,font)
						
								
			if b2 != m_b2:
				if m_b2 == 1:
					print 'middle click down'
				else:
					print 'middle click up'
			if b3 != m_b3:
				if m_b3 == 1:
					print 'right click down'
				else:
					print 'right click up'	
	

def gen_pic_infos(videoinfos,start):
	global total_pic_infos
	global pic_start_index
	global pic_end_index
	global pic_infos
	global menu_type_list
	global menu_focus
	
	i=0	
	pic_start_index = start
	if total_pic_infos<=pic_start_index:
		return
	else:
		del pic_infos[:]
	for index in range(pic_start_index,total_pic_infos):
		pic_info = gen_pic_info(i)
		i = i+1
		videoinfo = videoinfos[index]
		pic_info["words"]= videoinfo["img_alt"]
		pic_info["url"]= videoinfo["videourl"]
		if len(videoinfo["img_url"])>0:
			pic_info["pic"] = "%s/%d.jpg"%(menu_type_list[menu_focus],i)
			write_pic(videoinfo["img_url"],pic_info["pic"])	
		else:
			pic_info["pic"]=''
		pic_infos.append(pic_info)
		pic_end_index = pic_start_index+i
		if i> 19 or index>=total_pic_infos:
			break

def gen_video_infos_by_type(strtype,url=''):
	global videos
	global total_pic_infos
	
	if strtype=='qq':
		if len(url)<7:
			url="http://v.qq.com/"			
		videos=getvideoinfos.get_qq_video_infos(url)		
	elif strtype=='hlstv':
		videos=PPlive.getppliveurl()
		
	if len(videos)>0:
		total_pic_infos = len(videos)
		gen_pic_infos(videos,0)
	
		

def start_gui(w,h):
	global videos
	global total_pic_infos	
	global pygame_init
	size=[w,h]	
	
	pygame.init()
	#size=[600,480]
	screen=pygame.display.set_mode(size)	
	pygame.display.set_caption("NetWork Player")	
	#Loop until the user clicks the close button.
	done=False
	clock = pygame.time.Clock()
	screen.fill(white)
	#background = pygame.image.load("test.jpg").convert()
	#screen.blit(background,[0,0])
	#img_mode=getimgmode("test.jpg")
	#img_str=resizepic("test.jpg",(600,480))
	#background = pygame.image.fromstring(img_str,(600,480),img_mode)
	
	font = pygame.font.Font(pygame.font.match_font('microsoftyahei'),16)
	menu_font = font
	#pygame.font.Font(pygame.font.match_font('microsoftyahei'),16)
	#kb_font = pygame.font.Font(pygame.font.match_font('microsoftyahei'),24)
	
	#screen.blit(background,[0,0])
	update_menu_info(screen,menu_font)
	#draw_menu_info(screen,menu_font,0)
	update_pic_info(screen,font,pic_infos)
	pic_get_focus(screen,font,pic_focus)
	menu_get_focus(screen,menu_font,menu_focus)
	draw_search_bar(screen,font,'')
	pygame.time.set_timer(pygame.USEREVENT,300)
	pygame_init = True
	while done==False:
	    time_passed = clock.tick(30)    
	    for event in pygame.event.get(): # User did something    	
	    	if event:	
	    		deal_key_event(screen,font,event)
	    		handle_kb_event(screen,font,event)    		
	    		if event.type==pygame.KEYDOWN:
	    			if event.key==pygame.K_END:
	    				pygame.display.quit()
	    				pygame_init=False
	    			elif event.key == pygame.K_HOME:
	    				if pygame_init==False:
	    					pygame.display.init()
	    					pygame_init=True
	    					screen=pygame.display.set_mode(size)
	    					update_windows(screen,font)	    						
	    		elif event.type==pygame.QUIT:
	    			done = True
	    		elif event.type == pygame.USEREVENT:
	    			if pygame_init:
	    				update_pic_word(screen,font,pic_focus)	    		
	    		
	    if pygame_init:			
	    	pygame.display.flip()
	pygame.quit ()
	pygame_init=False


def set_play_param(url):
	global menu_type_list
	global menu_focus
	print 'play url',url
	if menu_type_list[menu_focus]=='hlstv':
		print 'hlstv'
		PPlive.start_tv(url)		
	elif menu_type_list[menu_focus]=='qq':
		print 'v.qq.com'
		vfs={}
		if len(url)>0:
			vfs=getvideoinfos.geturls(url)
		download_manage.set_url(vfs)

			
	
def send_event(keytype,attr):
	global pygame_init
	if pygame_init:
		ev=pygame.event.Event(keytype,attr)
		pygame.event.post(ev)
	else:
		print 'pygame_init false'

def exit_pygame():
	send_event(pygame.QUIT,{})
#gui thread
#download thread
#play thread
#control thread...main thread
#conf thread ...save the last state

#log thread
#console thread
#web thread

class ThreadEvent(threading.Thread):
	"""Threaded Event"""
	def __init__(self):
		threading.Thread.__init__(self)
		self.runing=True
	
	def run(self):
		dev = evdev.Device('/dev/input/event0')
		last={}
		while self.runing:
			dev.poll()
			time.sleep(0.3)
			last=dev.get_last_event()
			for key in last.keys():
				if last[key] == 'KEY_STOPCD':
					print 'stop_player'
					player.stop_player()
					dev.quit()
					return

def find_start_file(path):
	fn=''
	for root, dirs, files in os.walk(path, topdown=False):
		for f in files:
			if re.search('\.PART[0-9]+?\.',f):
				fn=os.path.join(root,f)
				return fn	
	return fn

def play_file(filename=''):
	playcmd=''
	if len(filename)>7:
		playcmd='/root/omxplayer.bin %s'%(filename)
		fl=os.path.getsize(filename)
		while fl<1024*1024:
			time.sleep(1)
	else:		
		while len(playcmd)<10:
			time.sleep(5)
			fn=find_start_file('./')
			if len(fn)>0:
				playcmd='/root/omxplayer.bin %s'%(fn)				
				fl=os.path.getsize(fn)
				while fl<5*1024*1024:
					time.sleep(1)
					fl=os.path.getsize(fn)
	return os.system(playcmd)

def start_evdev():
	print 'start evdev thread...'
	te=ThreadEvent()
	te.setDaemon(True)
	te.start()



def start():	
	#start download thread
	gen_video_infos_by_type('hlstv')
	menu_infos.append(getmenu_info("PPTV"))
	menu_infos.append(getmenu_info("QQ视频"))
	PPlive.init_tv()
	download_manage.setDaemon(True)
	download_manage.start()
	print 'init finish'	
	while True:
		start_gui(600,480)
		start_evdev()
		#start key manage to deal the player control		
		print 'startplay'
		#check if need restart player
		if menu_type_list[menu_focus]=='hlstv':
			os.system('/root/omxplayer.bin http://localhost/index.m3u8')
		else:
			#find start file...
			play_file()			
		set_play_param('')
		#exit key manage pygame will deal the key event			
		print 'restart gui'
		
	#start gui thread
	#start_gui(600,480)
start()	
#start_gui(600,480)	
	





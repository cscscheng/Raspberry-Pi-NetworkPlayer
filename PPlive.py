#-*- coding: utf-8 -*-
import httplib2
import re
import time
import json
import os
import Queue
import threading
import netinfo


last_time_dict={}
loop = True;
last_ts_file_name=''
ts_file_download_num =0
ts_file_download_name=[]
last_m3u8_url = ''
lan_ip=''
wan_ip=''
wlan_ip=''
ts_file_duration='5'
ts_file_seq='271547071'

def gen_pptv_list():
	lists=dict()
	h2=httplib2.Http()
	index_url2='http://live.pptv.com/list/tv_list'
	resp,content=h2.request(index_url2,'GET')
	if resp.status==200:
		areas=re.findall('#[^a-zA-Z]+area_id[^0-9]*=[^0-9]*([0-9]*)[^0-9]+>(.*)<\/a>',content)
		if areas:
			for id,name in areas:	
				are_list_url1='http://live.pptv.com/api/tv_list?cb=load.cbs.cb_1&area_id='			
				fullurl=are_list_url1+id				
				info=dict([('title',name),('url',fullurl)])
				lists[id]=info
				#last_time_dict[id]=0
	#print lists
	return lists

def gen_m3u8_url(in_url,id):
	return_urls=[]
	h=httplib2.Http()
	resp,content=h.request(in_url,'GET')
	if resp.status==200:
		#print content
		urls=re.findall('>(\\\u[^<]*)<[^>]*>[^<]*<[^>]*>[^<]*<[^<]+show_playing[^>]+>[^<]*<[^"]*"([^"]*)"[^>]+>[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>([^<]*)<',content)
		#urls=re.findall('<[^<]+show_playing[^>]+>[^<]*<[^"]*"([^"]*)"[^>]+>',content)
		if urls:			
			for name,url,titles in urls:
				res={}
				js='["list", {"name":["%s","%s"]}]'%(name,titles)
				j=json.loads(js)
				#print j[1]['name'][0]
				#print j[1]['name'][1]
				url = url.replace('\\','')
				playing=j[1]['name'][1].encode('utf-8')
				if len(playing)>0:
					res["img_alt"]=j[1]['name'][0].encode("utf-8")+'<'+j[1]['name'][1].encode("utf-8")+">"
				else:
					res["img_alt"]=j[1]['name'][0].encode("utf-8")
				res["img_url"]=''
				resp,content=h.request(url,'GET')
				if resp.status==200:
					play_ids=re.findall('"ipadurl":"([^"]+)"',content)
					if play_ids:
						for play_id in play_ids:
							m3u8url = play_id.replace('\\','')
							res["videourl"]=m3u8url
							return_urls.append(res)
	return return_urls
				
def getppliveurl():
	ret=[]
	ret = load_from_file("./live.json")
	if len(ret)>0:
		print 'load_from_file OK'
		return ret
	pptv_lists=gen_pptv_list()
	for id in pptv_lists.keys():
		urls=gen_m3u8_url(pptv_lists[id]['url'],id)
		if len(urls)>0:
			ret = ret+urls
	write_pptv2file(ret,"./live.json")	
	return ret
		
def write_m3u8_file(filename,content=''):
	print 'write_m3u8_file'
	global ts_file_duration
	f=open(filename,'w+')	
	b1='#EXTM3U\r\n#EXT-X-TARGETDURATION:%s\r\n#EXT-X-MEDIA-SEQUENCE:%s\r\n'%(ts_file_duration,ts_file_seq)			
	f.write(b1)
	if len(content)>0:
		bf='#EXTINF:%s,\r\n'%ts_file_duration
		f.write(bf)
		
	f.close()


def update_m3u8_file(filename,content):
	global ts_file_duration
	if os.path.exists(filename):
		f=open(filename,'a+')
		bf='#EXTINF:%s,\r\n'%ts_file_duration
		f.write(bf)
		f.write(content)
		f.write('\r\n')
		f.close()
	
def get_ts_by_url(infos):
	global last_ts_file_name
	global ts_file_download_name
	global ts_file_download_num
	ret = 0
	if len(infos)<1:
		return 0
	else:
		h=httplib2.Http()
		for info in infos:
			url=info['url']
			filename=info['ts_name']
			retry=8
			fullname='/var/www'+filename			
			if  fullname in ts_file_download_name:
				continue
			while retry>0:
				resp,content=h.request(url,'GET')
				if resp.status==200:
					pre_url='/var/www/'
					last_ts_file_name = filename
					filename = pre_url+filename
					f=open(filename,'wb')
					f.write(content)
					f.close()
					ret += 1	
					ts_file_download_num += 1
					ts_file_download_name.append(filename)
					break	
				else:
					retry = retry-1
					print 'get_ts_by_url ',retry
					if retry==0:
						ret = -1
						break	
	return ret

def find_m3u8_info(url):
	h=httplib2.Http()
	resp,content=h.request(url,'GET')
	if resp.status==200:
		fn=get_filename(url)
		if len(fn and 'm3u8'):
			
			get_ts_duration(ct)
		else:
			print 'error type:',fn

def get_ts_duration(ct):
	global ts_file_duration
	global ts_file_seq
	td='#EXT-X-TARGETDURATION:([0-9]+)'
	tds=re.findall(td,ct)
	if tds:
		ts_file_duration=tds[0]
	td='#EXT-X-MEDIA-SEQUENCE:([0-9]+)'
	tds=re.findall(td,ct)
	if tds:
		ts_file_seq=tds[0]


def parse_m3u8(ct,num):
	global last_m3u8_url
	global ts_file_duration
	global ts_file_seq	 
	get_ts_duration(ct)	
	rt=[]
	mp='BANDWIDTH=([0-9]+)[\s]+?([\S]+)'
	murls=re.findall(mp,ct)
	if murls:
		dic_list=[]
		tu=''
		for band,url in murls:			
			m_dic={}
			m_dic['band']=band
			m_dic['url']=url
			dic_list.append(m_dic)
		#m_dic=m_dic.sort()
		if len(dic_list)>0:
			if dic_list[0]['url'] != last_m3u8_url:
				last_m3u8_url=dic_list[0]['url']
			return get_ts_info(dic_list[0]['url'],num)
		else:
			return rt
	else:
		tp='(http[\S]+)[\s]+?'
		turls=re.findall(tp,ct)		
		if turls:
			for url in turls:
				ti={}
				fn=get_filename(url)
				ti['url']=url
				ti['ts_name']=fn
				rt.append(ti)
		return rt		
	
	
def get_ts_info(url,num):
	rt=[]
	h=httplib2.Http()
	resp,content=h.request(url,'GET')
	if resp.status==200:
		fn=get_filename(url)
		if len(fn and 'm3u8'):
			rt=parse_m3u8(content,num)
		else:
			print 'error type:',fn
	if len(rt)>num and num>0:
		rt=rt[-(num):]
	return rt
		
	
	
def get_filename(url):
	bn=os.path.basename(url)
	if len(bn)>2:
		fn=re.sub(r'([\w]*\.[\w]+).*',r'\1',bn)
		return fn
	else:
		return ""

def write_pptv2file(content,fn):
	c1=json.dumps(content)
	f=open(fn,'wb')
	##todo
	f.write(c1)
	f.close()
	return 0

#
def load_from_file(fn):
	ret = []
	if os.path.exists(fn):		
		f=open(fn,'rb')
		ret=json.load(f)
		for v in ret:
			v['img_alt']=v['img_alt'].encode('utf-8')
			v['videourl']=v['videourl'].encode('utf-8')
			v['img_url']=v['img_url'].encode('utf-8')
	return ret

def modify_m3u8_file(fn,str):
	if os.path.exists(fn):
		f1=open(fn,'r')
		f2=open('./tmp.m3u8','w+')
		ct=f1.read(10240)
		if len(ct)>30:
			pt='#EXTINF:5,[\s]+?http[\S]+?%s'%str
			newct = re.sub(pt,'',ct)
			f2.write(newct)
		f2.close()			
		f1.close()
		
		
		
	
def check_ts_file(url):
	global ts_file_download_name
	global ts_file_download_num
	global last_ts_file_name
	global last_m3u8_url
	
	ts=[]
	if len(last_m3u8_url)>0:
		url=last_m3u8_url
	ts=get_ts_info(url,1)

	if len(ts)>0:
		full='/var/www/'+ts[0]['ts_name']
		if full not in ts_file_download_name and last_ts_file_name != ts[0]['ts_name']:			
			get_ts_by_url(ts)
			for info in ts:
				if wlan_ip != '': 	
					url='http://%s/%s'%(wlan_ip,get_filename(info['url']))	
				else:
					url='http://localhost/%s'%(get_filename(info['url']))			
				update_m3u8_file('/var/www/live.m3u8',url)
		elif len(ts_file_download_name)>30:
			f=ts_file_download_name[0]
			del ts_file_download_name[0]			
			#modify_m3u8_file('/var/www/live.m3u8',os.path.basename(f))
			if os.path.exists(f):
				os.unlink(f)				
			else:
				print 'file not found',f
			
def del_file_by_name(path,name):
	for root, dirs, files in os.walk(path, topdown=False):
		for f in files:
			if re.search(name,f):
				os.remove(os.path.join(root,f))		

def stop_tv():
	global ts_file_download_name
	loop=False
	while len(ts_file_download_name)>0:
		ts_file_download_name.pop()
	

class ThreadTV(threading.Thread):
	"""Threaded TV"""
	def __init__(self):
		threading.Thread.__init__(self)
		self.url=''
		self.status='stop'
	def set_tv_url(self,url):
		global ts_file_duration
		global ts_file_seq	
		self.url=''	
		if len(url)>0:
			del_file_by_name('/var/www','ts')			
			ts_infos=get_ts_info(url,2)
			write_m3u8_file('/var/www/live.m3u8')
			get_ts_by_url(ts_infos)
			for info in ts_infos:
				if wlan_ip != '': 	
					url='http://%s/%s'%(wlan_ip,get_filename(info['url']))	
				else:
					url='http://localhost/%s'%(get_filename(info['url']))			
				update_m3u8_file('/var/www/live.m3u8',url)
			#write_m3u8_file('/var/www/live.m3u8')
			print 'start player here'
			f=open('/root/play/plt.txt','w+')
			f.write('TV')
			f.close()
			self.url=url
		else:
			data['cmd']='stop'
			stop_tv()
			f=open('/root/play/plt.txt','w+')
			f.write('')
			f.close()
		self.url=url	
	def run(self):
	  while True:
			if len(self.url)>0:
				check_ts_file(self.url)				
			time.sleep(1)

tv_thread = ThreadTV()

def init_tv():
	global lan_ip
	global wan_ip
	global wlan_ip
	global tv_thread
	for dev in netinfo.list_active_devs():
		print dev
		if dev == 'eth0':
			lan_ip = netinfo.get_ip(dev)
			print 'get lan ip:',lan_ip
			print dev
			print netinfo.get_ip(dev)
		elif dev == 'wlan0':
			wlan_ip = netinfo.get_ip(dev)
			print wlan_ip
		elif dev == 'lo':
			print 'local ip'
		##todo wan ip
		elif dev == 'ppp0':
			wan_ip = netinfo.get_ip(dev)
	
	tv_thread.setDaemon(True)
	tv_thread.start()

def start_tv(url):				
	global 	tv_thread
	tv_thread.set_tv_url(url)
	
def test(url):
	init_tv()
	start_tv(url)
	while True:
		time.sleep(1)

test('http://web-play.pptv.com/web-m3u8-300163.m3u8')
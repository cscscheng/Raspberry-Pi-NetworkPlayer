#-*- coding: utf-8 -*-
import httplib2
import re
import time
import json
import os

last_time_dict={}
loop = True;
last_ts_file_name=''
ts_file_download_num =0
ts_file_download_name=[]

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
	f=open(filename,'w+')				
	f.write('#EXTM3U\r\n#EXT-X-TARGETDURATION:5\r\n#EXT-X-MEDIA-SEQUENCE:271472474\r\n')
	if len(content)>0:
		f.write('#EXTINF:5,\r\n')
		f.write(content)
		f.write('\r\n')
	f.close()

	
def update_m3u8_file(filename,content):
	if os.path.exists(filename):
		f=open(filename,'a+')		
		f.write('#EXTINF:5,\r\n')
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
			while retry>0:
				resp,content=h.request(url,'GET')
				if resp.status==200:
					pre_url='/var/www/'
					last_ts_file_name = filename
					filename = pre_url+filename
					f=open(filename,'wb')
					f.write(content)
					f.close()	
					url='http://192.168.2.22/%s'%last_ts_file_name				
					update_m3u8_file('/var/www/live.m3u8',url)
					ret += 1	
					ts_file_download_num += 1
					ts_file_download_name.append(filename)
					break	
				else:
					retry = retry-1
					if retry==0:
						ret = -1
						break	
	return ret
	
def parse_m3u8(ct,num):
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
def check_ts_file(url):
	global ts_file_download_name
	global ts_file_download_num
	global last_ts_file_name
	ts=[]
	ts=get_ts_info(url,1)
	if len(ts)>0:
		if ts[0]['ts_name'] != last_ts_file_name:
			get_ts_by_url(ts)
		elif len(ts_file_download_name)>30:
			f=ts_file_download_name[0]
			del ts_file_download_name[0]
			os.unlink(f)
			print 'del file :',f
			
def del_file_by_name(path,name):
	for root, dirs, files in os.walk(path, topdown=False):
		for f in files:
			if re.search(name,f):
				os.remove(os.path.join(root,f))


def start_tv(url):				
	del_file_by_name('/var/www','ts')	
	write_m3u8_file('/var/www/live.m3u8')
	ts_infos=get_ts_info(url,5)
	rt = get_ts_by_url(ts_infos)
	print 'start play now...'	
	while loop:
		time.sleep(1)
		check_ts_file(url)		

def stop_tv():
	loop=False
			
del_file_by_name('/var/www','ts')	
write_m3u8_file('/var/www/live.m3u8')
ts_infos=get_ts_info('http://web-play.pptv.com/web-m3u8-300159.m3u8',5)
rt = get_ts_by_url(ts_infos)
print 'start play now...'
ii=300
while ii>0:
	time.sleep(1)
	check_ts_file('http://web-play.pptv.com/web-m3u8-300159.m3u8')
	
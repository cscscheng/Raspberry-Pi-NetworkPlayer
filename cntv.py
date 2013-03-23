# -*- coding: utf-8 -*-
import time
import random
import math
import httplib2
import json
import re
import os


base_url='http://ipad.cntv.cn'

myagent='Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/5.0.1 Mobile/7B334b Safari/531.21.10'
url_get_m3u8='http://vdn.apps.cntv.cn/api/getLiveUrlCommonRedirectApi.do?channel='
url_get_m3u8_2='&urlType=highEdition'

def get_cntv_url():
	base_url='http://ipad.cntv.cn'	
	urls=[]
	headers={'User-Agent':myagent}
	h=httplib2.Http()
	resp,content=h.request(base_url,'GET',headers=headers)
	if resp.status==200:
		tv_urls=re.findall('(\/nettv.+\.shtml)',content)
		if tv_urls:
			for tv_url in tv_urls:
				fullurl = base_url+tv_url
				resp,content=h.request(fullurl,'GET',headers=headers)
				if resp.status==200:
					ipad_url=re.findall('<li><a href="([^"]*)">([^<]*)</a></li>',content)
					if ipad_url:
						for tmp,title in ipad_url:
							resp,content=h.request(tmp,'GET',headers=headers)
							if resp.status==200:
								channel=re.findall('\["([^"]*)"\]',content)
								if channel:
									#urls.append(url_get_m3u8+channel[0]+url_get_m3u8_2)									
									resp,content=h.request(url_get_m3u8+channel[0]+url_get_m3u8_2,'GET',headers=headers)
									if resp.status==200:
										if re.findall('m3u8',resp['content-location']):
											info={}
											info["videourl"]=	resp['content-location']
											info["img_alt"]= title
											info["img_url"] = ''
											urls.append(info)
										else:
											print resp
											print resp['content-location']
											print url_get_m3u8+channel[0]+url_get_m3u8_2						
	return urls
											
	
def get_filename(url):
	bn=os.path.basename(url)
	if len(bn)>2:
		fn=re.sub(r'([\w]*\.[\w]+).*',r'\1',bn)
		return fn
	else:
		return ""
										
def get_base_uri(url):
	us=''
	bases=re.findall('([\S]*://[^/]*)/.*',url)
	if bases:
		us=bases[0]
	return us
	
def parse_cntv_m3u8(url):
	rt=[]
	headers={'User-Agent':myagent}
	h=httplib2.Http()
	resp,content=h.request(url,'GET',headers=headers)
	if resp.status==200:
		print resp['content-location']
		bu=get_base_uri(url)
		tp='(http[\S]+)[\s]+?'
		turls=re.findall(tp,content)
		if turls:
			for furl in turls:
				ti={}
				fn=get_filename(furl)
				ti['url']=furl
				ti['ts_name']=fn
				rt.append(ti)
		else:			
			files=re.findall('([^#\n][\S]+\.ts[\S]*)[\s]+?',content)
			if files:
				print files
				for filename in files:
					if len(filename)<=0:
						continue
					ti={}
					fn=get_filename(filename)					
					ti['url']=bu+filename
					ti['ts_name']=fn
					rt.append(ti)
			else:
				print 'no found'
	return rt
	
def parse_cntv_m3u82(ct,url):
	rt=[]	
	if len(ct)>0:
		bu=get_base_uri(url)
		tp='(http[\S]+)[\s]+?'
		turls=re.findall(tp,ct)
		if turls:
			for furl in turls:
				ti={}
				fn=get_filename(furl)
				ti['url']=furl
				ti['ts_name']=fn
				rt.append(ti)
		else:			
			files=re.findall('([^#\n][\S]+\.ts[\S]*)[\s]+?',ct)
			if files:
				for filename in files:
					if len(filename)<=0:
						continue
					ti={}
					fn=get_filename(filename)					
					ti['url']=bu+filename
					ti['ts_name']=fn
					rt.append(ti)
	return rt
	
	
 
if __name__ == "__main__":
	cntv_infos=get_cntv_url()
	for info in cntv_infos:
		print info['videourl']
		print info['img_alt'].decode('utf-8')

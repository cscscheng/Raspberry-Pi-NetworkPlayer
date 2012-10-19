import time
import random
import math
import httplib2
import json
import re

myagent='Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
def get_m3u8url_url(url):
	urls=[]
	h=httplib2.Http()
	headers={'User-Agent':myagent}
	resp,content=h.request(url,'GET',headers=headers)
	if resp.status==200:
		m3u8urls=re.findall('(http.+m3u8)',content)
		if m3u8urls:
			for m3u8url in m3u8urls:
				resp,content=h.request(m3u8url,'GET',headers=headers)
				if resp.status==200:
					real_m3u8urls=re.findall('(http.*)',content)
					if real_m3u8urls:
						for real_m3u8url in real_m3u8urls:
							urls.append(real_m3u8url)
	print urls
	return urls

def get_ipad_url(url):
	base_url='http://tv.cntv.cn'
	urls=[]
	headers={'User-Agent':myagent}
	h=httplib2.Http()
	resp,content=h.request(url,'GET')
	if resp.status==200:
		tv_urls=re.findall('<div class="m_box">[^<]*<h3>[^<]*<a target="_blank" href="([^"]+)">([^<]*)',content)
		if tv_urls:
			for tv_url,play_title in tv_urls:
				fullurl = base_url+tv_url
				resp,content=h.request(fullurl,'GET')
				if resp.status==200:
					ipad_url=re.findall('channelIpad[^"]*"([^"]*)"',content)
					if ipad_url:
						urls.append(ipad_url)
					break
	return urls
	

ipad_urls = get_ipad_url('http://tv.cntv.cn/live')
for url in ipad_urls:
	print url[0]
	m3u8urls = get_m3u8url_url(url[0])
	
	
##点播的比较简单后续有时间加上...
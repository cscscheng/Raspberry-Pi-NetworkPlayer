
# -*- coding: utf-8 -*-  
import httplib2
import re	
import Queue
import threading
import os
import urllib
from bs4 import BeautifulSoup


#'http://ncgi.video.qq.com/tvideo/fcgi-bin/smartbox?plat=2&ver=0&num=10&otype=json&query='
SEARCH_URLS={'utf-8':'http://v.qq.com/search.html?ms_key=%s','utf-8':'http://www.soku.com/search_video/q_%s','gbk':'http://www.soku.com/t/nisearch/%s/','utf-8':'http://search.pptv.com/s_video/q_%s'}


def do_search(kw):
	urls={}
	for (code,search_url) in SEARCH_URLS.items():
		h=httplib2.Http()
		if code != 'utf-8':
			kw = kw.decode('utf-8').encode(code)
		url=search_url%kw
		resp,content=h.request(url,'GET')
		if resp.status==200:
			bs=BeautifulSoup(content)
			url_list = bs.find_all(['a','img'])
			for u in url_list:
				print u
	return urls

do_search('蜘蛛侠')
	
	


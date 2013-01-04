#-*- coding: utf-8 -*-
import httplib2
import re
from bs4 import BeautifulSoup
import time
#'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
#http://vdn.apps.cntv.cn/api/getLiveUrlCommonRedirectApi.do?channel=tm1&urlType=highEdition

def get_qq_video_infos(url,exclude_str=''):
	img_url=[]
	img_alt=[]
	video_url=[]	
	video_with_img = []
	
	h=httplib2.Http()
	html=''
	resp,content=h.request(url)
	if resp.status==200:
		html=content
	soup = BeautifulSoup(html)
	all_img=soup.select("a img")
	for img in all_img:
		img_attrs = img.attrs
		for attr in img_attrs:			
			if attr == 'src' or attr == '_src':
				imgurl=img[attr]
			if attr == 'alt':
				imgalt=img[attr]			
		str=img.find_parent("a")
		if str == None:
			continue;
		videourl = 	str['href']
		if not re.findall("^http://v.qq.com/.+tm|^/cover/",videourl):
			continue
		if len(imgurl)>0 and len(imgalt) >0 and len(videourl)>0:
			if imgurl not in img_url and videourl not in video_url:
				img_url.append(imgurl)
				img_alt.append(imgalt)
				video_url.append(videourl)
				if re.findall("^/cover/",videourl):
					videourl = 'http://v.qq.com'+videourl
				info = {}
				info["img_url"]=imgurl.encode("utf-8")
				info["img_alt"]=imgalt.encode("utf-8")
				info["videourl"] = videourl.encode("utf-8")
				video_with_img.append(info)
	return video_with_img	

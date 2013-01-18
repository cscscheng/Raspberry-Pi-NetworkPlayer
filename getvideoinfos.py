#-*- coding: utf-8 -*-
import httplib2
import re
from bs4 import BeautifulSoup
import time
#'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'
#http://vdn.apps.cntv.cn/api/getLiveUrlCommonRedirectApi.do?channel=tm1&urlType=highEdition


flv_FLVCD_URL='http://www.flvcd.com/parse.php?format=&kw='
high_FLVCD_URL='http://www.flvcd.com/parse.php?format=high&kw='
super_FLVCD_URL='http://www.flvcd.com/parse.php?format=super&kw='

regs={}
regs['youku']='<U>([^<\s]*)'
regs['tudou']='<U>([^<\s]*)'

def geturls(url,ftype='high'):
	returls=[]
	flvcd_url=''
	reg='<N>([^<]*).*?<U>([^<\s]*).*?<X>([0-9]*).*?(<EXPLODEID>([0-9]*)){0,1}'
	h=httplib2.Http()
	if ftype== 'high':
		flvcd_url = high_FLVCD_URL+url
	elif ftype=='super':
		flvcd_url=super_FLVCD_URL+url
	elif ftype=='full':
		##todo
		flvcd_url=super_FLVCD_URL+url
	else:
		flvcd_url=flv_FLVCD_URL+url
	resp,content=h.request(flvcd_url,'GET')
	if resp.status==200:
		index=0
		content=re.sub('[\s]','',content)
		urls=re.findall(reg,content,re.M)
		if urls :
			for filename,url,num,tmp,part in urls:
				filename='file'
				filename=filename+'.PART%d'%index				
				filename=filename+'.mp4'
				info={}
				info['url']=url
				info['fn'] = filename
				info['part'] = num
				returls.append(info)
				index=index+1
			return returls
	return []

#get vidoes channels
def get_channels_info(html,types):
	ret = []
	url_list=[]
	if len(html)<=0:
		return []
	soup = BeautifulSoup(html)
	if types== 'qq':
		div_navs=soup.select('[class*="mod_nav"]')
		for div in div_navs:
			all_a=div.select('a')
			for a in all_a:
				info={}
				url = a['href']
				text=a.text.encode('utf-8')
				if url in url_list or text=='首页' or text=='更多':
					continue	
				url_list.append(url)				
				info['url']=re.sub('^/','http/v.qq.com/',url).encode('utf-8')
				info['words']=text
				print info['url']
				ret.append(info)
	else:
		print 'Type:',types,'not support'
	return ret

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
	all_img=soup.select("a > img")
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


def get_html_source(url,header={}):
	h=httplib2.Http()
	html=''
	if len(header)>0:
		resp,content=h.request(url,headers=header)
		if resp.status==200:
			html=re.sub('[\s]+','',content)
		
	else:
		resp,content=h.request(url)
		if resp.status==200:
			html=re.sub('[\s]+','',content)
			
	return html

def get_video_site_info(html):
	finded = re.find('qq.com',html)
	if finded:
		site_url = site_url+'v.qq.com/'
		return 'qq'
	finded = re.find('youku.com',html)	
	if finded:
		site_url = site_url+'v.youku.com'
		return 'youku'
	finded = re.find('tudou.com',html)
	if finded:
		site_url = site_url+'v.tudou.com'
		return 'tudou'	
	else:
		print 'error not support yet...'
		return ''

def get_video_img_info(html):
	#find site Name
	site_url='http://'
	url_p = '^http://v.qq.com/.+?tm|^/cover/'
	sub_url_p = '^/'
	video_with_img = []
	finded = re.find('qq.com',html)
	if finded:
		site_url = site_url+'v.qq.com/'
		url_p = '^http://v.qq.com/.+tm|^/cover/'
	elif (finded = re.find('youku.com',html)):
		site_url = site_url+'v.youku.com'
		url_p = '^http://v.youku.com/.+?_show'
	elif (finded = re.find('tudou.com',html)):
		site_url = site_url+'v.tudou.com'
		url_p = 'http://v.tudou.com/'
	else:
		print 'error not support yet...'
		return []	

	soup = BeautifulSoup(html)
	all_img=soup.select("a > img")
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
		if not re.findall(url_p,videourl):
			continue
		if len(imgurl)>0 and len(imgalt) >0 and len(videourl)>0:
			if imgurl not in img_url and videourl not in video_url:
				img_url.append(imgurl)
				img_alt.append(imgalt)
				video_url.append(videourl)
				if re.findall(sub_url_p,videourl):
					videourl = site_url+videourl
				info = {}
				info["img_url"]=imgurl.encode("utf-8")
				info["img_alt"]=imgalt.encode("utf-8")
				info["videourl"] = videourl.encode("utf-8")
				video_with_img.append(info)
	return video_with_img
	
	

def get_infos_by_url(url,ext={}):
	
	html=get_html_source(url)
	if len(html)>0:
		return get_video_img_info(html)
	else:
		return []
		
def find_otherpart_infos(url):
	ret=[]
	html=get_html_source(url)
	
	soup = BeautifulSoup(html)	
	aaa=soup.find('div',id='mod_videolist').find_all('a')
	for a in aaa:
		info={}
		u=a['href']
		u2=re.sub('^/','http://v.qq.com/',u)
		info["videourl"]=u2
		info["num"]=a.string.encode('utf-8')
		info['playing_url']=url
		ret.append(info)
	return ret
		

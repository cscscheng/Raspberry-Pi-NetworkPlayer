# -*- coding:utf-8 -*-
from xml.dom import minidom
import cStringIO
import time
import re
import random
import math
import httplib2
import json
#import download
from bs4 import BeautifulSoup


ipadagent='Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/6.1.2 Mobile/7B334b Safari/531.21.10'
IPAD_AGENT={'User-Agent':ipadagent}
#http://v.youku.com/player/getPlayList/VideoIDS/XNDYwMjAxODg4/timezone/+08/version/5/source/video?n=3&ran=7702&password=
#http://v.youku.com/player/getPlayList/VideoIDS/XNTQ3NDk3NDQw/timezone/+08/version/5/source/video/Type/Folder/Fid/19246221/Pt/3/Ob/1?ran=3615&n=3&password=
#http://f.youku.com/player/getFlvPath/sid/{sid}_{part}/st/{st}/fileid/{fileid}?K={K}
#http://f.youku.com/player/getFlvPath/sid/134993084259015909586_00/st/flv/fileid/030002060050756CB493A806257BB68321FDFE-85EE-C6CC-88BB-BBB9031076CE?K=014542bd156ed45124112a4e&hd=0&myp=0&ts=377&ymovie=1&ypp=0
def get_json(VideoIDS):	
	url='http://v.youku.com/player/getPlayList/VideoIDS/'+VideoIDS+'/timezone/+08/version/5/source/video?n=3&ran=7702&password='
	h=httplib2.Http()
	resp,content=h.request(url,'GET',headers=IPAD_AGENT)
	if resp.status==200:
		return content
	else:
		return ""

def get_list_json(Vid,fid,pt,ob):
	url='http://v.youku.com/player/getPlayList/VideoIDS/'+Vid+'/timezone/+08/version/5/source/video/Type/Folder/Fid/'+fid+'/Pt/'+pt+'/Ob/'+ob+'=?n=3&ran=7702&password='
	h=httplib2.Http()
	print url
	resp,content=h.request(url,'GET',headers=IPAD_AGENT)
	if resp.status==200:
		return content
	else:
		return ""
		
def createSid():
    nowTime = int(time.time() * 1000)
    random1 = random.randint(1000,1998)
    random2 = random.randint(1000,9999)
    return "%d%d%d" %(nowTime,random1,random2)

def getFileIDMixString(seed):
    mixed=[]
    source=list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/\:._-1234567890")
    seed=float(seed)
    for i in range(len(source)):
        seed = (seed * 211 + 30031 ) % 65536
        index = math.floor(seed / 65536 * len(source) )
        mixed.append(source[int(index)])
        source.remove(source[int(index)])
    #return ''.join(mixed)
    return mixed

def getFileId(fileId,seed):
    mixed=getFileIDMixString(seed)
    ids=fileId.split('*')
    realId=[]
    for ch in ids:
    	if len(ch)>0:
    		realId.append(mixed[int(ch)])
    return ''.join(realId)
    
def getFullFileId(index,fileId,seed):
	real=''
	fileid=getFileId(fileId,seed)
	index_str='%02X'%index
	real = fileid[:8]+index_str+fileid[10:]	
	return real

#streamtype flv,mp4,hd2
def getFullUrls(vids,streamtype='mp4',is_playlist=0,fid='0',pt='0',ob='0'):
	urls=[]
	json_str=''
	if is_playlist==0:
		json_str = get_json(vids)
	else:		
		json_str = get_list_json(vids,fid,pt,ob)
	if len(json_str)>0:
		jsons=json.loads(json_str)
		#print jsons
		#检查数据有效性
		seed=jsons["data"][0]["seed"]	
		key1=jsons["data"][0]["key1"]
		key2=jsons["data"][0]["key2"]
		segs=jsons["data"][0]["segs"]
		streamfileids = jsons["data"][0]["streamfileids"]
		seconds=jsons["data"][0]["seconds"]
		streamsizes = jsons["data"][0]["streamsizes"]
		titles=jsons["data"][0]["title"]
		for st in streamfileids.keys():
			if st == streamtype:
				break		
		streamtype = st	
		segments=segs[streamtype]
		for i in segments:
			index=int(i['no'])
			sfid=streamfileids[streamtype]
			fullfids=getFullFileId(index,sfid,seed)
			Keys=i['k']
			tmp={}
			tmp['type'] = streamtype
			tmp['provider'] = 'youku'
			tmp["part"] = index
			if streamtype == 'hd2':
				tmp["fileurl"] = 'http://f.youku.com/player/getFlvPath/sid/%s_%02X/st/flv/fileid/%s?K=%s&hd=2&myp=0&ts=200&ymovie=1&ypp=20'%(createSid(),index,fullfids,Keys)
			else:
				tmp["fileurl"] = 'http://f.youku.com/player/getFlvPath/sid/%s_%02X/st/%s/fileid/%s?K=%s'%(createSid(),index,streamtype,fullfids,Keys)
			urls.append(tmp)
	return urls
	
	

#qq video
#id 1wcqlvvpxc7osem
#vid n00125wqynb
#http://vv.video.qq.com/getspeed
#<?xml version="1.0" encoding="utf-8"  standalone="no" ?>
#<root><ip>60.190.252.21</ip><s/><speed>237</speed></root>

#http://vv.video.qq.com/getinfo
#http://vv.video.qq.com/getinfo?charge=0&appver=3%2E0%2E7%2E118&platform=11&speed=237&pid=324C706FAC008B95E5DEEAA359E0EEFF3BF4106B&vids=n00125wqynb&ran=0%2E7268632678315043&otype=xml

#'http://vv.video.qq.com/getkey?ran=0%2E36766051268205047&format=10202&platform=11&vid=n00125wqynb&otype=xml&filename=n00125wqynb%2Ep202%2E1%2Emp4&vt=112&charge=0'

#http://vv.video.qq.com/getkey

#http://115.238.175.2/vlive.qqvideo.tc.qq.com/n00125wqynb.p202.1.mp4?sdtfrom=v10&type=mp4&vkey=B2C7A28FDD576BFB672D1DE0F9349281F695B7EC5F6F4B7AA914D212570ACE06896FEC35AD1D8F6B&level=1&platform=1&br=66&fmt=hd&sp=0
#?sdtfrom=v2&vkey=3C037FA72663E7BEF526D1B44DAF93448CCEA4F329853816630B896CBCEC2DA9FFE97232C1FF39CA&level=3&platform=11

def getVideoInfoByVid(vid):
	GetInfoUrl='http://vv.video.qq.com/getinfo?charge=0&appver=3%2E0%2E7%2E118&platform=11&ran=0%2E7268632678315043&otype=xml&vids='+vid
	#print GetInfoUrl
	h=httplib2.Http()
	resp,content=h.request(GetInfoUrl,'GET',headers=IPAD_AGENT)
	if resp.status==200:
		return content
	else:
		return ""
def getQQVideoKey(vid,fn,fmt):
	print vid
	print fn
	print fmt
	GetKeyUrl = "http://vv.video.qq.com/getkey?ran=0%2E36766051268205047&format="+fmt+"&platform=11&otype=xml&filename="+fn+"&vt=112&charge=0&vid="+vid
	h=httplib2.Http()
	print GetKeyUrl
	resp,content=h.request(GetKeyUrl,'GET',headers=IPAD_AGENT)
	if resp.status==200:
		return content
	else:
		return ""
		
def getQQVideoUrls(vid):
	urls=[]
	streamtype='mp4'
	info_xml = getVideoInfoByVid(vid)
	infos=parseinfoQQxml(vid,info_xml)
	#video_key=getQQVideoKey(vid,infos["filename"],infos["type"])
	
	tmp={}
	tmp['type'] = streamtype
	tmp['provider'] = 'QQ'
	tmp["part"] = 0
	tmp["fileurl"] = ''
	urls.append(tmp)
	return urls

def parseKeyQQxml(xml_str):
	ret = {}
	ret["key"]=''
	ret["level"]=''
	
	xmldoc = minidom.parseString(xml_str)
	keystr = xmldoc.getElementsByTagName("key")
	cn=keystr[0].childNodes
	for fcn in cn:			
		if fcn.nodeType == fcn.TEXT_NODE:						
			ret["key"]=fcn.data
	levelstr = xmldoc.getElementsByTagName("level")
	cn=levelstr[0].childNodes
	for fcn in cn:			
		if fcn.nodeType == fcn.TEXT_NODE:						
			ret["level"]=fcn.data	
	return ret
def parseinfoQQxml(vid,xml_str):
	ret={}
	ret["type"]='mp4'
	ret["urls"]=[]
	ret["title"]=''
	ret["part_count"]=0
	ret["filename"]=''
	file_str=''
	xmldoc = minidom.parseString(xml_str)
	#get fn
	fn=xmldoc.getElementsByTagName("fn")
	#print len(fn)
	cn=fn[0].childNodes
	for fcn in cn:			
		if fcn.nodeType == fcn.TEXT_NODE:
			file_str=fcn.data
	#get urls
	#get pd urls
	pd_urls = []
	pds= xmldoc.getElementsByTagName("pd")	
	for f in pds:
		cn=f.childNodes
		for fcn in cn:			
			if fcn.nodeType == fcn.TEXT_NODE:
				print fcn.data
			else:
				if fcn.nodeType == fcn.ELEMENT_NODE:
					if fcn.nodeName != 'url':
						continue
					cn2 = fcn.childNodes
					for ff2 in cn2:
						if ff2.nodeType== ff2.TEXT_NODE :
							pd_urls.append(ff2.data)
							
	furls=xmldoc.getElementsByTagName("url")	
	for f in furls:
		cn=f.childNodes
		for fcn in cn:			
			if fcn.nodeType == fcn.TEXT_NODE:
				if fcn.data not in pd_urls:
					ret["urls"].append(fcn.data)
	#get part_count
	keyids = xmldoc.getElementsByTagName("keyid")
	ret["part_count"] = len(keyids)
	keyid_str=[]
	for f in keyids:
		cn=f.childNodes
		for fcn in cn:			
			if fcn.nodeType == fcn.TEXT_NODE:
				if fcn.data not in pd_urls:
					keyid_str=fcn.data.split('.')
					break
	
	#get title								
	title_str = xmldoc.getElementsByTagName("ti")
	cn=title_str[0].childNodes
	for fcn in cn:			
		if fcn.nodeType == fcn.TEXT_NODE:						
			ret["title"]=fcn.data
	ret["downloadurls"]=[]
	s=file_str.split('.')
	s_len = len(s)
	ret["type"]=s[s_len-1]
	s.pop(s_len-1)
	ret["filename"]= '.'.join(s)
	for i in range(1,ret["part_count"]+1):
		fn="%s.%d.%s"%(ret["filename"],i,ret["type"])
		key_xml=getQQVideoKey(vid,fn,keyid_str[1])
		key_ret=parseKeyQQxml(key_xml)		
		urls="%s/%s?sdtfrom=v2&vkey=%s&level=%s&platform=11"%(ret["urls"][0],fn,key_ret["key"],key_ret["level"])
		ret["downloadurls"].append(urls)
	return ret
	
#tudou video




def write_to_file(fn,ct,is_new=1):
	if(is_new == 1):
		f=open(fn,'wb')
	else:
		f=open(fn,'ab')
	f.write(ct)
	f.close()


#if __name__ == '__main__':
#	vids='XNTU4NDAxNDg0'
	#urls = getFullUrls(vids,'hd2')
	#print urls	
#	getQQVideoUrls('n00125wqynb')
#	exit()
	
	#json_str=''
	#json_str = get_json(vids)
	#if len(json_str)>0:
	#	jsons=json.loads(json_str)
	#	seed=jsons["data"][0]["seed"]	
	#	key1=jsons["data"][0]["key1"]
	#	key2=jsons["data"][0]["key2"]
	#	segs=jsons["data"][0]["segs"]
	#	streamfileids = jsons["data"][0]["streamfileids"]
	#	seconds=jsons["data"][0]["seconds"]
	#	streamsizes = jsons["data"][0]["streamsizes"]
	#	titles=jsons["data"][0]["title"]
	#	for streamtype in streamfileids.keys():
	#		segments=segs[streamtype]
	#		for i in segments:
	#			index=int(i['no'])
	#			sfid=streamfileids[streamtype]
	#			fullfids=getFullFileId(index,sfid,seed)
	#			Keys=i['k']
	#			print 'http://f.youku.com/player/getFlvPath/sid/%s_%02X/st/%s/fileid/%s?K=%s'%(createSid(),index,streamtype,fullfids,Keys)
				#      http://f.youku.com/player/getFlvPath/sid/136909810990949513880_00/st/flv/fileid/0300010E0051967D0375DE04CB019FCB2E5E47-790F-44E2-C44A-356B58FE8D9E?start=92&K=1fe706337c38cb06261d03d5&hd=2&myp=0&ts=200&ymovie=1&ypp=20
	#print segments


class YoukuParse():
	def __init__(self):
		#
		self.vids=[]
		self.status="inited"
		self.history=[]
		self.vid_index = 0
		self.input_url=''
		self.is_list=0
		self.list_param=[]
		self.list_current_part=0
		
	def set_parse_url(self,url):		
		self.input_url=url
		self.vid_index = 0
		self.list_param=[]
		self.is_list=0
		self.list_current_part=0
		r=self.get_all_vids(url)
		if len(r)>0:
			return 0
		else:
			print 'set_parse_url err: '+url
			return -1
		
	def get_download_urls(self):
		return self.get_next_file_urls()
		
	def write_current_status(self):
		#	
		return 0
	def get_showpage_by_ct(self,ct):
		rt=''
		if len(ct)>100:
			fr=re.findall('"([^"]+show_page/id_[^"]+)"',ct)
			if fr:
				for page_url in fr:
					return page_url		
		return rt
	def get_other_urls_by_content(self,content):
		
		return []
	
	def get_vids_by_pagect(self,pagect):
		ret=[]
		sp=BeautifulSoup(pagect)
		#<li class="price">
		#判断是否是收费视频
		need_buy=sp.find_all("li",class_="price")
		if len(need_buy)>0:
			return []
		find_div=sp.find_all("div",class_="coll_10")
		for div in find_div:
			urls=div.find_all("a")
			for aurl in urls:
				vid=self.get_vids_by_url(aurl["href"])
				if len(vid)>0:
					ret.append(vid)
		if len(ret)== 0:
			baseinfo=sp.find_all("ul",class_="baseinfo")
			for bi in baseinfo:
				urls=bi.find_all("a")
				for aurl in urls:
					vid=self.get_vids_by_url(aurl["href"])
					if len(vid)>0:
						ret.append(vid)
		return ret
		
	def get_playlist_url(self,ct):
		list_url=''
		
		
		il=re.findall('playlist_show',self.input_url)
		if il:
			list_url= self.input_url
		if len(list_url)>0:
			self.is_list = 1
		else:
			self.is_list = 0
		return list_url
		sp=BeautifulSoup(ct)
		all_div=sp.find_all("div",class_="listInfo")
		for div in all_div:
			all_a=div.find_all("a")
			for a in all_a:
				href=a["href"]				
				fs=re.findall('playlist_show',href)
				if fs:
					list_url= href		
		if len(list_url)>0:
			self.is_list = 1
		else:
			self.is_list = 0
		return list_url
	
	def get_all_list_videos(self,ct):
		ret=[]
		vu=''
		sp=BeautifulSoup(ct)
		all_items=sp.find_all("div",class_="items")
		for its in all_items:
			all_ul=its.find_all("ul",class_="v")
			for ul in all_ul:
				all_li=ul.find_all("li",class_="v_link")
				for li in all_li:
					all_a=li.find_all("a")
					for a in all_a:
						vu=a["href"]
						if len(vu)>0:
							ret.append(vu)
		return ret
				
	def get_playlist_param(self,vus):
		#var f="19246221";var o="1"; var p="3";
		ret=[]		
		if len(vus)>0:
			for vu in vus:
				h=httplib2.Http()
				resp,ct=h.request(vu,'GET',headers=IPAD_AGENT)
				param_find=re.findall('var f="([0-9]+)";var o="([0-9]+)"; var p="([0-9]+)";',ct)
				if param_find:
					tmp={}
					fid=''
					ob=''
					pt=''
					vid=self.get_vids_by_url(vu)
					one_part=0
					cvid=''
					
					cvid=self.get_vids_by_url(self.input_url)
					if len(cvid)>0:
						one_part=1
					for fid,ob,pt in param_find:
						tmp["vid"]= vid
						tmp["fid"]=fid
						tmp["ob"]=ob
						tmp["pt"]=pt
						if one_part==0 or len(cvid)==0:
							self.list_param.append(tmp)	
							ret.append(vid)
						elif vid == cvid:
							self.list_param.append(tmp)		
							ret.append(vid)						
		return ret		 
			
	def get_other_vids(self,html):
		#如果是连续剧.获取其他剧集的vids
		#否则返回空
		ret=[]
		page_ct=''
		page_url=''		
		#专辑
		lu=''
		lu=self.get_playlist_url(html)
		if len(lu)>0:
			rt=[]
			ct=''
			if lu != self.input_url:
				h=httplib2.Http()
				resp,ct=h.request(lu,'GET',headers=IPAD_AGENT)
			else:
				ct=html
			rt=self.get_all_list_videos(ct)			
			if len(rt)>0:
				r=self.get_playlist_param(rt)
				ret = r
				if len(ret)>0:
					return ret			
		
		page_url=self.get_showpage_by_ct(html)
		if len(page_url)>0:
			h=httplib2.Http()
			resp,page_ct=h.request(page_url,'GET',headers=IPAD_AGENT)
			ret=self.get_vids_by_pagect(page_ct)
			if len(ret)>0:
				return ret
				
		other_url=self.get_other_urls_by_content(html)
		if len(other_url)>0:
			for vid_url in other_url:
				vid_string=self.get_vids_by_url(vid_url["url"])
				if len(vid_string)>0:
					ret.append(vid_string)
		return ret
		
	def get_vids_by_content(self,ct):
		find_result=re.findall("var videoId2= '([0-9a-zA-Z]*)';",ct)
		if find_result:
			for vid in find_result:
				if len(vid)>0:
					return vid			
		return ""
		
	def get_vids_by_url(self,url):
		#根据URL获取 vids
		if len(url)>4:
			find_url_result=re.findall('.*v_show/id_([0-9a-zA-Z]*)\.',url)
			if find_url_result:
				for vd in find_url_result:
					if len(vd)>0:
						return vd
		return ""
		
	def get_all_vids(self,url):
		ret=[]
		ct = ''
		cur_vid = ''
		if len(url)>4:
			h=httplib2.Http()
			resp,ct=h.request(url,'GET',headers=IPAD_AGENT)
		other_vid=self.get_other_vids(ct)
		if len(other_vid)>0:
			ret = other_vid
		for avid in ret:
			self.vids.append(avid)
		if len(ret)==0:
		#可能是单一文件,也一样..通过 show_page页面来获取
			cur_vid=self.get_vids_by_url(url)
			if len(cur_vid)>0:
				self.vids.append(cur_vid)
				ret.append(cur_vid)
		return ret	
			
	def	get_next_file_urls(self,iindex=-1):
		#获取下一集的下载地址..
		if iindex != -1:
			if iindex >=0 and iindex < len(self.vids):				
				ivid=self.vids[self.iindex]
				self.vid_index = ivid+1
				return self.get_downloadurls_by_vids(ivid)
				
		if len(self.vids)>0 and self.vid_index<len(self.vids):
			next_vid = self.vids[self.vid_index]
			if self.vid_index < len(self.vids):
				self.vid_index += 1
			return self.get_downloadurls_by_vids(next_vid)
		else:
			return []	
	def get_downloadurls_by_vids(self,vids):
		#根据vids 获取下载地址
		#return getFullUrls(vids)		
		if self.is_list == 0:
			return getFullUrls(vids)
		elif self.is_list==1:
			fids=''
			obs=''
			pts=''			
			for para in self.list_param:
				if vids==para["vid"]:
					fids=para["fid"]
					obs=para['ob']
					pts=para['pt']
					return getFullUrls(vids,'mp4',1,fids,pts,obs)
			else:
				return []		
if __name__ == "__main__":
	yp=YoukuParse()	
	rt=yp.set_parse_url('http://www.youku.com/playlist_show/id_19246221.html')
	if rt == 0:
		us=yp.get_download_urls()
		print us
		while len(us)>0:
			us=yp.get_download_urls()
			print us
	else:
		print 'set_parse_url error2'
	
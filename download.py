#-*- coding: utf-8 -*-
import httplib2
import re
import time
import json
import os
import Queue
import threading
import pycurl
import HTMLParser

class ThreadDownloadManage(threading.Thread):
	"""Threaded Download"""
	def __init__(self):
		threading.Thread.__init__(self)
		self.url={}
		#wait to download
		self.threads=[]
		
		self.status='inited'
		
		#downloading thread
		self.work_thread = []
		self.need_cancel = False
	def set_url(self,url_list):
		start = 0
		if len(url_list)>0:	
			self.need_cancel = False		
			for one in url_list:			
				d_url=one['url']
				#print 'add url',d_url
				h = HTMLParser.HTMLParser()
				d_url = h.unescape(d_url)
				d_fn=one['fn']	
				th=ThreadDownload(d_url,d_fn,start)
				th.setDaemon(True)
				self.threads.append(th)
				start += 1
		else:
			self.need_cancel=True
		self.url=url_list
	def cancel_donwload(self):
		print 'cancel_donwload'
		for th in self.work_thread:
			th.cancel()
		while len(self.threads)>0:
			self.threads.pop()
		while len(self.work_thread)>0:
			self.work_thread.pop()
		
	def run(self):
	  while True:	  	
			if len(self.threads)>0 or len(self.work_thread)>0:	
				#print 'threads ',len(self.threads),'workthread ',len(self.work_thread)			
				for i in range(len(self.work_thread)):					
					th=self.work_thread[i]
					if not th.isAlive():						
						self.work_thread.pop(i)
						th.join()
						break
				if len(self.work_thread)<2 and len(self.threads)>0:
					th=self.threads.pop(0)
					self.work_thread.append(th)
					print 'start download thread'	
					th.start()
				time.sleep(0.2)
				if self.need_cancel:
					cancel_donwload()
			else:
				print 'no need to download'
				time.sleep(1)
						
			
			
			
class ThreadDownload(threading.Thread):
	"""Threaded Download"""
	def __init__(self,url,fn,i):
		threading.Thread.__init__(self)
		self.cancel_donwload = 0
		self.download_total=0
		self.down_status=0
		self.downloaded=0
		self.notify_player=0
		self.download_index=i
		if len(url)>0:			
			self.url=url
			self.fn=fn			
			self.pycurl_instance=pycurl.Curl()
			self.pycurl_instance.setopt(pycurl.URL,url)
			self.pycurl_instance.setopt(pycurl.WRITEFUNCTION, self.write_call_back)
			self.pycurl_instance.setopt(pycurl.NOPROGRESS, 0)
			self.pycurl_instance.setopt(pycurl.PROGRESSFUNCTION, self.process_call_back)
			self.pycurl_instance.setopt(pycurl.FOLLOWLOCATION, 1)
			self.pycurl_instance.setopt(pycurl.MAXREDIRS, 5)
			#self.pycurl_instance.setopt(pycurl.VERBOSE,1)
			self.pycurl_instance.setopt(pycurl.CONNECTTIMEOUT,5)
			#self.pycurl_instance.setopt(pycurl.USERAGENT,'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:50')			
			self.pycurl_instance.setopt(pycurl.USERAGENT,'Mozilla/5.0 (Windows NT 6.1; rv:18.0) Gecko/20100101 Firefox/18.0')
			#ch=['DNT: 1','Referer: http://player.pplive.cn/ikan/2.1.7.3/player4player2.swf']
			#self.pycurl_instance.setopt(pycurl.HTTPHEADER,ch)
			#self.pycurl_instance.setopt(pycurl.
			
		else:
			print 'error url'
			
	def write_call_back(self,buf):
		if self.cancel_donwload == 1:			
			print 'download canceled...'
			return -1
		else:
			self.f.write(buf)	
		
	def process_call_back(self,download_t, download_d, upload_t, upload_d):
		if self.download_total == 0:
			self.download_total = download_t
		self.downloaded = download_d
		if self.downloaded>(1024*1024) and self.download_index==0 and self.notify_player==0:
			print 'start player now...:',self.downloaded
			self.notify_player=1
		   
	def cancel(self):
		print 'cancel download....111'
		self.cancel_donwload = 1
		
	def get_status(self):
		return self.down_status
	
	def debuginfo(self):
		print 'SPEED_DOWNLOAD:',self.pycurl_instance.getinfo(pycurl.SPEED_DOWNLOAD)
		print 'TOTAL_TIME:',self.pycurl_instance.getinfo(pycurl.TOTAL_TIME)
		#print 'INFO_FILETIME',self.pycurl_instance.getinfo(pycurl.INFO_FILETIME)
		print 'CONTENT_LENGTH_DOWNLOAD',self.pycurl_instance.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
	
	def run(self):
		print self.fn
		self.f=open(self.fn,'wb')
		try:
			self.pycurl_instance.perform()
			if self.download_total != self.downloaded:
				self.down_status = 1
				print 'download error total:',self.download_total,'downloaded:',self.downloaded
			else:
				self.down_status = 1
				print "download finised index:",self.download_index," total:",self.download_total
		except:
			if(self.cancel_donwload == 1):
				print 'download canceled...index:',self.download_index
				self.down_status = 1
			else:
				print 'download error..'
				self.down_status = 1
			pass
		self.debuginfo()

def test_download():
	h = HTMLParser.HTMLParser()
	url='http://v.pptv.com:8080/0/decc213aa48a94a0f3f9fafa0257cf6a.mp4?key=7c9d2ab10d3958cd9ce518888ea21f9d'
	url=h.unescape(url).encode('utf-8')
	print url
	dt=ThreadDownload(url,'./test.mp4',0)
	dt.setDaemon(True)
	dt.start()
	#time.sleep(3)
	#dt.cancel()
	dt.join()


#test_download()
	
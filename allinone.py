import httplib2
import re	
import urllib2
import Queue
import threading
import os

urlqueue=Queue.Queue()
respqueue=Queue.Queue()


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
				#filename=filename.decode('gbk').encode('utf-8')
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
	
def download_file(url):
	index=0
	allurls = geturls(url)
	keylist = sorted(allurls.keys())
	ret = 1
	for key in keylist:
		while ret != 0:
			downloadcmd='curl -L -s %s -o/root/movie/%s'%(allurls[key],key)
			ret = os.system(downloadcmd)
			if ret != 0:#download failed
				print 'download failed'
				allurls.clear()
				allurls = geturls(url)
				continue					
			index = index+1
			if (index&7)==0:
				allurls.clear()
				allurls = geturls(url)
	

#download_file('http://www.tudou.com/albumcover/ZZl6Oc9rIGc.html')
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

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = urlqueue
        self.out_queue = respqueue
        self.data={}
    def run(self):
        while True:
            #grabs host from queue
            urlinfo = self.queue.get()
            #grabs urls of hosts and then grabs chunk of webpage
            for key in urlinfo:
            	filename=key
            	host=urlinfo[key]
            	print 'thread start working...file:%s host:%s',filename,host
            	file=open(filename,'w')
            	url = urllib2.urlopen(host)
            	chunk = url.read()
            	file.write(chunk)
            	#self.data[host]=chunk
            #place chunk into out queue

            #signals to queue job is done
            self.queue.task_done()

def geturls(url):
	returls={}
	reg='<N>([^<]*).*?<U>([^<\s]*)'
	h=httplib2.Http()
	flvcd_url = high_FLVCD_URL+url
	resp,content=h.request(flvcd_url,'GET')
	if resp.status==200:
		index=0
		content=re.sub('[\s]','',content)
		urls=re.findall(reg,content,re.M)
		if urls :
			for filename,url in urls:
				filename=filename.decode('gbk').encode('utf-8')
				filename=filename+'.PART%d'%index
				#filename=re.sub('-0*','.PART',filename)
				filename=filename+'.mp4'
				#print filename.decode('utf-8')
				returls[filename]=url
				index=index+1
			return returls
		else:
			flvcd_url = flv_FLVCD_URL+url
			resp,content=h.request(flvcd_url,'GET')
			if resp.status==200:
				content=re.sub('[\s]','',content)
				urls=re.findall(reg,content)
				if urls :
					for filename,url in urls:
						filename=filename.decode('gbk').encode('utf-8')
						filename=filename+'.PART%d'%index
						filename=filename+'.flv'
						#print filename.decode('utf-8')
						returls[filename]=url
						index=index+1
			return returls
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
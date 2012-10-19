import httplib2
import re
import time
import json
import os

last_time_dict={}
loop = True;

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
	print lists
	return lists

##这里直接用replace替换掉反斜杠会更好..我不会用replace..哈哈..python现学.先用的.
##可能有bug没仔细调试过..频道名称也没取出来..
def gen_m3u8_url(in_url,id):
	return_urls=[]
	h=httplib2.Http()
	resp,content=h.request(in_url,'GET')
	if resp.status==200:
		urls=re.findall('<[^<]+show_playing[^>]+>[^<]*<[^"]*".+\/([a-zA-Z0-9]*)\.html[^"]*".+>',content)
		if urls:				
			for url in urls:
				resp,content=h.request('http://v.pptv.com/show/'+url+'.html','GET')
				if resp.status==200:
					play_ids=re.findall('"ipadurl":"[^"]+web-m3u8-([0-9]+).m3u8"',content)
					if play_ids:
						for play_id in play_ids:
							m3u8url = 'http://web-play.pptv.com/web-m3u8-'+play_id+'.m3u8'
							return_urls.append(m3u8url)
	print return_urls
	return return_urls
				

if __name__ == '__main__':
	id='21'
	pptv_lists=gen_pptv_list()
	gen_m3u8_url(pptv_lists[id]['url'],id)
	
	
### omxplayer 直接支持m3u8的HLS流媒体播放..
	
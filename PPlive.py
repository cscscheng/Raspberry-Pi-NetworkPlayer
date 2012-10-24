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
	#print lists
	return lists

def gen_m3u8_url(in_url,id):
	return_urls=[]
	h=httplib2.Http()
	resp,content=h.request(in_url,'GET')
	if resp.status==200:
		#print content
		urls=re.findall('>(\\\u[^<]*)<[^>]*>[^<]*<[^>]*>[^<]*<[^<]+show_playing[^>]+>[^<]*<[^"]*"([^"]*)"[^>]+>[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>[^<]*[^<]*<[^>]*>([^<]*)<',content)
		#urls=re.findall('<[^<]+show_playing[^>]+>[^<]*<[^"]*"([^"]*)"[^>]+>',content)
		if urls:			
			for name,url,titles in urls:
				res={}
				js='["list", {"name":["%s","%s"]}]'%(name,titles)
				j=json.loads(js)
				#print j[1]['name'][0]
				#print j[1]['name'][1]
				url = url.replace('\\','')
				res["tv_name"]=j[1]['name'][0]
				res["playing"]=j[1]['name'][1]
				print url
				resp,content=h.request(url,'GET')
				if resp.status==200:
					play_ids=re.findall('"ipadurl":"([^"]+)"',content)
					if play_ids:
						for play_id in play_ids:
							m3u8url = play_id.replace('\\','')
							res["url"]=m3u8url
							return_urls.append(res)
	#print return_urls
	return return_urls
				

if __name__ == '__main__':
	#id='25'
	pptv_lists=gen_pptv_list()
	for id in pptv_lists.keys():
		urls=gen_m3u8_url(pptv_lists[id]['url'],id)
		for url in urls:
			print url

	
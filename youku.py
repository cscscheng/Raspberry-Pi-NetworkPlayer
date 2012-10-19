import time
import random
import math
import httplib2
import json

#http://v.youku.com/player/getPlayList/VideoIDS/XNDYwMjAxODg4/timezone/+08/version/5/source/video?n=3&ran=7702&password=
#
#http://f.youku.com/player/getFlvPath/sid/{sid}_{part}/st/{st}/fileid/{fileid}?K={K}
#http://f.youku.com/player/getFlvPath/sid/134993084259015909586_00/st/flv/fileid/030002060050756CB493A806257BB68321FDFE-85EE-C6CC-88BB-BBB9031076CE?K=014542bd156ed45124112a4e&hd=0&myp=0&ts=377&ymovie=1&ypp=0
def get_json(VideoIDS):
	url='http://v.youku.com/player/getPlayList/VideoIDS/'+VideoIDS+'/timezone/+08/version/5/source/video?n=3&ran=7702&password='
	h=httplib2.Http()
	resp,content=h.request(url)
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
	
if __name__ == '__main__':
	vids='XNDYwMjAxODg4'
	json_str=''
	json_str = get_json(vids)
	if len(json_str)>0:
		jsons=json.loads(json_str)
		seed=jsons["data"][0]["seed"]	
		key1=jsons["data"][0]["key1"]
		key2=jsons["data"][0]["key2"]
		segs=jsons["data"][0]["segs"]
		streamfileids = jsons["data"][0]["streamfileids"]
		seconds=jsons["data"][0]["seconds"]
		streamsizes = jsons["data"][0]["streamsizes"]
		titles=jsons["data"][0]["title"]
		for streamtype in streamfileids.keys():
			segments=segs[streamtype]
			for i in segments:
				index=int(i['no'])
				sfid=streamfileids[streamtype]
				fullfids=getFullFileId(index,sfid,seed)
				Keys=i['k']
				print 'http://f.youku.com/player/getFlvPath/sid/%s_%02X/st/%s/fileid/%s?K=%s'%(createSid(),index,streamtype,fullfids,Keys)
				
			#print segments
###这个是测试代码....
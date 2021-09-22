# -*- coding: utf-8 -*-
import math
import sys 
import urllib,urllib2
import commands,time
import configparser
import os
import json
import threading 
from collections import OrderedDict

class myconf(configparser.ConfigParser):
	def __init__(self,defaults=None):
		configparser.ConfigParser.__init__(self,defaults=None)
	def optionxform(self, optionstr):
		return optionstr


def mongoState(machineIdList ,url_ResourceInfo ,user ,password ,dbname ,address ,command):
	headers = {"Content-Type":"application/json" ,"token":"monitoring_6496d6c7422146fab147ca11d61c19bd"}
	os.environ['user'] = str(user)
	os.environ['password'] = str(password)
	os.environ['dbname'] = str(dbname)
	os.environ['address'] = str(address)
	os.environ['command'] =str(command)

	while True:
		try:
			mongostat = commands.getoutput("$command -n 1 1 --username=$user --password=$password --authenticationDatabase=$dbname --host=$address --noheaders --json --humanReadable=false")
			print(mongostat)
			text = json.loads(mongostat)
		#	print(type(text))
			stat = text[address]
			print(stat['getmore'] ,stat['vsize'] ,stat['insert'] ,stat['query'] ,stat['update'] ,stat['delete'] ,stat['command'] ,stat['dirty'] ,stat['flushes'] ,stat['used'] ,stat['res'] ,stat['qrw'] ,stat['arw'] ,stat['net_in'] ,stat['net_out'] ,stat['conn'] ,stat['repl'] ,stat['set'])
			insert = stat['insert']
			insert = int(insert.replace('*',''))
			print(insert)
			query = stat['query']
			query = int(query.replace('*',''))
			print(query)
			update = stat['update']
			update = int(update.replace('*',''))
			print(update)
			delete = stat['delete']
			delete = int(delete.replace('*',''))
			print(delete)
			getmore = stat['getmore']
			getmore = int(getmore.replace('*',''))	
			print(getmore)
			localCommand = int(str(stat['command']).split('|')[0])
			print(localCommand)
			replicatedCommand = int(str(stat['command']).split('|')[1])
			print(replicatedCommand)
			dirty = float(stat['dirty'])
			print(dirty)
			used = float(stat['used'])
			print(used)
			flushes = int(stat['flushes'])
			print(flushes)
			vsize = float(stat['vsize'])/1024/1024
			print(vsize)
			res = float(stat['res'])/1024/1024
			print(res)
			qw = int(str(stat['qrw']).split('|')[0])
			print(qw)
			qr = int(str(stat['qrw']).split('|')[1])
			print(qr)
			aw = int(str(stat['arw']).split('|')[0])
			print(aw)
			ar = int(str(stat['arw']).split('|')[1])
			print(ar)
			netIn = float(stat['net_in'])
			print(netIn)
			netOut = float(stat['net_out'])
			print(netOut)
			conn = int(stat['conn'])
			print(conn)
			repl = stat['repl']
			print(repl)
			set1 = stat['set']
			print(set1)
			for machineId in machineIdList.split(','):
				resourceInfo = mongoStateJsonTrans(machineId ,insert ,query ,update ,delete ,getmore ,localCommand ,replicatedCommand ,flushes \
,dirty ,used ,vsize ,res ,qw ,qr ,aw ,ar ,netIn ,netOut ,conn ,repl ,set1)
				print time.asctime(time.localtime(time.time()))
				print(url_ResourceInfo,resourceInfo)
				print("每分钟数据上报，" + resourceInfo )
				request = urllib2.Request(url_ResourceInfo ,data = resourceInfo ,headers = headers)
				r = urllib2.urlopen(request ,timeout=10)
				code = r.getcode()
				r = r.read()
				print(r ,code)
			time.sleep(60)
		except Exception, e:
			print(str(e) + '每分钟数据上报异常')
			time.sleep(300)


#硬件信息转为规定json
def mongoStateJsonTrans(*numbers):
	post_Item = OrderedDict()
	resourceInfo = ["configId", "inserts" ,"query", "update" ,"delete" ,"getmore" ,"localCommand" ,"replicatedCommand" ,"flushes" \
	,"dirty" ,"used" ,"vsize" ,"res" ,"qw" ,"qr" ,"aw" ,"ar" ,"netIn" ,"netOut" ,"conn" ,"repl" ,"set"]
	numbers = list(numbers)
	for single_item,single_value in zip(resourceInfo ,numbers):
		single_item = str(single_item)
		post_Item[single_item] = single_value
	json.encoder.FLOAT_REPR = lambda x: format(x,'.2f')
	second_Post = json.dumps(post_Item)
	return(second_Post)


def main():
	headers = {"Content-Type":"application/json" ,"token":"monitoring_6496d6c7422146fab147ca11d61c19bd"}
	conf = configparser.ConfigParser()
	conf.read('mongodb.properties')
	url = conf.get("section" ,"url")
	configId = conf.get("section", "configId")
	dbname = conf.get("section", "DB")
	user = conf.get("section", "DB_USER")
	password = conf.get("section", "DB_PASS")
	address = conf.get("section", "address")
	command = conf.get("section", "command")
	threads = []
	url_ResourceInfo = str(url)
	t1 = threading.Thread(target = mongoState ,args = (configId ,url_ResourceInfo ,user ,password ,dbname ,address ,command))
	threads.append(t1)
	for resourceInfo in range(len(threads)): 
		threads[resourceInfo].start()

if __name__== "__main__":
	main()

#coding=utf8

def parse_args():
	"""Fetch args as dict from command
	
	Returns:
		A dict representing the system args.
		example:
		{'config': 0, 'begin': 0, 'path': ['./20123.xls'], 'end': 0}
	"""
	import argparse
	import sys
	# APP_DESC="""
	# this is desc.
	# """
	# print(APP_DESC)

	if len(sys.argv) == 1:
	    sys.argv.append('--help')
	parser = argparse.ArgumentParser()
	parser.add_argument('-b', '--begin', default=0, help="需要导出记录的起始时间(和字段形式一致), 缺省为最早时间")
	parser.add_argument('-e', '--end', default=0, help="需要导出记录的终止时间(和字段形式一致), 缺省为最新时间")
	parser.add_argument('-c', '--config', default=0, help="配置文件路径(如: /home/user/aptexp.conf), 缺省为指定字段")
	parser.add_argument('path', metavar='PATH', nargs=1, help="输出xls文件保存路径(如: /home/user/20180403.xls)")
	args = parser.parse_args()
	# 获取对应参数只需要args.quality,args.url之类.
	# url = (args.path)[0]
	return vars(args)

def parse_time(begin, end, fields='Date'):
	res = {"vendors": { "$exists" : True}}
	if(begin != 0 and end != 0):
		res[fields] = {"$gte" : begin, "$lte" : end}
	elif(begin == 0 and end != 0):
		res[fields] = {"$lte" : end}
	elif(begin != 0 and end == 0):
		res[fields] = {"$gte" : begin}


	print("================ time-res ================")
	print(res)

	return res


def export():
	
	args = parse_args()
	from aptexpy.generate import GenerateXls
	from aptexpy.query import MongoQuery
	from aptexpy.config import Config
	# import hashlib

	

	# -c config 
	conf = None
	mquery = None
	if(args['config'] == 0):
		limits = parse_time(args['begin'], args['end'])
		mquery = MongoQuery(limits=limits)
	else:
		conf = Config(args['config'])
		limits = parse_time(args['begin'], args['end'], conf.get_time('time'))
		mquery = MongoQuery(fields=conf.get_fields_inf(), params=conf.get_link_inf(),limits=limits)
	test = GenerateXls(args['path'][0],'w')

	# {"age" : {"$gte" : 18, "$lte" : 30}}


	result = mquery.parse_collection()
	test.appendHeadLine(mquery.head)
	mquery.close()
	test.appendMultiLines(result)
	test.exportXLS()



if __name__ == '__main__':
	
	export()
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
	parser.add_argument('-b', '--begin', default=0, help="需要导出记录的起始时间(如: 20170801), 缺省为最早时间")
	parser.add_argument('-e', '--end', default=0, help="需要导出记录的终止时间(如: 20180801), 缺省为最新时间")
	parser.add_argument('-c', '--config', default=0, help="配置文件路径(如: /home/user/aptexp.conf), 缺省为指定字段")
	parser.add_argument('path', metavar='PATH', nargs=1, help="输出xls文件保存路径(如: /home/user/20180403.xls)")
	args = parser.parse_args()
	# 获取对应参数只需要args.quality,args.url之类.
	# url = (args.path)[0]
	return vars(args)


def export():
	
	args = parse_args()
	from aptexpy.generate import GenerateXls
	from aptexpy.query import MongoQuery
	# import hashlib

	mquery = MongoQuery()

	test = GenerateXls(agrs.path,'w')
	result = mquery.parse_collection()
	test.appendHeadLine(mquery.head)
	test.appendMultiLines(result)
	test.exportXLS()

if __name__ == '__main__':
	
	export()
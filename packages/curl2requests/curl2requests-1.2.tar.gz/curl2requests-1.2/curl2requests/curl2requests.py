#!/usr/bin/env python3
#coding: utf-8
# Author: mark0smith
# Blog: https://a4m.github.io/

import json
import argparse
import sys 



def curl2requests(command):
	if len(command) <= 5 or 'curl' not in command:
		print('\033[1;31;47mWrong CURL command !\033[0m')
		exit(1)
		return	None

	info = {}
	Request_Method="GET"

	if "--insecure" in command:
		info['Verify']=False
		command = command.replace('--insecure','')
		command = command.replace('--compressed','')

	if "--data" in command:
		info['data'] = {}
		Request_Method="POST"
		_data = command.split('--data')[-1].split("'")[1]
		command = command.split('--data')[0]
		for i in _data.split('&'):
			name = i.split('=')[0]
			value = i.split('=')[-1]
			info['data'][name]=value

	_list = command.strip().split('-H')
	url = _list[0].split("'")[1]
	
	headers = {}
	cookie = {}
	for item in _list[1:]:
		if 'cookie' in item or 'Cookie' in item:
			full = item.split("'")[1].split(': ')[-1].split(";")
			for item in full:
				both = item.split("=")
				name = both[0].strip()
				value = both[1].strip()
				cookie[name] = value
		else:
			both = item.split("'")[1].split(":")
			name = both[0].strip()
			value = both[1].strip()
			headers[name] = value

	info['url']=url
	info['headers'] = headers
	info['cookies'] = cookie
	info['Request_Method']=Request_Method
	return info

def parser_info(info,show_script=False):
	print(json.dumps(info,ensure_ascii=False,indent=2))

def main():
	description = "Convert CURL command into Python Requests Script by mark0smith"
	parser = argparse.ArgumentParser(
		add_help=True,
		description=description,
		)
	parser.add_argument("-s","--stdin",
		help="Add CURL command from stdin",
		required=False
		)
	parser.add_argument("-f","--filename",
		help="Read CURL command from given file",
		required=False
	)

	parser.add_argument("-r","--request",
		help="Show py script",
		required=False
	)
	
	if len(sys.argv) < 2:
		parser.parse_args(["-h"])

	args = parser.parse_args()
	if args.stdin :
		command = sys.stdin.read()
		info = curl2requests(command)
		parser_info(info)
	if args.filename :
		with open(args.filename) as fr:
			info = curl2requests(fr.read())
			parser_info(info)

	c = """"""
	# print(json.dumps(curl2requests(c),ensure_ascii=False,indent=2))

if __name__=='__main__':
	main()

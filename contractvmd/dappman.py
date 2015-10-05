#!/usr/bin/python3
# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import json
import sys
import os
import getopt

from . import config


def usage ():
	print ('Usage:', sys.argv[0], '[option] action')
	print ('Actions:')
	print ('\t-s, --search=query\t\tsearch for a dapp')
	print ('\t-i, --install=url/name\t\tinstall a dapp by its git repository or by its name')
	print ('\t-ii, --info=url/name\t\treturn informations about a dapp')
	print ('\t-r, --remove=name\t\tremove an installed dapp')
	print ('\t-l, --list\t\t\tlist installed dapps')
	print ('\t-c, --create\t\t\tcreate a new empty dapp starting from a template')
	print ('\t-h, --help\t\t\this help')
	print ('\t-v, --version\t\t\tversion')
	print ('')
	print ('Options:')
	print ('\t-d,--data=path\t\t\tspecify a custom data directory path (default: '+config.DATA_DIR+')')

def create_wizard ():
	name = raw_input ('Dapp name: ')
	

def main ():
	#try:
	opts, args = getopt.getopt(sys.argv[1:], "s:i:ii:r:lchd:v", ["help", "version", "search", "data="])
	#except getopt.GetoptError:
	#	usage()
	#	sys.exit(2)


	# Parse options
	for opt, arg in opts:
		if opt in ("-D", "--data"):
			config.DATA_DIR = os.path.expanduser (arg)

	# Loading config file
	try:
		f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'r')
	except:
		print ('cannot read configuration file:', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		sys.exit (0)
	conf = f.read ()
	f.close ()


	# Parse actions
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage ()
			sys.exit ()

		elif opt in ("-v", "--version"):
			print (config.APP_VERSION)
			sys.exit ()


		elif opt in ("-l", "--list"):
			print ('installed dapps:')
			sys.exit ()


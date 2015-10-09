#!/usr/bin/python3
# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import shutil
import json
import sys
import os
import getopt

from . import config


def usage ():
	print ('Usage:', sys.argv[0], '[option] action')
	print ('Actions:')
	print ('\t-s, --search=query\t\tsearch for a dapp')
	print ('\t-i, --install=url\t\tinstall a dapp by its git repository or by its name')
	print ('\t-ii, --info=url\t\t\treturn informations about a dapp')
	print ('\t-r, --remove=name\t\tremove an installed dapp')
	print ('\t-u, --update=name\t\tupdate an installed dapp')
	print ('\t-l, --list\t\t\tlist installed dapps')
	print ('\t-c, --create\t\t\tcreate a new empty dapp starting from a template')
	print ('\t-h, --help\t\t\tthis help')
	print ('\t-v, --version\t\t\tsoftware version')
	print ('')
	print ('Options:')
	print ('\t-d,--data=path\t\t\tspecify a custom data directory path \n\t\t\t\t\t(default: '+config.DATA_DIR+')')

def create_wizard ():
	name = raw_input ('Dapp name: ')

def save_conf (fpath, conf):
	f = open (fpath, 'w')
	f.write (json.dumps (conf))
	f.close ()

def main ():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:i:ii:r:lchd:v", ["help", "version", "search", "data=", "list", "install"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)


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
	conf = json.loads (f.read ())
	f.close ()

	try:
		os.mkdirs (config.DATA_DIR + '/dapps/')
	except:
		pass


	# Parse actions
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage ()
			sys.exit ()

		elif opt in ("-v", "--version"):
			print (config.APP_VERSION)
			sys.exit ()

		elif opt in ("-i", "--install"):
			print ('installing', arg, '...')

			# Cleaning temp tree
			try:
				shutil.rmtree (config.DATA_DIR + '/dapps/temp/')
			except:
				pass

			# Cloning
			os.system ('git clone ' + arg + ' ' + config.DATA_DIR + '/dapps/temp')

			manifest = {}
			try:
				f = open (config.DATA_DIR + '/dapps/temp/manifest.json', 'r')
				manifest = json.loads (f.read ())
				f.close ()
			except:
				print ('no manifest.json or malformed manifest')
				sys.exit ()

			if not 'name' in manifest:
				print ('no dapp name in manifest.json')
				sys.exit ()

			# Move the cloned repository
			# Move the cloned repository
			if os.path.isdir (config.DATA_DIR + '/dapps/' + manifest['name'].lower ()):
				print ('dapp already installed, reinstalling')
				shutil.rmtree (config.DATA_DIR + '/dapps/' + manifest['name'].lower ())

			os.rename (config.DATA_DIR + '/dapps/temp/', config.DATA_DIR + '/dapps/' + manifest['name'].lower ())

			# Config update
			if not manifest['name'].lower () in conf['dapps']['list']:
				conf['dapps']['list'].append (manifest['name'].lower ())

			if not manifest['name'].lower () in conf['dapps']['enabled']:
				conf['dapps']['enabled'].append (manifest['name'].lower ())

			save_conf (config.DATA_DIR + '/' + config.APP_NAME + '.json', conf)

			print (manifest['name'], 'is now installed')

			sys.exit ()

		elif opt in ("-l", "--list"):
			print ('installed dapps:')
			for dapp in conf['dapps']['list']:
				print (dapp)
			print ('enabled dapps:')
			for dapp in conf['dapps']['enabled']:
				print (dapp)
			sys.exit ()

	usage ()

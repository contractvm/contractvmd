#!/usr/bin/python3
# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import shutil
import json
import sys
import os
import getopt
import requests

from . import config

DAPP_LIST_URL = "https://raw.githubusercontent.com/contractvm/dapp-list/master/list.json"

def usage ():
	print ('Usage:', sys.argv[0], '[option] action')
	print ('Actions:')
	#print ('\t-s, --search=query\t\tsearch for a dapp')
	print ('\t-i, --install=url\t\tinstall a dapp by its git repository or by its name')
	#print ('\t-ii, --info=url\t\t\treturn informations about a dapp')
	print ('\t-r, --remove=name\t\tremove an installed dapp')
	print ('\t-u, --update=name\t\tupdate an installed dapp')
	print ('\t-c, --reset=name\t\treset an installed dapp state')
	print ('\t-l, --list\t\t\tlist installed dapps')
	print ('\t-w, --create\t\t\tcreate a new empty dapp starting from a template')
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

def download_list ():
	print ('Downloading dapps catalog...')
	r = requests.get (DAPP_LIST_URL)
	d = r.json ()['dapps']
	print ('Dapps catalog contains', len (d), 'dapps')
	return d

def main ():
	catalog = download_list ()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:i:k:r:lwhd:vu:c:", ["reset=", "update=", "help", "version", "search=", "data=", "list", "install="])
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
		print ('Cannot read configuration file:', config.DATA_DIR+'/'+config.APP_NAME+'.json')
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

		elif opt in ("-c", "--reset"):
			dapp = arg.lower ()
			print ('Resetting state of', dapp)
			r = input ('Are you sure (y/n)? ').lower ()
			if r == 'y':
				for f in os.listdir (config.DATA_DIR + '/dapps/'):
					if f[0:6] == 'state_' and f[-3:] == 'dat' and f[6:6+len(dapp)] == dapp:
							os.remove (config.DATA_DIR + '/dapps/' + f)
							print ('Deleted', f)

			sys.exit (0)


		elif opt in ("-u", "--update"):
			dapp = arg.lower ()
			print ('Updating', dapp, '...')
			os.system ('cd ' + config.DATA_DIR + '/dapps/' + dapp + ' && git pull')
			os.system ('cd ' + config.DATA_DIR + '/dapps/' + dapp + ' && sudo pip3 install -r requirements.txt && sudo python3 setup.py install')
			print (dapp, 'updated')
			sys.exit (0)


		elif opt in ("-r", "--remove"):
			dapp = arg.lower ()
			print ('Removing', dapp, '...')

			try:
				# shutils.rmtree (
				os.system ('sudo rm -r ' + config.DATA_DIR + '/dapps/' + dapp)
			except:
				print ('Dapp' + dapp + 'doesn\'t exists')

			if dapp in conf['dapps']['list']:
				conf['dapps']['list'].remove (dapp)

			if dapp in conf['dapps']['enabled']:
				conf['dapps']['enabled'].remove (dapp)

			save_conf (config.DATA_DIR + '/' + config.APP_NAME + '.json', conf)
			print ('Dapp', dapp, 'successfully removed')
			print ('State is preserved')
			sys.exit (0)


		elif opt in ("-i", "--install"):
			print ('Installing', arg, '...')
			url = arg

			for dapp in catalog:
				if dapp['name'] == arg:
					url = dapp['source']								

			# Cleaning temp tree
			try:
				shutil.rmtree (config.DATA_DIR + '/dapps/temp/')
			except:
				pass

			# Cloning
			os.system ('git clone ' + url + ' ' + config.DATA_DIR + '/dapps/temp')

			manifest = {}
			try:
				f = open (config.DATA_DIR + '/dapps/temp/manifest.json', 'r')
				manifest = json.loads (f.read ())
				f.close ()
			except:
				print ('No manifest.json or malformed manifest')
				sys.exit ()

			if not 'name' in manifest:
				print ('No dapp name in manifest.json')
				sys.exit ()

			# Move the cloned repository
			# Move the cloned repository
			if os.path.isdir (config.DATA_DIR + '/dapps/' + manifest['name'].lower ()):
				print ('Dapp already installed, reinstalling')
				os.system ('sudo rm -r ' + config.DATA_DIR + '/dapps/' + manifest['name'].lower ())
				#shutil.rmtree (

			os.rename (config.DATA_DIR + '/dapps/temp/', config.DATA_DIR + '/dapps/' + manifest['name'].lower ())

			# Install
			os.system ('cd ' + config.DATA_DIR + '/dapps/' + manifest['name'].lower () + ' && sudo pip3 install -r requirements.txt && sudo python3 setup.py install')

			# Config update
			if not manifest['name'].lower () in conf['dapps']['list']:
				conf['dapps']['list'].append (manifest['name'].lower ())

			if not manifest['name'].lower () in conf['dapps']['enabled']:
				conf['dapps']['enabled'].append (manifest['name'].lower ())

			save_conf (config.DATA_DIR + '/' + config.APP_NAME + '.json', conf)

			print (manifest['name'], 'is now installed')

			sys.exit ()


		elif opt in ("-l", "--list"):
			print ('Installed dapps:')
			for dapp in conf['dapps']['list']:
				print ('\t', dapp)
			print ('Enabled dapps:')
			for dapp in conf['dapps']['enabled']:
				print ('\t', dapp)
			print ('Available:')
			for dapp in catalog:
				print ('\t', dapp['name'], '-', dapp['description'])
			sys.exit ()

	usage ()

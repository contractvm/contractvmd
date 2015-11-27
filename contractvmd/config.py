# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from pycoin import networks
from colorlog import ColoredFormatter
import logging
import os
import platform
import sys

def app_data_path (appauthor, appname, roaming=True):
	if sys.platform.startswith('java'):
		os_name = platform.java_ver()[3][0]
		if os_name.startswith('Windows'):
			system = 'win32'
		elif os_name.startswith('Mac'):
			system = 'darwin'
		else:
			system = 'linux2'
	else:
		system = sys.platform

	if system == "win32":
		if appauthor is None:
			appauthor = appname
		const = roaming and "CSIDL_APPDATA" or "CSIDL_LOCAL_APPDATA"
		path = os.path.normpath(_get_win_folder(const))
		if appname:
			if appauthor is not False:
				path = os.path.join(path, appauthor, appname)
			else:
				path = os.path.join(path, appname)
	elif system == 'darwin':
		path = os.path.expanduser('~/Library/Application Support/')
		if appname:
			path = os.path.join(path, appname)
	else:
		path = os.getenv('XDG_DATA_HOME', os.path.expanduser("~/"))
		if appname:
			path = os.path.join(path, '.'+appname)
	return path


VERBOSE = 5
APP_VERSION = '0.6.8'
APP_NAME = 'contractvm'
APP_AUTHOR = 'Davide Gessa'
DATA_DIR = app_data_path (appauthor=APP_AUTHOR, appname=APP_NAME)
TEMP_DIR_RELATIVE = '/temp/'
TEMP_DIR = DATA_DIR + TEMP_DIR_RELATIVE
DAPPS_DIR_RELATIVE = '/dapps/'
DAPPS_DIR = DATA_DIR + DAPPS_DIR_RELATIVE

BACKEND_PROTOCOLS = ['rpc', 'chainsoapi', 'node']

CHAINS = {
		'XTN' : {
			'code': 'XTN',
			'base_fee': 60000,
			'genesis_block': "000000000077f119d8b40b2858c865a9d5950595297df75d93c5c414743e2928",
			'genesis_height': 607571,
			'name': networks.full_network_name_for_netcode ('XTN')
		},
		'BTC' : {
			'code': 'BTC',
			'base_fee': 40000,
			'genesis_block': "",
			'genesis_height': 329203,
			'name': networks.full_network_name_for_netcode ('BTC')
		},
		'XLT' : {
			'code': 'XLT',
			'base_fee': 450000,
			'genesis_block': "22f9d7316645dc02cdd05c32db902ae4aca582c7f138b2b7cecbc58d269e58a6",
			'genesis_height': 741198,
			'name': networks.full_network_name_for_netcode ('XLT')
		},
		'LTC' : {
			'code': 'LTC',
			'base_fee': 100000,
			'genesis_block': "",
			'genesis_height': 329203,
			'name': networks.full_network_name_for_netcode ('LTC')
		},
		'DOGE': {
			'code': 'DOGE',
			'base_fee': 100000000,
			'genesis_block': "",
			'genesis_height': 481000,
			'name': networks.full_network_name_for_netcode ('DOGE')
		}
	}


#'dapps': [ 'tst', 'hw', 'bs', 'fifo' ],



CONF = {
	'chain': 'XLT',
	'regtest': False,
	'discard-old-blocks': False,
	'maxpeers': 25,
	'dapps': {
		'list': [],
		'enabled': []
	},
	'backend': {
		'protocol': ['rpc', 'chainsoapi', 'node'],
		'rpc': {
			'host': 'localhost', #51.254.215.160',
			'port':'8080',
			'user':'test',
			'password': 'testpass',
			'ssl': False
		}
	},
	'api': {
		'enabled': True,
		'threads': 1,
		'port': 8181
	},
	'dht': {
		'seeds': [],
		'port': 5051
	}
}






formatter = ColoredFormatter(
	'%(log_color)s[%(asctime)-8s] %(module)s: %(message_log_color)s%(message)s',
	datefmt=None,
	reset=True,
	log_colors = {
		'DEBUG':	'blue',
		'PLUGINFO': 'purple',
		'INFO':	 'green',
		'WARNING':  'yellow',
		'ERROR':	'red',
		'CRITICAL': 'red',
	},
	secondary_log_colors={
		'message': {
			'DEBUG':	'purple',
			'PLUGINFO': 'blue',
			'INFO':	 'yellow',
			'WARNING':  'green',
			'ERROR':	'yellow',
			'CRITICAL': 'red',
		}
	},
	style = '%'
)

stream = logging.StreamHandler ()
stream.setFormatter (formatter)

logger = logging.getLogger (APP_NAME)
logger.addHandler (stream)


logging.addLevelName (15, "PLUGINFO")
logging.Logger.pluginfo = lambda self, message, *args, **kws: self._log(15, message, args, **kws) if self.isEnabledFor(15) else None

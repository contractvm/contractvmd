#!/usr/bin/python3

import json
import sys
import os
import getopt
import logging
import signal

from . import config, dht, database, pluginmanager, api
from .chain import chain
from .backend import daemonrpc, chainsoapi


logger = logging.getLogger(config.APP_NAME)


def signal_handler(signal, frame):
        logger.critical ('Exiting...')
        sys.exit (0)

def usage ():
	print ('Usage:',sys.argv[0],'[OPTIONS]\n')
	print ('Mandatory arguments:')
	print ('\t-h,--help\t\t\tdisplay this help')
	print ('\t-V,--version\t\t\tdisplay the software version')
	print ('\t-v,--verbose=n\t\t\tset verbosity level to n=[1-5] (default: '+str(config.VERBOSE)+')')
	print ('\t-D,--data=path\t\t\tspecify a custom data directory path (default: '+config.DATA_DIR+')')
	print ('\t-d,--daemon\t\t\trun the software as daemon')
	print ('\t-c,--chain=chainname\t\tblock-chain', '['+(', '.join (map (lambda x: "'"+x+"'", config.CHAINS)))+']')
	print ('\t-b,--backend=protocol\t\tbackend protocol', str(config.BACKEND_PROTOCOLS))
	print ('\t-p,--port=port\t\tdht port')
	print ('\t-a,--api=bool\t\tdisable or enable api framework')
	print ('\t--api-port=port\t\tset an api port')
	print ('\t-s,--seed=host:port\t\tset a dht seed peer')
	print ('\t--discard-old-blocks\t\tdiscard old blocks')
	print ('\t--malicious\t\treturn wrong result with api.consensus_test')


def main ():
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGQUIT, signal_handler)
	logger.setLevel (60-config.VERBOSE*10)
	logger.info ('Starting %s %s', config.APP_NAME, config.APP_VERSION)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hv:VD:c:b:t:a:sp", ["malicious", "discard-old-blocks", "help", "verbose=", "version", "data=", "daemon", "chain=", "backend=", "api-port=", "api=", "regtest", "seed=", "port="])

	except getopt.GetoptError:
		usage()
		sys.exit(2)

	# Parse arguments
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage ()
			sys.exit ()

		elif opt in ("-V", "--version"):
			print (config.APP_VERSION)
			sys.exit ()

		elif opt in ("-D", "--data"):
			config.DATA_DIR = os.path.expanduser (arg)

		elif opt in ("-v", "--verbose"):
			config.VERBOSE = int (arg)


		elif opt in ("-d", "--daemon"):
			logger.critical ('Daemon is not yet implemented')
			sys.exit ()


	# Set debug level
	logger.setLevel (60-config.VERBOSE*10)


	# Check if the data-dir exists
	if not os.path.isdir (config.DATA_DIR):
		logger.warning ('Directory %s not present', config.DATA_DIR)
		os.mkdir (config.DATA_DIR)
		logger.warning ('Directory %s created', config.DATA_DIR)


	# Check if temp dir exists
	if not os.path.isdir (config.DATA_DIR + config.TEMP_DIR_RELATIVE):
		logger.warning ('Directory %s not present', config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		os.mkdir (config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		logger.warning ('Directory %s created', config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		config.TEMP_DIR = config.DATA_DIR + config.TEMP_DIR_RELATIVE


	# Check if config file exits
	if not os.path.exists(config.DATA_DIR+'/'+config.APP_NAME+'.json'):
		logger.warning ('Configuration file %s not present', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'w')
		f.write (json.dumps (config.CONF, indent=4, separators=(',', ': ')))
		f.close ()
		logger.warning ('Configuration file %s created', config.DATA_DIR+'/'+config.APP_NAME+'.json')


	# Loading config file
	f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'r')
	conf = f.read ()
	f.close ()

	config.CONF = json.loads (conf)
	logger.info ('Configuration file %s loaded', config.DATA_DIR+'/'+config.APP_NAME+'.json')


	# Parse arguments that overrides config file
	for opt, arg in opts:
		if opt in ("-r", "--regtest"):
			config.CONF['regtest'] = True
			config.CHAINS[config.CONF['chain']]['genesis_height'] = 0
		elif opt in ("-c", "--chain"):
			config.CONF['chain'] = arg
		elif opt in ("-b", "--backend"):
			config.CONF['backend']['protocol'] = [arg]
		elif opt in ("-a", "--api"):
			config.CONF['api']['enabled'] = bool (int (arg))
		elif opt in ("-s", "--seed"):
			config.CONF['dht']['seeds'] = [arg]
		elif opt in ("-p", "--port"):
			config.CONF['dht']['port'] = int (arg)
		elif opt in ("--api-port"):
			config.CONF['api']['port'] = int (arg)
		elif opt in ("--discard-old-blocks"):
			config.CONF['discard-old-blocks'] = True
		elif opt in ("--malicious"):
			config.CONF['malicious'] = True
			logger.debug ('Running in malicious mode')

	# Check for chain
	if not config.CONF['chain'] in config.CHAINS:
		logger.critical ('Unable to start %s on chain \'%s\'', config.APP_NAME, config.CONF['chain'])
		sys.exit (0)


	# Start the backend
	be = None
	fallbackends = config.CONF['backend']['protocol']

	while be == None and len (fallbackends) > 0:
		cbe = fallbackends [0]
		fallbackends = fallbackends[1:]

		if cbe == 'rpc':
			be = daemonrpc.DaemonRPC (config.CONF['chain'], config.CONF['backend']['rpc']['host'], config.CONF['backend']['rpc']['port'],
						config.CONF['backend']['rpc']['user'], config.CONF['backend']['rpc']['password'],
						bool(config.CONF['backend']['rpc']['ssl']))

			if be.connect ():
				logger.info ('Backend protocol %s initialized', cbe)
			else:
				logger.critical ('Unable to connect to the rpc host, falling back')
				be = None

		elif cbe == 'chainsoapi':
			if chainsoapi.ChainSoAPI.isChainSupported(config.CONF['chain']):
				be = chainsoapi.ChainSoAPI (config.CONF['chain'])
			else:
				logger.critical ('Backend protocol %s is only available with %s networks, falling back',
					config.CONF['backend']['protocol'], str (chainsoapi.ChainSoAPI.getSupportedChains ()))
				be = None
		else:
			logger.critical ('Unable to handle the backend protocol %s, falling back', cbe)
			be = None

	if be == None:
		logger.critical ('Cannot find a good backend protocol, exiting')
		sys.exit (0)


	# Start the DHT
	ddht = dht.DHT (int (config.CONF['dht']['port']), config.CONF['dht']['seeds'], config.DATA_DIR+'/dht_'+config.CONF['chain']+'.dat', {'api_port': config.CONF['api']['port']})
	ddht.run ()
	#logger.info ('DHT initialized')
	#print ('DHT',ddht.identity ())


	# Load the state db
	db = database.Database (config.DATA_DIR+'/db_'+config.CONF['chain']+ ('_regtest' if config.CONF['regtest'] else '') + '.dat')
	logger.info ('Database %s initialized', 'db_'+config.CONF['chain']+ ('_regtest' if config.CONF['regtest'] else '') + '.dat')



	# Load the plugin engine
	pm = pluginmanager.PluginManager ()

	# Create the chain engine
	ch = chain.Chain (pm, db, be, ddht, config.CHAINS[config.CONF['chain']])


	# API
	if bool (int (config.CONF['api']['enabled'])):
		aapi = api.API (be, ch, ddht, config.CONF['api']['port'], config.CONF['api']['threads'])
		aapi.run ()
	else:
		aapi = None

	# Load all plugins
	for p in config.CONF['plugins']:
		pm.load (p, ch, db, ddht, aapi)


	# Run the mainloop
	logger.info ('Chain initialized, starting the main loop')
	ch.run ()


if __name__ == "__main__":
	main ()

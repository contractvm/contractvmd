#!/usr/bin/python3
# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
import time
import json
import sys
import os
import getopt
import logging
import signal

from . import config, dht, database, pluginmanager, api
from .chain import chain
from .backend import daemonrpc, chainsoapi, node


logger = logging.getLogger(config.APP_NAME)


def signal_handler (sig, frame):
	logger.critical ('Exiting...')
	f = open (config.DATA_DIR + '/pid', 'r')
	cpid = f.read ()
	f.close ()
	os.kill (int (cpid), signal.SIGKILL)
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
	print ('\t-p,--port=port\t\t\tdht port')
	print ('\t-a,--api=bool\t\t\tdisable or enable api framework')
	print ('\t--api-port=port\t\t\tset an api port')
	print ('\t-s,--seed=host:port,[host:port]\tset a contractvm seed nodes list')
	print ('\t--discard-old-blocks\t\tdiscard old blocks')

	print ('\nDaemon commands:')
	print ('\t--restart\t\t\trestart the contractvmd instance')
	print ('\t--stop\t\t\t\tstop the contractvmd instance')



def core (opts, args):
	firstrun = False

	logger.info ('Starting %s %s', config.APP_NAME, config.APP_VERSION)

	# Set debug level
	logger.setLevel (60-config.VERBOSE*10)


	# Check if the data-dir exists
	if not os.path.isdir (config.DATA_DIR):
		logger.warning ('Directory %s not present', config.DATA_DIR)
		os.mkdir (config.DATA_DIR)
		logger.warning ('Directory %s created', config.DATA_DIR)
		firstrun = True

	# Check if temp dir exists
	if not os.path.isdir (config.DATA_DIR + config.TEMP_DIR_RELATIVE):
		logger.warning ('Directory %s not present', config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		os.mkdir (config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		logger.warning ('Directory %s created', config.DATA_DIR + config.TEMP_DIR_RELATIVE)
		config.TEMP_DIR = config.DATA_DIR + config.TEMP_DIR_RELATIVE

	# Check if dapps dir exists
	if not os.path.isdir (config.DATA_DIR + config.DAPPS_DIR_RELATIVE):
		logger.warning ('Directory %s not present', config.DATA_DIR + config.DAPPS_DIR_RELATIVE)
		os.mkdir (config.DATA_DIR + config.DAPPS_DIR_RELATIVE)
		logger.warning ('Directory %s created', config.DATA_DIR + config.DAPPS_DIR_RELATIVE)
		config.DAPPS_DIR = config.DATA_DIR + config.DAPPS_DIR_RELATIVE

	# Check if config file exits
	if not os.path.exists(config.DATA_DIR+'/'+config.APP_NAME+'.json'):
		logger.warning ('Configuration file %s not present', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		f = open (config.DATA_DIR+'/'+config.APP_NAME+'.json', 'w')
		f.write (json.dumps (config.CONF, indent=4, separators=(',', ': ')))
		f.close ()
		logger.warning ('Configuration file %s created', config.DATA_DIR+'/'+config.APP_NAME+'.json')
		firstrun = True

	try:
		os.mkdirs (config.DATA_DIR + '/dapps/')
	except:
		pass

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
			config.CONF['dht']['seeds'] = arg.split (',')
		elif opt in ("-p", "--port"):
			config.CONF['dht']['port'] = int (arg)
		elif opt in ("--api-port"):
			config.CONF['api']['port'] = int (arg)
		elif opt in ("--discard-old-blocks"):
			config.CONF['discard-old-blocks'] = True


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
		#print (fallbackends)

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

		elif cbe == 'node':
			c = config.CHAINS[config.CONF['chain']]
			be = node.Node (config.CONF['chain'], config.DATA_DIR+'/node_'+config.CONF['chain']+'.dat', (c['genesis_block'], c['genesis_height']))
			if be.connect ():
				logger.info ('Backend protocol %s initialized', cbe)
			else:
				logger.critical ('Unable to enstablish a bitpeer daemon, falling back')
				be = None

		else:
			logger.critical ('Unable to handle the backend protocol %s, falling back', cbe)
			be = None


	if be == None:
		logger.critical ('Cannot find a good backend protocol, exiting')
		sys.exit (0)


	# Start the DHT
	try:
		ddht = dht.DHT (int (config.CONF['dht']['port']), seedlist=config.CONF['dht']['seeds'], dhtfile=config.DATA_DIR+'/dht_'+config.CONF['chain']+'.dat', info=config.CONF['api']['port'])
		ddht.run ()
		logger.info ('DHT initialized with identity: ' + str (ddht.identity ()))
	except Exception as e:
		logger.critical ('Exception while initializing kademlia DHT')
		logger.critical (e)
		sys.exit (0)


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


	# Load all dapps
	for dapp in config.CONF['dapps']['enabled']:
		try:
			pm.load (dapp, ch, db, ddht, aapi)
		except Exception as e:
			logger.critical ('Exception while loading dapp: ' + dapp)
			logger.critical (e)

	# Run the mainloop
	logger.info ('Chain initialized, starting the main loop')
	ch.run ()



def main ():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hv:VD:c:b:t:a:sp", ["stop", "restart", "discard-old-blocks", "help", "verbose=", "version", "data=", "daemon", "chain=", "backend=", "api-port=", "api=", "regtest", "seed=", "port="])

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

		elif opt in ("--restart"):
			print ('Restarting daemon...')

			f = open (config.DATA_DIR + '/pid', 'r')
			cpid = f.read ()
			f.close ()
			try:
				os.kill (int (cpid), signal.SIGUSR1)
			except:
				print ('No running instance.')
			sys.exit (0)

		elif opt in ("--stop"):
			print ('Stopping daemon...')

			f = open (config.DATA_DIR + '/pid', 'r')
			cpid = f.read ()
			f.close ()
			try:
				os.kill (int (cpid), signal.SIGKILL)
			except:
				print ('No running instance.')
			sys.exit (0)

	# Check if the data-dir exists
	if not os.path.isdir (config.DATA_DIR):
		logger.warning ('Directory %s not present', config.DATA_DIR)
		os.mkdir (config.DATA_DIR)
		logger.warning ('Directory %s created', config.DATA_DIR)


	try:
		f = open (config.DATA_DIR + '/pid', 'r')
		cpid = f.read ()
		f.close ()

		os.kill (int (cpid), signal.SIGKILL)
		logger.critical ('Already running, killed: ' + str (cpid))
	except:
		pass

	#logger.addHandler (logging.FileHandler (config.DATA_DIR + '/contractvmd.log'))
	#logger.info ('Logging to', config.DATA_DIR + '/contractvmd.log')


	run = True
	while run:
		pid = os.fork ()

		if pid != 0:
			signal.signal(signal.SIGINT, signal_handler)
			signal.signal(signal.SIGQUIT, signal_handler)

			logger.critical ('Started: ' + str (pid))

			f = open (config.DATA_DIR + '/pid', 'w')
			f.write (str(pid))
			f.close ()

			r = os.waitpid (int (pid), 0)
			logger.critical ('Stopped: ' + str (r[0]))
			time.sleep (5)

			if r[1] == signal.SIGKILL:
				run = False
		else:
			core (opts, args)
			sys.exit (0)

if __name__ == "__main__":
	main ()

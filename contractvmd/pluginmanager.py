import logging
from colorlog import ColoredFormatter

from . import config

logger = logging.getLogger(config.APP_NAME)



class PluginManager:
	def __init__ (self):
		self.plugins = {}

	def load (self, pname, chain, db, dht, api):
		classname = config.PLUGINS[pname.upper ()]

		logger.pluginfo ('Plugging module "%s"', pname.upper ())
		exec ('from .' + pname.lower() + '.' + pname.lower() + 'plugin import ' + classname + 'Plugin')
		pc = eval (classname+'Plugin')

		po = pc (chain, db.newNamespaceInstance (pname.upper () + '_'), dht, api)

		rpcm = po.getAPI ().getRPCMethods ()
		for m in rpcm:
			api.registerRPCMethod (pname.lower () + '.' + m, rpcm[m])

		self.plugins[po.Name] = po



	# Handle message received from the DHT
	def handleMessage (self, m):
		for p in self.plugins:
			if m.PluginCode == self.plugins[p].PluginCode:
				logger.pluginfo ('Found handler %s for message %s from %s', p, m.Hash, m.Player)
				return self.plugins[p].handleMessage (m)
		logger.error ('Cannot handle message method %d for plugin %d', m.Method, m.PluginCode)
		return None

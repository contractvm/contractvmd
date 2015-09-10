from .proto import Protocol

class Plugin:
	def __init__ (self, name, plugin_code, methods, chain, database, dht):
		self.Name = name
		self.PluginCode = plugin_code
		self.Methods = methods
		self.Database = database
		self.Chain = chain
		self.DHT = dht

	def getAPI (self):
		return None

	def handleMessage (self, message):
		return None


class API:
	def __init__ (self, vm, dht, rpcmethods, errors):
		self.vm = vm
		self.dht = dht
		self.errors = errors
		self.rpcmethods = rpcmethods

	def getRPCMethods (self):
		return self.rpcmethods

	def createErrorResponse (self, error):
		if error in self.errors:
			return { 'error': self.errors[error]['code'], 'message': self.errors[error]['message'] }
		else:
			return { 'error': -1, 'message': 'General error ('+str(error)+')' }


class VM:
	def __init__ (self, chain, database):
		self.chain = chain
		self.database = database

	
	# Get the current time, or time of an arbitrary block-height
	def getTime (self, height=None):
		if height != None:
			return int (int (height) / Protocol.TIME_UNIT_BLOCKS)
		return int (int (self.chain.getChainHeight ()) / Protocol.TIME_UNIT_BLOCKS)

	def getChainName (self):
		return self.chain.getChainName ()

	def getChainCode (self):
		return self.chain.getChainCode ()

	def getChainHeight (self):
		return int (self.chain.getChainHeight ())

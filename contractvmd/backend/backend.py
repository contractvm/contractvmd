class WrongChainException (Exception):
	pass

class Backend:
	def __init__ (self):
		raise ('This is an abstract method')		

	def connect (self):
		raise ('This is an abstract method')

	def getLastBlockHeight (self):
		raise ('This is an abstract method')

	def getBlockHash (self, index):
		raise ('This is an abstract method')

	# Return a dict {"height": x, "hash": y, "time": unixtime, "tx": [listoftxids]}
	def getBlockByHash (self, bhash):
		raise ('This is an abstract method')

	def getTransaction (self, txid):
		raise ('This is an abstract method')

	def broadcastTransaction (self, transaction):
		raise ('This is an abstract method')

	def getBlock (self, index):
        	return self.getBlockByHash (self.getBlockHash (index))


		

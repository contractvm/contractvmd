# Protocol metadata and definitions
from . import config

class Protocol:
	# Protocol related
	VERSION = 1
	MAGIC_FLAG = 'CCHN'

	# Transaction limits
	STORAGE_OPRETURN_LIMIT = 40
	DATA_HASH_SIZE = 64

	# Time related
	TIME_UNIT_BLOCKS = 1

	def timeUnit (chain):
		return TIME_UNIT_BLOCKS

	# Fee estimation
	def estimateFee (chain, weight):
		return config.CHAINS[chain]['base_fee'] + weight * 4 + 2


	def estimateExpiryFromFee (chain, fee, weight):
		fee = int (fee) - config.CHAINS[chain]['base_fee'] - 2
		return int (fee / weight)
		

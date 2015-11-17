# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import requests
import json
import logging
import time

from .backend import *
from .. import config

logger = logging.getLogger(config.APP_NAME)


class LibBitcoin (Backend):
	def __init__ (self, chain):
		self.chain = chain

	def getChainCode (self):
	    return 'UNK'

	def connect (self):
	    return None
	
	def getLastBlockHeight (self):
	    return None

	def getBlockHash (self, index):
	    return None

	def getBlockByHash (self, bhash):
	    return None

	def broadcastTransaction (self, transaction):
	    return None

	def getTransaction (self, txid):
	    return None


# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import time

from .. import config

class BlockWatch:
	def __init__ (self, current, backend, notifyHandler):
		self.current_height = current
		self.backend = backend
		self.notify = notifyHandler

	def run (self):
		while True:
			h = self.backend.getLastBlockHeight ()
	
			if (h != self.current_height):
				for i in range (self.current_height+1, h+1):
					self.notify (i)
					self.current_height = i
					time.sleep (0.1)
			time.sleep (5)

	

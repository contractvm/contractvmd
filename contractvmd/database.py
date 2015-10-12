# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys
import logging
import copy
import shelve
#import leveldb
from threading import Lock

from . import config
from .chain.message import Message

logger = logging.getLogger(config.APP_NAME)

# Database abstraction layer
class Database:
	def __init__ (self, f):
		self.shelve = shelve.open (f)

	def close (self):
		self.shelve.close ()

	def sync (self):
		self.shelve.sync ()

	def new (path):
		return Database (path)


	# Raw operations
	def _exists (self, key):
		return (key in self.shelve)
		#try:
		#	self.db.Get(key)
		#	return True
		#except:
		#	return False


	def _delete (self, key):
		del (self.shelve[key])
		#self.db.Delete(key)

	def _get (self, key):
		if key in self.shelve:
			return self.shelve [key]
		else:
			return None
		#try:
		#	return self.db.Get(key)
		#except:
		#	return None

	def _set (self, key, dictobj):
		self.shelve [key] = dictobj
		#self.db.Put(key, dictobj)


	# General operations
	def exists (self, key):
		return self._exists (key)

	def get (self, key):
		return self._get (key)

	def set (self, key, dictobj):
		self._set (key, dictobj)
		self.sync ()

	def delete (self, key):
		if self.exists (key):
			self._delete (key)
			self.sync ()


	# Integer object operations
	def intinc (self, key):
		self.set (key, int (self.get (key)) + 1)

	def intdec (self, key):
		self.set (key, int (self.get (key)) + 1)


	# List

	# List object operations
	def listappend (self, key, data):
		d = self.get (key)
		#print (d)
		d.append (data)
		#print (d)
		self.set (key, d)

	def listremove (self, key, data):
		li = self.get (key)
		li.remove (data)
		self.set (key, li)

	def listcontains (self, key, data):
		return (data in self.get (key))


	# Get the object at 'key', or set 'key' to 'dictobj'
	def getinit (self, key, dictobj):
		if not self.exists (key):
			self.set (key, dictobj)
			return dictobj
		else:
			return self.get (key)


	def init (self, key, dictobj):
		if not self.exists (key):
			self.set (key, dictobj)

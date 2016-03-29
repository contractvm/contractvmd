"""
Module structure

dappc/
dappc/__init___.py
dappc/dappc.py 				- Starter file (contains the main)

dappc/library/				- Library compiler for various languages
dappc/library/py.py
dappc/library/js.py
dappc/library/ml.py
dappc/library/common.py		- Common utilities for library compiler

dappc/core/py.py			- Dappc compiler for python language (with meta)
dappc/core/ml.py			- Dappc compiler for ocaml language (with meta)
dappc/core/js.py			- Dappc compiler for nodejs language (with meta)
dappc/core/common.py		- Common interface for dappc

"""

import sys
import os
import inspect
import imp

from .chain.message import Message
from .proto import Protocol
from . import config, dapp, database


class DappCompiler ():
	def __init__ (self, source, destination):
		self.dappsrc = imp.load_source ('dappsrc', source)
		self.NAME = self.dappsrc.NAME.title ().replace (' ', '')

		self.wrapper = []
		self.init = []
		self.library = []

		self.sample = []
		self.manifest = []
		self.requirements = []
		self.setup = []

		self.source = source
		self.destination = destination

	def compileSample (self):
		base = [
			'#!/usr/bin/python3\n',
			'from libcontractvm import Wallet, WalletExplorer, ConsensusManager\n',
			'from ' + self.NAME.lower () + ' import ' + self.NAME + 'Dapp\n',
			'import sys\n\n',
			'consMan = ConsensusManager.ConsensusManager ()\n',
			'consMan.bootstrap ("http://127.0.0.1:8181")\n\n',
			"wallet = WalletExplorer.WalletExplorer (wallet_file='test.wallet')\n",
			'dapp = ' + self.NAME + 'Dapp.' + self.NAME + 'Dapp (consMan, wallet=wallet)\n',
		]
		return base

	def compileMeta (self):
		manifest = [ 
			"{\n",
			'\t"name": "' + self.NAME.lower () + '",\n',
			'\t"version": "' + str (self.dappsrc.VERSION) + '",\n',
			'\t"authors": ["' + ', '.join (self.dappsrc.AUTHORS) + '"],\n',
			'\t"description": "' + self.dappsrc.DESCRIPTION + '"\n}\n'
		]

		requirements = []

		try:
			for x in self.dappsrc.REQUIRE:
				requirements.append (x + '\n')
		except:
			pass

		setup = [
			'#!/usr/bin/python3\n',
			'from setuptools import find_packages\n',
			'from setuptools import setup\n\n',
			'setup(name="' + self.NAME.lower () + '",\n',
			'\tversion="' + str (self.dappsrc.VERSION) + '",\n',
			'\tdescription="' + self.dappsrc.DESCRIPTION + ' - client library",\n',
			'\tauthor="' + ', '.join (self.dappsrc.AUTHORS) + '",\n',
			'\tsetup_requires="setuptools",\n',
			'\tpackage_dir={"":"library"},\n',
			'\tpackages=["' + self.NAME.lower () + '"]\n',
			')\n'
		]
		return (manifest, setup, requirements)


	def compileLibrary (self):
		base = [
			'from libcontractvm import Wallet, ConsensusManager, DappManager\n\n',
			'class ' + self.NAME + 'Dapp (DappManager.DappManager):\n',
			'\tdef __init__ (self, consensusManager, wallet = None):\n',
			'\t\tsuper (' + self.NAME + 'Dapp, self).__init__(consensusManager, wallet)\n\n'
		]


		#	'\tdef getNames (self):\n',
		#	"\t\treturn self.consensusManager.jsonConsensusCall ('helloworld.get_names', [])['result']\n\n"
		#]
		# Methods
		for update in self.dappsrc.UPDATE:
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef ' + update + ' (' + ', '.join (('self',) + args) + '):\n',
				"\t\treturn self.produceTransaction ('" + self.NAME.lower () + "." + update + "', ["+ ', '.join (args) + "])\n\n"
			]

			if ('validate' in self.dappsrc.UPDATE[update]):
				args = self.dappsrc.UPDATE[update]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + update + 'Validate (' + ', '.join (('self',) + args) + '):\n',
					"\t\treturn self.consensusManager.jsonConsensusCall ('" + self.NAME.lower () + "." + update + "Validate', ["+ ', '.join (args) + "])\n\n"
				]


			if ('pre' in self.dappsrc.UPDATE[update]):
				args = self.dappsrc.UPDATE[update]['pre'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + update + 'Pre (' + ', '.join (('self',) + args) + '):\n',
					"\t\treturn self.consensusManager.jsonConsensusCall ('" + self.NAME.lower () + "." + update + "Pre', ["+ ', '.join (args) + "])\n\n"
				]

		for query in self.dappsrc.QUERIES:
			args = self.dappsrc.QUERIES[query]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef ' + query + ' (' + ', '.join (('self',) + args) + '):\n',
				"\t\treturn self.consensusManager.jsonConsensusCall ('" + self.NAME.lower () + "." + query + "', ["+ ', '.join (args) + "])\n\n"
			]

			if ('validate' in self.dappsrc.QUERIES[query]):
				args = self.dappsrc.QUERIES[query]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + query + 'Validate (' + ', '.join (('self',) + args) + '):\n',
					"\t\treturn self.consensusManager.jsonConsensusCall ('" + self.NAME.lower () + "." + query + "Validate', ["+ ', '.join (args) + "])\n\n"
				]

		return base


	def compileProtocol (self):
		methods = []

		base = [
			'class ' + self.NAME + 'Protocol:\n',
			'\tDAPP_CODE = [ 0x01, 0x06 ]\n'
		]

		for update in self.dappsrc.UPDATE:
			base.append ('\tMETHOD_' + update.upper () + ' = ' + str (self.dappsrc.UPDATE[update]['method']) + '\n')
			methods.append ('METHOD_' + update.upper ())

		base.append ('\tMETHOD_LIST = [ ' + ', '.join (methods) + ' ]\n')
		return base


	def compileMessage (self):
		base = [
			'class ' + self.NAME + 'Message (Message):\n'
		]

		for update in self.dappsrc.UPDATE:
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]

			base += [
				'\tdef ' + update + ' ( ' + ', '.join (args) + ' ):\n',
				'\t\tm = ' + self.NAME + 'Message ()\n'
			]

			for arg in args:
				base.append ('\t\tm.' + arg + ' = ' + arg + '\n')

			base += [
				'\t\tm.DappCode = ' + self.NAME + 'Protocol.DAPP_CODE\n',
				'\t\tm.Method = ' + self.NAME + 'Protocol.METHOD_' + update.upper () + '\n',
				'\t\treturn m\n',
				'\n'
			]

		base += [
			'\tdef toJSON (self):\n',
			'\t\tdata = super ('+self.NAME+'Message, self).toJSON ()\n',
			'\n'
		]

		for update in self.dappsrc.UPDATE:
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]

			base.append ('\t\tif self.Method == '+self.NAME+'Proto.METHOD_' + update.upper () + ':\n')

			for arg in args:
				base.append ("\t\t\tdata['" + arg +"'] = self." + arg +"\n")

			base += [
				'\t\t\treturn data\n',
				'\n'
			]

		base += [ '\t\treturn None\n' ]
		return base


	def compileAPI (self):
		base = [
			'class '+self.NAME+'API (dapp.API):\n',
			'\tdef __init__ (self, core, dht, api):\n',
			'\t\tself.api = api\n',
			'\t\tself.core = core\n',
			'\t\trpcmethods = {}\n',
			'\n'
		]

		for update in self.dappsrc.UPDATE:
			base += [ '\t\trpcmethods["'+update+'"] = { "call": self.method_'+update+' }\n' ]

			if ('validate' in self.dappsrc.UPDATE[update]):
				base += [ '\t\trpcmethods["'+update+'Validate"] = { "call": self.method_'+update+'Validate }\n' ]

			if ('pre' in self.dappsrc.UPDATE[update]):
				base += [ '\t\trpcmethods["'+update+'Pre"] = { "call": self.method_'+update+'Pre }\n' ]


		for query in self.dappsrc.QUERIES:
			base += [ '\t\trpcmethods["'+query+'"] = { "call": self.method_'+query+' }\n' ]

			if ('validate' in self.dappsrc.QUERIES[query]):
				base += [ '\t\trpcmethods["'+query+'Validate"] = { "call": self.method_'+query+'Validate }\n' ]

		base += [ '\n\t\tsuper ('+self.NAME+'API, self).__init__(core, dht, rpcmethods, {})\n\n' ]


		# Methods
		for update in self.dappsrc.UPDATE:
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef method_' + update + ' (' + ', '.join (('self',) + args) + '):\n',
				'\t\tmessage = ' + self.NAME + 'Message.' + update + ' ('+ ', '.join (args) + ')\n',
				'\t\treturn self.createTransactionResponse (message)\n\n'
			]

			if ('validate' in self.dappsrc.UPDATE[update]):
				args = self.dappsrc.UPDATE[update]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef method_' + update + 'Validate (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.core.' + self.dappsrc.UPDATE[update]['validate'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]


			if ('pre' in self.dappsrc.UPDATE[update]):
				args = self.dappsrc.UPDATE[update]['pre'].__code__.co_varnames[1:]
				base += [
					'\tdef method_' + update + 'Pre (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.core.' + self.dappsrc.UPDATE[update]['pre'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]


		for query in self.dappsrc.QUERIES:
			args = self.dappsrc.QUERIES[query]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef method_' + query + ' (' + ', '.join (('self',) + args) + '):\n',
				'\t\treturn (self.core.' + query + '(' + ', '.join (args) + '))\n',
				'\n'
			]

			if ('validate' in self.dappsrc.QUERIES[query]):
				args = self.dappsrc.QUERIES[query]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef method_' + query + 'Validate (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.core.' + self.dappsrc.QUERIES[query]['validate'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]

		return base


	def compileMain (self):
		base = [
			'class ' + self.NAME.lower () + ' (dapp.Dapp):\n',
			'\tdef __init__ (self, chain, db, dht, apimaster):\n',
			'\t\tself.core = ' + self.NAME + 'CoreWrapper (chain, db)\n',
			'\t\tapi = ' + self.NAME + 'API (self.core, dht, apimaster)\n',
			'\t\tsuper (' + self.NAME.lower () + ', self).__init__(' + self.NAME + 'Protocol.DAPP_CODE, ' + self.NAME + 'Protocol.METHOD_LIST, chain, db, dht, api)\n',
			'\n',
			'\tdef handleMessage (self, m):\n'
		]

		for update in self.dappsrc.UPDATE:
			bb = []
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]
			for arg in args:
				bb += ['m.Data ["' + arg + '"]']

			base += [
				'\t\tif m.Method == ' + self.NAME + 'Protocol.METHOD_' + update.upper () + ':\n',
				"\t\t\tlogger.pluginfo ('Found new message %s: %s', m.Hash, '" + update + "')\n",
				"\t\t\tself.core." + update + " (" + ', '.join (bb) + ")\n\n"
			]		    

		return base


	def compileCoreWrapper (self):
		base = [
			'class ' + self.NAME + 'CoreWrapper (dapp.Core):\n',
			'\tdef __init__ (self, chain, database):\n',
			'\t\tsuper (' + self.NAME + 'CoreWrapper, self).__init__ (chain, database)\n\n',
			'\tdef compileCore (self, message):\n',
			'\t\tc = core.' + self.NAME + 'Core()\n',
			'\t\tc.state = database.State (self.database)\n',
			'\t\tc.message = message\n'
		]

		for x in self.dappsrc.INIT:
			base.append ('\t\tc.' + self.dappsrc.INIT[x]['function'].__name__ + ' ()\n')
		base.append ('\t\treturn c\n\n')


		for query in self.dappsrc.QUERIES:
			args = self.dappsrc.QUERIES[query]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef ' + query + ' (' + ', '.join (('self',) + args) + '):\n',
				'\t\treturn (self.createCore (None).' + query + '(' + ', '.join (args) + '))\n',
				'\n'
			]

			if 'validate' in self.dappsrc.QUERIES [query]:
				args = self.dappsrc.QUERIES[query]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + self.dappsrc.QUERIES[query]['validate'].__name__ + ' (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.createCore (None).' + self.dappsrc.QUERIES[query]['validate'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]

		for update in self.dappsrc.UPDATE:
			args = self.dappsrc.UPDATE[update]['function'].__code__.co_varnames[1:]
			base += [
				'\tdef ' + update + ' (' + ', '.join (('self',) + args) + '):\n',
				'\t\treturn (self.createCore (None).' + update + '(' + ', '.join (args) + '))\n',
				'\n'
			]

			if 'validate' in self.dappsrc.UPDATE [update]:
				args = self.dappsrc.UPDATE [update]['validate'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + self.dappsrc.UPDATE [update]['validate'].__name__ + ' (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.createCore (None).' + self.dappsrc.UPDATE [update]['validate'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]

			if 'pre' in self.dappsrc.UPDATE [update]:
				args = self.dappsrc.UPDATE [update]['pre'].__code__.co_varnames[1:]
				base += [
					'\tdef ' + self.dappsrc.UPDATE [update]['pre'].__name__ + ' (' + ', '.join (('self',) + args) + '):\n',
					'\t\treturn (self.createCore (None).' + self.dappsrc.UPDATE [update]['pre'].__name__ + '(' + ', '.join (args) + '))\n',
					'\n'
				]

		return base


	def compile (self):
		# Create the source of the dapp
		protocol = self.compileProtocol ()
		message = self.compileMessage ()
		corewrap = self.compileCoreWrapper ()
		api = self.compileAPI ()
		main = self.compileMain ()
		
		(self.manifest, self.setup, self.requirements) = self.compileMeta ()
		self.sample = self.compileSample ()

		header = [
			'import logging\n\n',
			'from contractvmd import config, dapp, database\n',
			'from contractvmd.proto import Protocol\n',
			'from contractvmd.chain.message import Message\n',
			'from . import core\n\n',
			'logger = logging.getLogger(config.APP_NAME)\n\n'
		]

		self.wrapper = header + ['\n\n'] + protocol + ['\n\n'] + message + ['\n\n'] + corewrap + ['\n\n'] + api + ['\n\n'] + main

		self.init = [
			'from . import core\n',
			'from . import ' + self.NAME.lower ()
		]

		self.library = self.compileLibrary ()


	def save (self):
		basedir = self.destination + '/'

		try:
			os.mkdir (basedir)
		except: pass

		try:
			os.mkdir (basedir + 'dapp')
		except: pass

		try:
			os.mkdir (basedir + 'library')
		except: pass

		try:
			os.mkdir (basedir + 'library/' + self.NAME.lower ())
		except: pass

		try:
			os.mkdir (basedir + 'samples')
		except: pass

		# DAPP wrapper
		with open (basedir + 'dapp/' + self.NAME.lower () + '.py', 'w') as f:
			print ('Writing', self.NAME.lower () + '.py')
			f.write ('# Autogenerated file by dappc\n')
			for x in self.wrapper:
				f.write (x)


		# library
		with open (basedir + 'library/' + self.NAME.lower () + '/' + self.NAME + 'Dapp.py', 'w') as f:
			print ('Writing', 'library/' + self.NAME + 'Dapp.py')

			f.write ('# Autogenerated file by dappc\n')
			for x in self.library:
				f.write (x)

		with open (basedir + 'library/' + self.NAME.lower () + '/__init__.py', 'w') as f:
			print ('Writing', 'library/__init__.py')

			f.write ('# Autogenerated file by dappc\n')

		with open (basedir + 'samples/sample.py', 'w') as f:
			print ('Writing', 'samples/sample.py')

			f.write ('# Autogenerated file by dappc\n')
			for x in self.sample:
				f.write (x)


		# Init
		with open (basedir + 'dapp/__init__.py', 'w') as f:
			print ('Writing', '__init__.py')

			f.write ('# Autogenerated file by dappc\n')
			for x in self.init:
				f.write (x)

		# Core
		with open (basedir + 'dapp/core.py', 'w') as f:
			print ('Writing', 'core.py')

			f.write ('# Autogenerated file by dappc\n')
			source = inspect.getsourcelines (self.dappsrc)[0]

			for y in source:
				for x in self.dappsrc.DAPP:
					if y.find ('class '+self.dappsrc.DAPP[x].__name__) != -1:
						y = 'class ' + self.NAME + 'Core ():\n'

				f.write (y)



		# Source
		with open (basedir + self.NAME.lower() + '.dapp.py', 'w') as f:
			print ('Writing', self.NAME.lower () + '.dapp.py')

			source = inspect.getsourcelines (self.dappsrc)[0]

			for y in source:
				f.write (y)


		# Requirements
		with open (basedir + 'requirements.txt', 'w') as f:
			print ('Writing', 'requirements.txt')

			for x in self.requirements:
				f.write (x)

		# Setup
		with open (basedir + 'setup.py', 'w') as f:
			print ('Writing', 'setup.py')

			for x in self.setup:
				f.write (x)

		# Manifest
		with open (basedir + 'manifest.json', 'w') as f:
			print ('Writing', 'manifest.json')

			for x in self.manifest:
				f.write (x)

		print ('Done.')




def usage ():
	print ('Usage:', sys.argv[0], 'source destination')


def main ():
	if len (sys.argv) < 2:		
		usage ()

	if len (sys.argv) > 2:
		dc = DappCompiler (sys.argv[1], sys.argv[2])
	else:
		dc = DappCompiler (sys.argv[1], 'build')
		
	dc.compile ()
	dc.save ()




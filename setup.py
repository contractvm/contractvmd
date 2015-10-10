# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from setuptools import find_packages
from setuptools import setup

setup(name='contractvm',
	version='0.1',
	description='ContractVM daemon',
	author='Davide Gessa',
	setup_requires='setuptools',
	author_email='gessadavide@gmail.com',
	packages=['contractvmd', 'contractvmd.backend', 'contractvmd.chain'],
	entry_points={
		'console_scripts': [
			'contractvmd=contractvmd.contractvmd:main',
			'dappman=contractvmd.dappman:main',
		],
	},
)

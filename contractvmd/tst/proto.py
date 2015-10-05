# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

class TSTProto:
	DAPP_CODE = 0x01

	METHOD_TELL = 0x00
	METHOD_FUSE = 0x01
	METHOD_FUSE_NET = 0x02
	METHOD_DO = 0x03
	METHOD_ACCEPT = 0x04

	METHOD_LIST = [METHOD_TELL, METHOD_FUSE, METHOD_FUSE_NET, METHOD_DO, METHOD_ACCEPT]    

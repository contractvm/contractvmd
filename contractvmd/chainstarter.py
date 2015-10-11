import os
import sys

ARGS = '-server -rpcuser=test -rpcpassword=testpass -rpcport=18332 -txindex -debug -printtoconsole'

def main ():
	if len (sys.argv) == 1:
		os.system ('bitcoin-qt -testnet '+ARGS)
	elif len (sys.argv) == 2:
		if sys.argv[1] == 'XLT':
			os.system ('litecoin-qt -testnet '+ARGS)
		elif sys.argv[1] == 'XTN':
			os.system ('bitcoin-qt -testnet '+ARGS)
		elif sys.argv[1] == 'XDT':
			os.system ('dogecoin-qt -testtest '+ARGS)
		elif sys.argv[1] == 'RXLT':
			os.system ('litecoin-qt -regtest '+ARGS)
		elif sys.argv[1] == 'RXTN':
			os.system ('bitcoin-qt -regtest '+ARGS)
		elif sys.argv[1] == 'RXDT':
			os.system ('dogecoin-qt -regtest '+ARGS)
		else:
			print ("unrecognized chain name", sys.argv[1])
	else:
		print ('usage: python start_chain.py chaincode')

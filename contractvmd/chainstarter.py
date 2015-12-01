import os
import sys

def main ():
	ARGS = '-server -rpcuser=test -rpcpassword=testpass -rpcport=8080 -txindex -debug -printtoconsole -rpcallowip=0.0.0.0/0'

	if len (sys.argv) == 1:
		os.system ('bitcoin-qt -testnet '+ARGS)
	elif len (sys.argv) > 1:
		cmd = '-qt'
		if len (sys.argv) == 3 and sys.argv[2] == 'daemon':
			ARGS += ' -daemon'
			cmd = 'd'
		if len (sys.argv) == 3 and sys.argv[2] == 'stop':
			cmd = '-cli'
			ARGS += ' stop'

		if sys.argv[1] == 'XLT':
			os.system ('litecoin'+cmd+' -testnet '+ARGS)
		elif sys.argv[1] == 'XTN':
			os.system ('bitcoin'+cmd+' -testnet '+ARGS)
		elif sys.argv[1] == 'XDT':
			os.system ('dogecoin'+cmd+' -testtest '+ARGS)
		elif sys.argv[1] == 'RXLT':
			os.system ('litecoin'+cmd+' -regtest '+ARGS)
		elif sys.argv[1] == 'RXTN':
			os.system ('bitcoin'+cmd+' -regtest '+ARGS)
		elif sys.argv[1] == 'RXDT':
			os.system ('dogecoin'+cmd+' -regtest '+ARGS)
		else:
			print ("unrecognized chain name", sys.argv[1])
	else:
		print ('usage: python '+sys.argv[0]+' chaincode [daemon|stop]')

if __name__ == "__main__":
	main ()

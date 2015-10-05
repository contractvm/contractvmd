# Contractvm
The contractVM daemon implementation. This is still a wip project, then the installation process could be a bit trivial. Anyway, a quick install script for ubuntu is available in this repository.


## Quick installation for Ubuntu users

The quickinstall.sh will install kad.py, contractvmd, libcontractvmd with sample dapps and all required dependencies.

First, download and run the installation script:

	``` curl https://raw.githubusercontent.com/contractvm/contractvmd/master/quickinstall.sh | sh ```

After the script execution, the contractvmd daemon and library should be installed.

Now we can start a local instance of the daemon (this is necessary since there isn't a test network at the moment); we do this by typing:

	``` contractvmd --discard-old-blocks ```

The default daemon instance includes all case studies dapps: blockstore, fifo-mom and tst, plus a dummy helloworld dapp. You can start a sample client application from samples directory of libcontractvm; in next lines we start the blockstore sample application:
	
	```
	cd ~/cvm-temp/libcontractvm/samples
	python3 bs_helloworld.py set
	# The sample app asks for a key-value pair, and it broadcasts the new pair in the network
	# After some minutes, the message will appears as confirmed in the blockchain; you can check the arrival of the message by switching in the contractvmd terminal.
	python3 bs_helloworld.py get
	# The sample app now asks for a previously saved key, querying node (at the time the local node) and returning the resulting value
	```

Obviously, you can start the contractvmd daemon from multiple nodes, creating a complex network; at the time there isn't a bootstraping mechanism (but it will be available soon), so when you start a new instance you have to specify a list of seed nodes.

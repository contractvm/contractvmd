# Contractvm
The contractVM daemon implementation. A quick install script for linux is available in this repository.

Documentation: http://contractvm.github.io/doc


## Quick start

The quickinstall.sh will install kad.py, contractvmd, libcontractvmd with sample dapps and all required dependencies.

First, install python3 and python3-pip (aka pip3); in ubuntu linux you can do this by:

```shell
sudo apt-get install python3 python3-pip
```


Then, download and run the installation script:

```shell
curl https://raw.githubusercontent.com/contractvm/contractvmd/master/quickinstall.sh | sh
```

After the script execution, the contractvmd daemon and library should be installed.

Now we can start a local instance of the daemon (this is necessary since there isn't a test network at the moment); we do this by typing:

```shell
contractvmd
```

Install one of case study dapps via dappman:

```shell
dappman --install blockstore
dappman --install cotst
dappman --install fifomom
```

Note that the default contractvmd uses Litecoin testnet as blockchain, and it connets to our test server to achieve a running litecoind instances.

Obviously, you can start the contractvmd daemon from multiple nodes, creating a complex network.

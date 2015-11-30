CVMD_STABLE=0043b16fad362299d027bb8f2b9c5b7eba1abcd0
LIBCVM_STABLE=a9e6a755346bc9cf899766d04bfbd74389df9794

PYTHON=python3
PIP=pip3


echo "Contractvmd quick installer for Linux"
sudo rm -rf ~/.contractvm

#echo "Installing required packages..."
#sudo apt-get install python3 python3-pip


echo "Installing contractvm"
cd ~/cvm-temp/
git clone https://github.com/contractvm/contractvmd
cd contractvmd
git checkout $CVMD_STABLE

echo "Installing requirements..."
sudo $PIP install -r requirements.txt

echo "Installing daemon..."
sudo $PYTHON setup.py install

echo "Installing contractvm-library"
cd ~/cvm-temp/
git clone https://github.com/contractvm/libcontractvm
cd libcontractvm
git checkout $(LIBCVM_STABLE)

echo "Installing requirements..."
sudo $PIP install -r requirements.txt

echo "Installing library..."
sudo $PYTHON setup.py install

echo "Installation done."



CVMD_STABLE=8453aac1cbb02b48bbb2eb32e1b5b180cc436351
LIBCVM_STABLE=1116c1e63c847a13ac6b4df6bb60b904e890e685
KADPY_STABLE=b35ef5ecf6be0b65d83828271cfda3ead07a086c

PYTHON=python3
PIP=pip3


echo "Contractvmd quick installer for Linux"
sudo rm -rf ~/.contractvm

#echo "Installing required packages..."
#sudo apt-get install python3 python3-pip


echo "Installing kad.py"
sudo rm -rf ~/cvm-temp/
mkdir -p ~/cvm-temp/
cd ~/cvm-temp/
git clone https://github.com/contractvm/kad.py.git
cd kad.py
git checkout $KADPY_STABLE
sudo $PIP install -r requirements.txt
sudo $PYTHON setup.py install


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



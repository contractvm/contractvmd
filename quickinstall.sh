# Quick installation for ubuntu
echo "Contractvmd quick installer for ubuntu"

echo "Installing required packages..."
sudo apt-get install python3 python3-pip


echo "Installing kad.py"
mkdir -p ~/cvm-temp/
cd ~/cvm-temp/
git clone git@github.com:contractvm/kad.py.git
cd kad.py
#sudo pip3 install -r requirements
sudo python3 setup.py install


echo "Installing contractvm"
cd ~/cvm-temp/
git clone git@github.com:contractvm/contractvmd
cd contractvmd

echo "Installing python dependecies..."
sudo pip3 install -r requirements.txt

echo "Installing daemon..."
sudo python3 setup.py install


echo "Installing contractvm-library"
cd ~/cvm-temp/
git clone git@github.com:contractvm/libcontractvm
cd libcontractvm

echo "Installing python dependecies..."
sudo pip3 install -r requirements.txt

echo "Installing library..."
sudo python3 setup.py install

echo "Installation done."

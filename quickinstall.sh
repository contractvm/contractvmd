# Quick installation for ubuntu
echo "Contractvmd quick installer for ubuntu"
sudo rm -rf ~/.contractvm

echo "Installing required packages..."
sudo apt-get install python3 python3-pip


echo "Installing kad.py"
sudo rm -rf ~/cvm-temp/
mkdir -p ~/cvm-temp/
cd ~/cvm-temp/
git clone git@github.com:contractvm/kad.py.git
cd kad.py
#git checkout 9e98d377fa228bf6938b57d522c15e6ca699ce27
sudo pip3 install -r requirements.txt
sudo python3 setup.py install


echo "Installing contractvm"
cd ~/cvm-temp/
git clone git@github.com:contractvm/contractvmd
cd contractvmd
#git checkout ab3c452708cc3acfd127b1ac668ed691303296a0

echo "Installing python dependecies..."
sudo pip3 install -r requirements.txt

echo "Installing daemon..."
sudo python3 setup.py install


echo "Installing contractvm-library"
cd ~/cvm-temp/
git clone git@github.com:contractvm/libcontractvm
cd libcontractvm
#git checkout 01447bbc47d9195c43eec206d8e4c682490f0bb1

echo "Installing python dependecies..."
sudo pip3 install -r requirements.txt

echo "Installing library..."
sudo python3 setup.py install

echo "Installation done."



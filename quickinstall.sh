PYTHON=python3.5
PIP=pip3



echo "Contractvmd quick installer for Linux"
sudo rm -rf ~/.contractvm

#echo "Installing required packages..."
#sudo apt-get install python3 python3-pip

sudo apt-get install -y libxml2-dev libxslt1-dev python3.5 python3.5-dev python3-pip curl git zlib1g-dev
sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.5 /usr/bin/python3

sudo apt-get remove python-pip
rm -f get-pip.py
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python3 get-pip.py

sudo pip3 uninstall -y contractvm libcontractvm
echo "Installing pycoin"
sudo pip3 install --upgrade pycoin

echo "Installing bitpeer"
sudo pip3 install --upgrade bitpeer.py

echo "Installing contractvm"
sudo pip3 install --upgrade contractvm

echo "Installing contractvm-library"
sudo pip3 install --upgrade libcontractvm

echo "Installation done."



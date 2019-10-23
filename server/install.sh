echo "Installing python2.7-dev"
sudo apt update
sudo apt-get -y install python2.7-dev

echo ""
echo "Installing PIP and python packages"
cd /tmp
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py
sudo pip install pyserial
sudo pip install Adafruit_LED_Backpack


echo ""
echo "Installing arcade-controller scripts"
mkdir /home/pi/arcade_controller
cd /home/pi/arcade_controller
curl https://raw.githubusercontent.com/lolnsw/arcade_controller/master/server/S25arcade-controller-server > /etc/init.d/S25arcade-controller-server
curl https://raw.githubusercontent.com/lolnsw/arcade_controller/master/server/arcade-controller-server.py > /home/pi/arcade_controller/arcade-controller-server.py
chmod +x /etc/init.d/S25arcade-controller-client
chmod +x /recalbox/share/custom_scripts/arcade-controller-client.py
echo "Installing Python depedencies"
mount -o remount rw, /
cd /tmp
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install pyserial

echo ""
echo "Enabling UART"
mount -o remount, rw /boot
echo "enable_uart=1" >> /boot/config.txt

echo ""
echo "Installing arcade-controller scripts"
mkdir /recalbox/share/custom_scripts
curl http://raw.githubusercontent.com/lolnsw/arcade_controller/master/client/S25arcade-controller-client > /etc/init.d/S25arcade-controller-client
curl http://raw.githubusercontent.com/lolnsw/arcade_controller/master/client/arcade-controller-client.py> /recalbox/share/custom_scripts/arcade-controller-client.py
chmod +x /etc/init.d/S25arcade-controller-client
chmod +x /recalbox/share/custom_scripts/arcade-controller-client.py

echo ""
echo "Rebooting..."

reboot

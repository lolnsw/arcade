mount -o remount rw, /
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install pyserial

mount -o remount, rw /boot
echo "enable_uart=1" >> /boot/config.txt

mkdir /recalbox/share/custom_scripts
curl https://github.com/lolnsw/arcade_controller/tree/master/client/S25arcade-controller-client > /etc/init.d/S25arcade-controller-client
curl https://github.com/lolnsw/arcade_controller/tree/master/client/arcade-controller-client.py > /recalbox/share/custom_scripts/arcade-controller-client.py
chmod +x /etc/init.d/S25arcade-controller-client
chmod +x /recalbox/share/custom_scripts/arcade-controller-client.py
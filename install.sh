#!/bin/bash

# set permissions for script files
chmod a+x /data/dbus-iobroker-smartmeter/restart.sh
chmod 744 /data/dbus-iobroker-smartmeter/restart.sh

chmod a+x /data/dbus-iobroker-smartmeter/uninstall.sh
chmod 744 /data/dbus-iobroker-smartmeter/uninstall.sh

chmod a+x /data/dbus-iobroker-smartmeter/service/run
chmod 755 /data/dbus-iobroker-smartmeter/service/run



# create sym-link to run script in deamon
ln -s /data/dbus-iobroker-smartmeter/service /service/dbus-iobroker-smartmeter



# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f $filename ]
then
    touch $filename
    chmod 755 $filename
    echo "#!/bin/bash" >> $filename
    echo >> $filename
fi

grep -qxF '/data/dbus-iobroker-smartmeter/install.sh' $filename || echo '/data/dbus-iobroker-smartmeter/install.sh' >> $filename

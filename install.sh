#!/bin/bash

# set permissions for script files
chmod a+x /data/dbus-senec-enfluri/restart.sh
chmod 744 /data/dbus-senec-enfluri/restart.sh

chmod a+x /data/dbus-senec-enfluri/uninstall.sh
chmod 744 /data/dbus-senec-enfluri/uninstall.sh

chmod a+x /data/dbus-senec-enfluri/service/run
chmod 755 /data/dbus-senec-enfluri/service/run



# create sym-link to run script in deamon
ln -s /data/dbus-senec-enfluri/service /service/dbus-senec-enfluri



# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f $filename ]
then
    touch $filename
    chmod 755 $filename
    echo "#!/bin/bash" >> $filename
    echo >> $filename
fi

grep -qxF '/data/dbus-senec-enfluri/install.sh' $filename || echo '/data/dbus-senec-enfluri/install.sh' >> $filename

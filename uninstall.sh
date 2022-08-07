#!/bin/bash

rm /service/dbus-senec-enfluri
kill $(pgrep -f 'supervise dbus-senec-enfluri')
chmod a-x /data/dbus-senec-enfluri/service/run
./restart.sh

#!/bin/bash

rm /service/dbus-iobroker-smartmeter
kill $(pgrep -f 'supervise dbus-iobroker-smartmeter')
chmod a-x /data/dbus-iobroker-smartmeter/service/run
./restart.sh

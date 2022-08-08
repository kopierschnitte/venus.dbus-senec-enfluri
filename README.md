# dbus-iobroker-smartmeter

Integrate any smartmeter which is connected to iobroker.

## Purpose

With the scripts in this repo it should be easy possible to install, uninstall, restart a service that .
Idea is pasend on @RalfZim project linked below.

## Inspiration

This project is my first on GitHub and with the Victron Venus OS, so I took some ideas and approaches from the following projects - many thanks for sharing the knowledge:

- https://github.com/kopierschnitte/venus.dbus-senec-enfluri
- https://github.com/RalfZim/venus.dbus-fronius-smartmeter
- https://github.com/victronenergy/dbus-smappee
- https://github.com/Louisvdw/dbus-serialbattery
- https://community.victronenergy.com/questions/85564/eastron-sdm630-modbus-energy-meter-community-editi.html

## How it works

### My setup

- iobroker smartmeter plugin ( https://github.com/Apollon77/ioBroker.smartmeter )
- iobroker simple api plugin ( https://github.com/ioBroker/ioBroker.simple-api )
- any ir reader for the smartmeter https://www.ebay.de/itm/125077162292

### Details / Process

As mentioned above the script is inspired by @RalfZim and @kopierschnitte fronius smartmeter implementation.
So what is the script doing:

- Running as a service
- connecting to DBus of the Venus OS `com.victronenergy.grid.http_40`
- After successful DBus connection, IOBroker smartmeter values are accessed. NOTE: it might be required to change the iobroker IDs in order to be functuonal for you (see method \_getIOBrokerSmartmeterData). IF you need it please open an issue, than this can also be added to the config file..
- Serial is taken from the response as device serial
- Paths are added to the DBus with default value 0 - including some settings like name, etc
- After that a "loop" is started which polls iobroker data every 1000ms from the REST-API and updates the values in the DBus

Thats it 😄

## Install & Configuration

- same as https://github.com/RalfZim/venus.dbus-fronius-smartmeter

### Get the code

Just grap a copy of the main branch and copy them to `/data/dbus-iobroker-smartmeter`.
Edit the config.ini file
Possibly edit \_getIOBrokerSmartmeterData to the paths you need
After that call the install.sh script.

## Used documentation

- https://github.com/victronenergy/venus/wiki/dbus#grid DBus paths for Victron namespace
- https://github.com/victronenergy/venus/wiki/dbus-api DBus API from Victron
- https://www.victronenergy.com/live/ccgx:root_access How to get root access on GX device/Venus OS

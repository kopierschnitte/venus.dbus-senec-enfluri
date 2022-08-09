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

## Install & Configuration

IO-Broker

- configure iobroker smartmeter plugin (or simply store your powers per phase in iobroker..)
- configure simple api plugin for api broker

Venus/GX

- Get Superuser rights on your CCGX device (https://www.victronenergy.com/live/ccgx:root_access#set_access_level_to_superuser)
- Configure root password
- Get the code from github
- configure config.ini and maintain the paths to the device-id (smart meter id), power overall, power phase 1 - 3
- Connect via winscp (or similar ssh clients) and copy over the code to /data/dbus-iobroker-smartmeter
- Possibly adjust the execution rights on install.sh (e.g. via winscp)
- Execute install.sh script

Config-INI Details

- All IOBroker Paths are referencing to the _full path_ of the iobroker object
- IOBrokerPathSmartMeterId --> Unique ID (serial) used - can e.g. be the serial of the smart meter
- IOBrokerPathOverallConsumption --> Consumption of all three phases in W
- IOBrokerPathPhase1 --> Consumption on phase 1 in W
- IOBrokerPathPhase2 --> Consumption on phase 2 in W
- IOBrokerPathPhase3 --> Consumption on phase 3 in W
- IOBrokerPathGridSold --> Total Sold in kWh
- IOBrokerPathGridBought --> Total Bought in kWh

Additionally the parameter _IOBrokerHostPath_ must give the absolute URL to your IOBroker instance.

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
- After successful DBus connection, IOBroker smartmeter values are accessed.
- Serial is taken from the response as device serial
- Paths are added to the DBus with default value 0 - including some settings like name, etc
- After that a "loop" is started which polls iobroker data every 1000ms from the REST-API and updates the values in the DBus

Thats it 😄

## Used documentation

- https://github.com/victronenergy/venus/wiki/dbus#grid DBus paths for Victron namespace
- https://github.com/victronenergy/venus/wiki/dbus-api DBus API from Victron
- https://www.victronenergy.com/live/ccgx:root_access How to get root access on GX device/Venus OS

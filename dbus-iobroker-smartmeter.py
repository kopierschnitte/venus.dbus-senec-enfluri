#!/usr/bin/env python

# import normal packages
from vedbus import VeDbusService
import platform
import logging
import sys
import os
import sys
if sys.version_info.major == 2:
    import gobject
else:
    from gi.repository import GLib as gobject
import sys
import time
import requests  # for http GET
import configparser  # for config/ini file
import struct

# our own packages from victron
sys.path.insert(1, os.path.join(os.path.dirname(__file__),
                '/opt/victronenergy/dbus-systemcalc-py/ext/velib_python'))


class DbusIobrokerSmartmeterService:
    def __init__(self, servicename, deviceinstance, paths, productname='Smartmeter Reader', connection='Smartmeter via IOBroker HTTP JSON service'):
        self._dbusservice = VeDbusService(
            "{}.http_{:02d}".format(servicename, deviceinstance))
        self._paths = paths

        self._config = self._getConfig()

        # get data from Senec
        meter_data = self._getIOBrokerSmartmeterData()

        self.grid_sold_start = next((x for x in meter_data if x['id'] ==
                                     self._getSmartMeterGridSold()), None)['val']
        self.grid_bought_start = next((x for x in meter_data if x['id'] ==
                                       self._getSmartMeterGridBought()), None)['val']

        logging.debug("%s /DeviceInstance = %d" %
                      (servicename, deviceinstance))

        # debug:
        #logging.info("Senec serial: %s" % (self._getSenecSerial()))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path(
            '/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        # self._dbusservice.add_path('/ProductId', 16) # value used in ac_sensor_bridge.cpp of dbus-cgwacs
        # self._dbusservice.add_path('/ProductId', 0xFFFF) # id assigned by Victron Support from SDM630v2.py
        # found on https://www.sascha-curth.de/projekte/005_Color_Control_GX.html#experiment - should be an ET340 Engerie Meter
        self._dbusservice.add_path('/ProductId', 45069)
        # found on https://www.sascha-curth.de/projekte/005_Color_Control_GX.html#experiment - should be an ET340 Engerie Meter
        self._dbusservice.add_path('/DeviceType', 345)
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/CustomName', productname)
        self._dbusservice.add_path('/Latency', None)
        self._dbusservice.add_path('/FirmwareVersion', 0.1)
        self._dbusservice.add_path('/HardwareVersion', 0)
        self._dbusservice.add_path('/Connected', 1)
        self._dbusservice.add_path('/Role', 'grid')
        # normaly only needed for pvinverter
        self._dbusservice.add_path('/Position', 0)
        self._dbusservice.add_path('/Serial', self._getSmartMeterSerial())
        self._dbusservice.add_path('/UpdateIndex', 0)

        # add path values to dbus
        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path, settings['initial'], gettextcallback=settings['textformat'], writeable=True, onchangecallback=self._handlechangedvalue)

        # last update
        self._lastUpdate = 0

        # add _update function 'timer'
        # pause 1000ms before the next request
        gobject.timeout_add(500, self._update)

        # add _signOfLife 'timer' to get feedback in log every 5minutes
        gobject.timeout_add(self._getSignOfLifeInterval()
                            * 60*1000, self._signOfLife)

    def _getSmartMeterSerial(self):
        meter_data = self._getIOBrokerSmartmeterData()

        device_id = next(
            (x for x in meter_data if x['id'] == self._getSmartMeterDeviceId()), None)

        if not device_id['val']:
            raise ValueError(
                "Response does not contain 'DEVICE_ID' attribute")

        serial = device_id['val']
        return serial

    def _getConfig(self):
        config = configparser.ConfigParser()
        config.read("%s/config.ini" %
                    (os.path.dirname(os.path.realpath(__file__))))
        return config

    def _getSignOfLifeInterval(self):
        value = self._config['DEFAULT']['SignOfLifeLog']

        if not value:
            value = 0

        return int(value)

    def _getSmartMeterDeviceId(self):
        value = self._config['DEFAULT']['IOBrokerPathSmartMeterId']
        return value

    def _getSmartMeterOverallConsumption(self):
        value = self._config['DEFAULT']['IOBrokerPathOverallConsumption']
        return value

    def _getSmartMeterPhase1Consumption(self):
        value = self._config['DEFAULT']['IOBrokerPathPhase1']
        return value

    def _getSmartMeterPhase2Consumption(self):
        value = self._config['DEFAULT']['IOBrokerPathPhase2']
        return value

    def _getSmartMeterPhase3Consumption(self):
        value = self._config['DEFAULT']['IOBrokerPathPhase3']
        return value

    def _getSmartMeterGridSold(self):
        value = self._config['DEFAULT']['IOBrokerPathGridSold']
        return value

    def _getSmartMeterGridBought(self):
        value = self._config['DEFAULT']['IOBrokerPathGridBought']
        return value

    def _getSmartMeterVoltage(self):
        value = self._config['DEFAULT']['IOBrokerPathVoltage']
        return value

    def _getIOBrokerPath(self):
        value = self._config['DEFAULT']['IOBrokerHostPath']
        return value

    def _getIOBrokerSmartmeterData(self):
        URL = self._getIOBrokerPath() + "/getBulk/" + self._getSmartMeterDeviceId() + "," + self._getSmartMeterOverallConsumption() + "," + \
            self._getSmartMeterPhase1Consumption() + "," + self._getSmartMeterPhase2Consumption() + \
            "," + self._getSmartMeterPhase3Consumption() + "," + self._getSmartMeterGridBought() + \
            "," + self._getSmartMeterGridSold() + "," + self._getSmartMeterVoltage()

        headers = {}

        meter_r = requests.request("GET", URL, headers=headers)

        # check for response
        if not meter_r:
            raise ConnectionError("No response from IOBroker - %s" % (URL))

        meter_data = meter_r.json()

        # check for Json
        if not meter_data:
            raise ValueError("Converting response to JSON failed")

        return meter_data

    def _floatFromHex(self, val):

        return struct.unpack('!f', bytes.fromhex(val[3:]))[0]
        #struct.unpack('!f', (val[3:]).decode('hex'))[0]

    def _signOfLife(self):
        logging.info("--- Start: sign of life ---")
        logging.info("Last _update() call: %s" % (self._lastUpdate))
        ##logging.info("Last '/Ac/Power': %s" % (self._dbusservice['/Ac/Power']))
        logging.info("--- End: sign of life ---")
        return True

    def _update(self):
        try:
            # get data from Senec
            meter_data = self._getIOBrokerSmartmeterData()

            # send data to DBus
            total_value = next(
                (x for x in meter_data if x['id'] == self._getSmartMeterOverallConsumption()), None)['val']
            phase_1 = next((x for x in meter_data if x['id'] ==
                            self._getSmartMeterPhase1Consumption()), None)['val']
            phase_2 = next((x for x in meter_data if x['id'] ==
                            self._getSmartMeterPhase2Consumption()), None)['val']
            phase_3 = next((x for x in meter_data if x['id'] ==
                            self._getSmartMeterPhase3Consumption()), None)['val']
            grid_sold = next((x for x in meter_data if x['id'] ==
                              self._getSmartMeterGridSold()), None)['val'] - self.grid_sold_start
            grid_bought = next((x for x in meter_data if x['id'] ==
                                self._getSmartMeterGridBought()), None)['val'] - self.grid_bought_start
            voltage = next((x for x in meter_data if x['id'] ==
                            self._getSmartMeterVoltage()), None)['val']

            # positive: consumption, negative: feed into grid
            self._dbusservice['/Ac/Power'] = total_value
            self._dbusservice['/Ac/L1/Voltage'] = voltage
            self._dbusservice['/Ac/L2/Voltage'] = voltage
            self._dbusservice['/Ac/L3/Voltage'] = voltage
            self._dbusservice['/Ac/L1/Current'] = phase_1 / voltage
            self._dbusservice['/Ac/L2/Current'] = phase_2 / voltage
            self._dbusservice['/Ac/L3/Current'] = phase_3 / voltage
            self._dbusservice['/Ac/L1/Power'] = phase_1
            self._dbusservice['/Ac/L2/Power'] = phase_2
            self._dbusservice['/Ac/L3/Power'] = phase_3

            self._dbusservice['/Ac/Current'] = total_value / voltage
            self._dbusservice['/Ac/Voltage'] = phase_3

            ##self._dbusservice['/Ac/L1/Energy/Forward'] = (meter_data['emeters'][0]['total']/1000)
            self._dbusservice['/Ac/Energy/Forward'] = grid_bought
            self._dbusservice['/Ac/Energy/Reverse'] = grid_sold

            # logging
            ##logging.info("House Consumption (/Ac/Power): %s" % (self._dbusservice['/Ac/Power']))
            #logging.info("L1: %s L2: %s L3: %s" % (self._dbusservice['/Ac/L1/Power'],self._dbusservice['/Ac/L2/Power'],self._dbusservice['/Ac/L3/Power']))
            ##logging.debug("House Forward (/Ac/Energy/Forward): %s" % (self._dbusservice['/Ac/Energy/Forward']))
            ##logging.debug("House Reverse (/Ac/Energy/Revers): %s" % (self._dbusservice['/Ac/Energy/Reverse']))
            # logging.debug("---");

            # increment UpdateIndex - to show that new data is available
            index = self._dbusservice['/UpdateIndex'] + 1  # increment index
            if index > 255:   # maximum value of the index
                index = 0       # overflow from 255 to 0
            self._dbusservice['/UpdateIndex'] = index

            # update lastupdate vars
            self._lastUpdate = time.time()
        except Exception as e:
            logging.critical('Error at %s', '_update', exc_info=e)

        # return true, otherwise add_timeout will be removed from GObject - see docs http://library.isr.ist.utl.pt/docs/pygtk2reference/gobject-functions.html#function-gobject--timeout-add
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


def main():
    # configure logging
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler(
                                "%s/current.log" % (os.path.dirname(os.path.realpath(__file__)))),
                            logging.StreamHandler()
                        ])

    try:
        logging.info("Start")

        from dbus.mainloop.glib import DBusGMainLoop
        # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
        DBusGMainLoop(set_as_default=True)

        # formatting
        def _kwh(p, v): return (str(round(v, 2)) + ' KWh')
        def _a(p, v): return (str(round(v, 1)) + ' A')
        def _w(p, v): return (str(round(v, 1)) + ' W')
        def _v(p, v): return (str(round(v, 1)) + ' V')

        # start our main-service
        pvac_output = DbusIobrokerSmartmeterService(
            servicename='com.victronenergy.grid',
            deviceinstance=40,
            paths={
                # energy bought from the grid
                '/Ac/Energy/Forward': {'initial': 0, 'textformat': _kwh},
                # energy sold to the grid
                '/Ac/Energy/Reverse': {'initial': 0, 'textformat': _kwh},
                '/Ac/Power': {'initial': 0, 'textformat': _w},

                '/Ac/Current': {'initial': 0, 'textformat': _a},
                '/Ac/Voltage': {'initial': 0, 'textformat': _v},

                '/Ac/L1/Voltage': {'initial': 0, 'textformat': _v},
                '/Ac/L2/Voltage': {'initial': 0, 'textformat': _v},
                '/Ac/L3/Voltage': {'initial': 0, 'textformat': _v},
                '/Ac/L1/Current': {'initial': 0, 'textformat': _a},
                '/Ac/L2/Current': {'initial': 0, 'textformat': _a},
                '/Ac/L3/Current': {'initial': 0, 'textformat': _a},
                '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L2/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L3/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L1/Energy/Forward': {'initial': 0, 'textformat': _kwh},
                '/Ac/L2/Energy/Forward': {'initial': 0, 'textformat': _kwh},
                '/Ac/L3/Energy/Forward': {'initial': 0, 'textformat': _kwh},
                '/Ac/L1/Energy/Reverse': {'initial': 0, 'textformat': _kwh},
                '/Ac/L2/Energy/Reverse': {'initial': 0, 'textformat': _kwh},
                '/Ac/L3/Energy/Reverse': {'initial': 0, 'textformat': _kwh},
            })

        logging.info(
            'Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
        mainloop = gobject.MainLoop()
        mainloop.run()
    except Exception as e:
        logging.critical('Error at %s', 'main', exc_info=e)


if __name__ == "__main__":
    main()

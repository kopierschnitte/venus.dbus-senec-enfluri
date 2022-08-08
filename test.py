

import requests  # for http GET


class DbusIobrokerSmartmeterService:
    def _getIOBrokerSmartmeterData(self):
        URL = "http://192.168.178.81:8087/getBulk/smartmeter.0.1-0:96_1_0__255.value,smartmeter.0.1-0:16_7_0__255.value,smartmeter.0.1-0:36_7_0__255.value,smartmeter.0.1-0:56_7_0__255.value,smartmeter.0.1-0:76_7_0__255.value"

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


pvac_output = DbusIobrokerSmartmeterService()
meter_data = pvac_output._getIOBrokerSmartmeterData()


total_value = next(
    (x for x in meter_data if x['id'] == "smartmeter.0.1-0:16_7_0__255.value"), None)['val']
phase_1 = next((x for x in meter_data if x['id'] ==
                "smartmeter.0.1-0:36_7_0__255.value"), None)['val']
phase_2 = next((x for x in meter_data if x['id'] ==
                "smartmeter.0.1-0:56_7_0__255.value"), None)['val']
phase_3 = next((x for x in meter_data if x['id'] ==
                "smartmeter.0.1-0:76_7_0__255.value"), None)['val']

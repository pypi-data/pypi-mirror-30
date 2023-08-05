"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import json
from .jemu_button import JemuButton
from .jemu_mem_peripheral import JemuMemPeripheral
from .jemu_bma280 import JemuBMA280
from .jemu_bme280 import JemuBME280
from .jemu_sudo import JemuSudo
from .jemu_bq24160 import JemuBQ24160
from .jemu_bq27421 import JemuBQ27421


class JemuPeripheralsParser:
    _EXTERNAL_PERIPHERAL = "External"
    _NRF52_PERIPHERAL = "nrf52"

    __peripherals_json_path = None

    def __init__(self, peripherals_json_path):
        self.__peripherals_json_path = peripherals_json_path

    def get_peripherals(self, jemu_connection):
        peripheral_list = []
        mcu_list = []

        if not os.path.isfile(self.__peripherals_json_path):
            raise Exception(self.__peripherals_json_path + ' is not found')
        elif not os.access(self.__peripherals_json_path, os.R_OK):
            raise Exception(self.__peripherals_json_path + ' is not readable')
        else:
            with open(self.__peripherals_json_path) as peripherals_json_file:
                peripherals_json = json.load(peripherals_json_file)

                for peripheral in peripherals_json["Peripherals"]:
                    peripheral_id = peripheral["id"]

                    if ("config" in peripheral) and ("generators" in peripheral["config"]):
                        generators = peripheral["config"]["generators"]
                    else:
                        generators = None

                    if peripheral["class"] == "Button":
                        peripheral_obj = JemuButton(jemu_connection, peripheral_id)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "BME280":
                        peripheral_obj = JemuMemPeripheral(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "M24C04":
                        peripheral_obj = JemuMemPeripheral(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "AD7798":
                        peripheral_obj = JemuMemPeripheral(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "ADG1404":
                        peripheral_obj = JemuMemPeripheral(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "PCA9539A":
                        peripheral_obj = JemuMemPeripheral(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "BQ24160":
                        peripheral_obj = JemuBQ24160(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "BQ27421":
                        peripheral_obj = JemuBQ27421(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})
                    
                    if peripheral["class"] == "BMA280":
                        peripheral_obj = JemuBMA280(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "BME280":
                        peripheral_obj = JemuBME280(jemu_connection, peripheral_id, self._EXTERNAL_PERIPHERAL, generators)
                        peripheral_list.append({"obj": peripheral_obj, "name": peripheral["name"]})

                    if peripheral["class"] == "Nrf52832":
                        mcu_list.append(peripheral["name"])

                    elif peripheral["class"] == "MCU":
                        mcu_list.append(peripheral["name"])

                if "InternalsPeripherals" not in peripherals_json:
                    return peripheral_list

                # Load internak peripherals
                internal_peripherals = peripherals_json["InternalsPeripherals"]
                for mcu in mcu_list:
                    if mcu not in internal_peripherals:
                        continue
                    peripherals = internal_peripherals[mcu]
                    for peripheral in peripherals:
                        if peripheral["class"] == "SUDO":
                            peripheral_obj = JemuSudo(jemu_connection, peripheral["id"], mcu)
                            peripheral_list.append({"obj": peripheral_obj, "name": peripheral["class"]})
                
            return peripheral_list

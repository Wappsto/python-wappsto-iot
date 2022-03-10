#!/usr/bin/python3
import struct
import smbus2
from smbus2 import i2c_msg
import time
from collections import namedtuple


class SCD30():
    def __init__(self, i2cbus, measurement_interval, auto_calibration, pressure):
        """Starts the scd30 driver."""
        super(SCD30, self).__init__()

        self.i2c_address = 0x61
        self.bus_number = smbus2.SMBus(i2cbus)

        self.__set_measurement_interval(measurement_interval)
        time.sleep(0.1)
        self.__set_auto_calibration(auto_calibration)
        time.sleep(0.1)
        if pressure:
            self.__start_periodic_measurement(pressure)
            time.sleep(0.1)

    # Set measurement interval
    def __set_measurement_interval(self, interval):
        try:
            cmd_set_measurement_interval = self.__create_cmd(interval, 0x00)
            self.bus_number.write_i2c_block_data(self.i2c_address, 0X46, cmd_set_measurement_interval)
        except OSError as e:
            print("set_measurement_interval: " + str(e))

    # Start periodic measurement
    def __start_periodic_measurement(self, pressure):
        try:
            cmd_start_periodic_measurement = self.__create_cmd(pressure, 0x10)
            self.bus_number.write_i2c_block_data(self.i2c_address, 0X00, cmd_start_periodic_measurement)
            time.sleep(0.1)
            print("%7.2f hPa 2" % pressure)
        except OSError as e:
            print("start_periodic_measurement: " + str(e))

    # Set auto calibration
    def __set_auto_calibration(self, on_off):
        try:
            cmd_set_auto_calibration = self.__create_cmd(on_off, 0x06)
            self.bus_number.write_i2c_block_data(self.i2c_address, 0x53, cmd_set_auto_calibration)
        except OSError as e:
            print("set_auto_calibration: " + str(e))

    # Get Data ready
    def data_ready(self):
        """Checks if data is ready."""
        try:
            self.bus_number.write_byte_data(self.i2c_address, 0x02, 0x02)
            time.sleep(0.1)
            data_ready = i2c_msg.read(self.i2c_address, 3)
            time.sleep(0.1)
            self.bus_number.i2c_rdwr(data_ready)

            return bool(list(data_ready)[1])
        except OSError as e:
            print("OSError in scd30 data_ready: " + str(e))
            return False

    # Read measurement buffer
    def get_scd30_measurements(self, ):
        """Gets the scd30 measurement."""
        try:
            self.bus_number.write_byte_data(self.i2c_address, 0x03, 0x00)
            time.sleep(0.1)

            measurement = i2c_msg.read(self.i2c_address, 18)
            self.bus_number.i2c_rdwr(measurement)

            co2_list = [0, 1, 2, 3, 4, 5]
            co2_measurement = self.__get_measurement(measurement, co2_list)

            temperature_list = [6, 7, 8, 9, 10, 11]
            temperature_measurement = self.__get_measurement(measurement, temperature_list)

            humidity_list = [12, 13, 14, 15, 16, 17]
            humidity_measurement = self.__get_measurement(measurement, humidity_list)

            if co2_measurement and humidity_measurement and temperature_measurement:
                return self.__to_name_tuple(co2_measurement, humidity_measurement, temperature_measurement)
            else:
                return None

        except OSError as e:
            print("OSError in scd30 get_scd30_measurements: " + str(e))
            return None

    def __extract_measurement(self, i, measurement):
        return list(measurement)[i]

    def __pack_struct(self, i, i1, i2, i3, measurement):
        return struct.pack('4B',
                           self.__extract_measurement(i, measurement),
                           self.__extract_measurement(i1, measurement),
                           self.__extract_measurement(i2, measurement),
                           self.__extract_measurement(i3, measurement))

    def __crc8_update(self, b, crc):
        crc = crc ^ b
        for i in range(8):
            if (crc & 0x80) == 0x80:
                crc = (crc << 1) ^ 0x131
            else:
                crc <<= 1
        return crc

    def __calc_crc(self, d):
        crc = self.__crc8_update((d >> 8) & 0x00FF, 0xff)
        crc = self.__crc8_update((d & 0x00FF), crc)
        return crc

    def __get_crc(self, i, j, measurement):
        crc = self.__crc8_update(list(measurement)[i], 0xff)
        crc = self.__crc8_update(list(measurement)[j], crc)
        return crc

    def __get_measurement(self, measurement, val_list):
        crc = self.__get_crc(val_list[0], val_list[1], measurement)
        unpacked_measurement = None

        if crc == self.__extract_measurement(val_list[2], measurement):
            crc = self.__get_crc(val_list[3], val_list[4], measurement)
            if crc == self.__extract_measurement(val_list[5], measurement):
                tmp = self.__pack_struct(val_list[0], val_list[1], val_list[3], val_list[4], measurement)
                unpacked_measurement = struct.unpack('>f', tmp)
        return unpacked_measurement

    def __create_cmd(self, payload, x_):
        ff = 0x00FF
        i = 8
        return [x_, (payload >> i) & ff, (payload & ff), self.__calc_crc(payload)]

    def __to_name_tuple(self, co2_measurement, humidity_measurement, temperature_measurement):
        Data = namedtuple('Data', ['CO2', 'temperature', 'humidity'])
        return Data(co2_measurement[0], temperature_measurement[0], humidity_measurement[0])


if __name__ == "__main__":

    try:
        scd30 = SCD30(1, 5, 1, None)

        while(1):
            if scd30.data_ready():
                print("ready")
                print(list(scd30.get_scd30_measurements()))
            else:
                print("nope")
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        print("Stopped")

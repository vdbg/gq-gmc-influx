from datetime import datetime
import logging
import platform
import re
import serial
import serial.tools.list_ports


class GqGmcConnector:
    """
    Documentation of protocol: http://www.gqelectronicsllc.com/download/GQ-RFC1201.txt
    CPM: counts per minute. 0-> safe <-50-> Attention <-100-> Danger
    """

    def __init__(self, port: str, baudrate: int, timeout: int, check: bool, expected_version: str):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

        if check:
            if len(serial.tools.list_ports.comports()) == 0:
                raise Exception("No serial ports detected. Check that the device is plugged into an USB port.")

            actual_version = self.__get_firmware_version()

            if not re.search(expected_version, actual_version):
                raise Exception(f"Actual GMC version {actual_version} did not match expected {expected_version}.")

            logging.info(f"Device version: {actual_version}")

    def __flush_serial_port(self) -> bytearray:
        ret = b""

        while True:
            x = self.ser.read(1)
            if len(x) == 0:
                break
            ret += x

        return ret

    def __send_command(self, command: bytearray) -> None:
        self.ser.write(b'<'+command+b'>>')

    def __get_data(self, size: int) -> bytearray:
        return self.ser.read(size) + self.__flush_serial_port()

    def __get_firmware_version(self) -> str:
        self.__send_command(b'GETVER')
        return self.__get_data(15).decode().strip()

    def __get_sensor_value(self, command) -> int:
        size = 4  # older firmware versions return 2 bytes instead
        self.__send_command(command)
        ret = self.__get_data(size)

        if len(ret) == size:
            return ((ret[0] << 8 | ret[1]) << 8 | ret[2]) << 8 | ret[3]

        raise Exception(f"Expected {size} bytes; got {len(ret)} instead. Possibly wrong model or firmware version.")

    def fetch_data(self):
        cpm = self.__get_sensor_value(b'GETCPM')
        logging.debug(f"CPM: {cpm}")

        return {
            "measurement": "radiation",
            "tags": {"host": platform.node()},
            "fields": {"cpm": cpm},
            "time": datetime.utcnow()
        }

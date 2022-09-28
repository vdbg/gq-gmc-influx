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
        self.check = check

        if check:
            if len(serial.tools.list_ports.comports()) == 0:
                logging.warning("No serial ports detected. If not running in Docker container, check that the device is plugged into an USB port.")

            actual_version = self.__get_firmware_version()

            if not re.search(expected_version, actual_version):
                raise Exception(f"Actual GMC version {actual_version} did not match expected {expected_version}.")

            logging.info(f"Device version: {actual_version}")

    def __read_all(self) -> bytearray:
        ret = b""

        while self.check:
            x = self.ser.read(1)
            if not x:
                break
            ret += x

        return ret

    def __send_command(self, command: bytearray) -> None:
        self.ser.write(b'<'+command+b'>>')

    def __get_data(self, size: int) -> bytearray:
        return self.ser.read(size) + self.__read_all()

    def __get_firmware_version(self) -> str:
        self.__send_command(b'GETVER')
        return self.__get_data(15).decode().strip()

    def __get_sensor_value(self, command) -> int:
        size = 4  # older firmware versions return 2 bytes instead
        self.__send_command(command)
        ret = self.__get_data(size)

        if len(ret) == size:
            return int.from_bytes(ret, byteorder='big')

        raise Exception(f"Expected {size} bytes; got {len(ret)} instead. Possibly wrong model or firmware version.")

    def fetch_data(self, measurement: str):
        cpm = self.__get_sensor_value(b'GETCPM')
        logging.info(f"CPM: {cpm}")

        return {
            "measurement": measurement,
            "tags": {"host": platform.node()},
            "fields": {"cpm": cpm},
            "time": datetime.utcnow()
        }

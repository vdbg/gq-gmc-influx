from influxdb_client import InfluxDBClient
import logging


class InfluxConnector:

    def __init__(self, bucket: str, token: str, org: str, url: str):
        self.bucket = bucket
        self.token = token
        self.org = org
        self.url = url

    def __get_client(self) -> InfluxDBClient:
        return InfluxDBClient(url=self.url, token=self.token, org=self.org, debug=False)

    def add_samples(self, records) -> None:
        logging.debug(f"Importing record to influx.")
        with self.__get_client() as client:
            with client.write_api() as write_api:
                write_api.write(bucket=self.bucket, record=records)

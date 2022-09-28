#!/usr/bin/python3

import logging
import time
import yaml

from influx import InfluxConnector
from gqgmc import GqGmcConnector
from pathlib import Path

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)


def get_config():
    CONFIG_FILE = "config.yaml"
    try:
        with open(Path(__file__).with_name(CONFIG_FILE)) as config_file:
            config = yaml.safe_load(config_file)

            if not config:
                raise ValueError(f"Invalid {CONFIG_FILE}. See template.{CONFIG_FILE}.")

            for name in {"influx", "gqgmc", "main"}:
                if name not in config:
                    raise ValueError(f"Invalid {CONFIG_FILE}: missing section {name}.")

            return config
    except FileNotFoundError as e:
        logging.error(f"Missing {e.filename}.")
        exit(2)


try:
    config = get_config()

    main_conf = config["main"]
    logging.getLogger().setLevel(logging.getLevelName(main_conf["logverbosity"]))
    loop_seconds: int = main_conf["loop_seconds"]

    influx_conf = config["influx"]
    measurement: str = influx_conf["measurement"]
    influxConnector = InfluxConnector(influx_conf["bucket"], influx_conf["token"], influx_conf["org"], influx_conf["url"])

    gq_conf = config["gqgmc"]
    gcmConnector = GqGmcConnector(gq_conf["port"], gq_conf["baudrate"], gq_conf["timeout"], gq_conf["check"], gq_conf["version"])

    while True:
        try:
            record = gcmConnector.fetch_data(measurement)
            influxConnector.add_samples(record)
            if not loop_seconds:
                exit(0)
            time.sleep(loop_seconds)
        except Exception as e:
            logging.exception(e)


except Exception as e:
    logging.exception(e)
    exit(1)

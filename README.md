# GQ GMC-500 to InfluxDB

Allows for importing data from a [GQ GMC-500 Geiger counter](https://www.gqelectronicsllc.com/comersus/store/comersus_viewItem.asp?idProduct=5631) to [InfluxDB](https://www.influxdata.com/) v2.

## Requirements

- A [GQ GMC-500 Geiger counter](https://www.gqelectronicsllc.com/comersus/store/comersus_viewItem.asp?idProduct=5631). May work on other models, but that's the one tested.
- A device that can run Linux and be linked to the Geiger counter with a USB cable. Tested with a [Raspberry pi](https://www.raspberrypi.com/products/) 2.
- Either [Docker](https://www.docker.com/) or Python 3.7 or later installed on this device.
- [InfluxDB](https://en.wikipedia.org/wiki/InfluxDB) v2 installed on this or another device, and a bucket created in influxDB.


## Setup

### With Docker

Dependency: Docker installed.

``
sudo docker run \
  -d \
  --name gq-gmc \
  -v /path_to_your/config.yaml:/app/config.yaml \
  --memory=100m \
  --pull always \
  --device=/dev/ttyUSB1 \
  vdbg/gq-gmc-influx:latest
``

### Without Docker

Dependency: Python3 and pip3 installed. `sudo apt-get install python3-pip` if missing on raspbian.

1. Git clone this repository and cd into directory
2. `cp template.config.yaml config.yaml`
3. Edit file `config.yaml` by following instructions in file
4. `pip3 install -r requirements.txt`
5. `python3 main.py` or `./main.py`

## Alternatives

The `geigerlog_simple_500plus-v0.2.2.zip` located [here](https://sourceforge.net/projects/geigerlog/files/)
can query other fields, and handles different firmware & Python versions. It does not however import to influx.



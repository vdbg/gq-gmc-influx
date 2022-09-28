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

1. Identify the USB port the Geiger counter is attached to. Running `dmesg | grep ttyUSB` after plugging-in the USB cable may help to identify (in my case: `ch341-uart converter now attached to ttyUSB1`)
2. Download and run the Docker image (in this example, `/dev/ttyUSB1` is the identified USB port): `sudo docker run --name gq-gmc -v config.yaml:/app/config.yaml --device=/dev/ttyUSB1 vdbg/gq-gmc-influx:latest`
3. Copy template config file from image: `sudo docker cp gq-gmc:/app/template.config.yaml config.yaml`
4. Edit `config.yaml` by following the instructions in the file
5. Start the container again to verify the settings are correct: `sudo docker start gq-gmc -i`
6. Once the settings are finalized, `Ctrl-C` to stop the container, `sudo docker container rm gq-gmc` to delete it
7. Start the container with final settings:

```
sudo docker run \
  -d \
  --name gq-gmc \
  -v /path_to_your/config.yaml:/app/config.yaml \
  --memory=100m \
  --pull=always \
  --restart=always \
  --device=/dev/ttyUSB1 \
  vdbg/gq-gmc-influx:latest
```

### Without Docker

Dependency: Python3 and pip3 installed. `sudo apt-get install python3-pip` if missing on raspbian.

1. Git clone this repository and cd into directory
2. `cp template.config.yaml config.yaml`
3. Edit file `config.yaml` by following the instructions in the file
4. `pip3 install -r requirements.txt`
5. `python3 main.py` or `./main.py`

## Troubleshooting

### Power supply

If using a Raspberry pi, make sure it is properly powered for both itself and the Geiger counter. `dmesg` to see if it's the case

### Stops working on reboots

If more than one USB device is attached, the magic number `x` in `ttyUSBx` may not be preserved on reboots. To handle this case:

  - Determine idVendor, idProduct and serial from dmesg output. Taking the below example, the values are respectively: 1a86, 7523 and 0
```
[  541.891928] usb 1-1.2: new full-speed USB device number 5 using dwc_otg
[  542.024969] usb 1-1.2: New USB device found, idVendor=1a86, idProduct=7523, bcdDevice= 2.64
[  542.024991] usb 1-1.2: New USB device strings: Mfr=0, Product=2, SerialNumber=0
```
  - Verify that there's only one device with this combination: `dmesg | grep idVendor`
  - Add one of the following lines to the file under `/etc/udev/rules.d` (replace `idVendor`, `idProduct` and `serial` accordingly):
```
# If serial number is different than 0:
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", ATTRS{serial}=="123456", SYMLINK+="ttyGMC"
# If serial number is 0:
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyGMC"
```
  - Reload udev: `sudo udevadm control --reload-rules && sudo udevadm trigger`
  - Verify that it worked: `ls -l /dev/ttyGMC` should return something simular to `/dev/ttyGMC -> ttyUSB1`
  - Change both the `port` parameter in `config.yaml` and the `--device` parameter for the `docker run` incantation accordingly


## Alternatives

The `geigerlog_simple_500plus-v0.2.2.zip` located [here](https://sourceforge.net/projects/geigerlog/files/)
can query other fields, and handles different firmware & Python versions. It does not however import to influx.



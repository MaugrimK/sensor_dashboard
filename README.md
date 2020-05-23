# Raspberry Pi Zero Sensor Dashboard
Flask dashboard to manage camera and temperature sensor on Raspberry Pi Zero.

## Features
* Flask webserver
* Autostart on boot by systemd
* Periodic task (apscheduler) to take temperature measurements
* Store readings in a SQLite DB
* Use Adafruit_DHT sensor driver
* Keep 1 week history of temperature measurements
* Button to take pictures from a camera module
* Bokeh interactive graph to display temperature readings
* Take fake measurements to run the app in test mode/without sensors/on other 
platforms 

## Preview
Homepage:

<img src=images/homepage.png width=400>

Interactive Bokeh graph showing temperature and humidity readings:

<img src=images/measurement_timeseries.png width=400>

## Hardware
* Raspberry Pi Zero Wireless WH (Pre-Soldered Header)
* Camera
    * Raspberry Pi Zero Camera Module Night Vision Wide Angle Fisheye 
5MP Webcam with Infrared IR Sensor LED Light for RPI Zero
* Sensor
    * DHT22 AM2302 Digital Temperature and Humidity Sensor Module
    * The sensor is connected to +5V, Ground and Pin 38 (GPIO20)

## Run the app

#### Install Raspbian on Raspberry Pi Zero
```
https://www.raspberrypi.org/downloads/raspbian/
```
#### Clone the repository
```
cd /home/pi/dev
git clone <repository>
```
#### Create virtual env
```
pip install --upgrade pip
python3 -m venv /home/pi/dev/env
source /home/pi/dev/env/bin/activate
pip install -r /home/pi/dev/sensor_dashboard/requirements.txt
```
#### Additional install for numpy
```
sudo apt-get install python-dev libatlas-base-dev
```
#### Setup the service to autostart on reboot
```
sudo ln -s /home/pi/dev/sensor_dashboard/sensor_dashboard/website.service /etc/systemd/system/website.service
sudo systemctl daemon-reload
sudo systemctl enable website
```
#### start|stop|display status of the service
```
sudo systemctl start|stop|status website
```
#### View live logs
```
journalctl -u website
```
#### Run in debug mode from a different platform
```
set PYTHONPATH=.

python sensor_dashboard\app.py --fake-measurements --db-path=<db path> --photo-dir=<photo dir path>/sensor_dashboard/static --debug
```
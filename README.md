# FEDWatcher

FEDWatcher is sofware to connect up to 4 [FED3 feeder devices](https://github.com/KravitzLabDevices/FED3/) to one Raspberry Pi 4. 
The Raspberry Pi communicates with the FED3 devices using software serial from the BNC/headphone jack port of the Adafruit feather into the activated UART channels on the Pi.

This repository contains:

* Python code that uses standard Raspberry Pi software and Python packages. 
* The modified software serial library used on the FED3 devices. See [softwareSerial](https://github.com/matiasandina/FEDWatcher/tree/main/softwareSerial).
* Files to print the PCB we are using as a Raspberry Pi HAT for easier interface with the Raspberry Pi 4 pinout. 
* Python code for FEDWatcher GUI, which provides a way for the user to create projects and trigger FEDWatcher easily (see pic below).

![](https://github.com/matiasandina/FEDWatcher/blob/main/docs/img/gui.png?raw=true)

## Installation

If you already have an OS installed in your Rasberry Pi, [jump here](#edit-config). Otherwise continue reading.

To set up the Raspberry Pi, begin with flashing a standard image of Raspbian to an SD card. The project was coded and tested using Raspbian Lite with a Gnome Desktop and Raspbian Lite Buster, but any version of Raspbian should work.

For installing the operating system, the official Raspberry Pi Imager can be used. If you would like to install the Gnome desktop, the install will require that you have at least an 8GB SD card, the Pi plugged directly into a monitor, and a wifi or ethernet connection. 

### Gnome desktop

To use the Gnome desktop, first run

```
sudo raspi-config
```

Go into advanced options, select GL driver, install necessary packages if asked, and set the driver to fake KMS. Next, go back into advanced options and make sure you expand filesystem, as this is a large download. Then, back in bash, run

```
git clone https://github.com/TerraGitHuB/gnomeforpi.git && cd gnomeforpi && sudo bash gnomeforpi-install
```

This will take a long time. When the install is finished, the Raspberry Pi will reboot and you will be able to log into the Gnome desktop. In addition, the wifi will be disconnected, but you will be able to reconnect after logging in. After choosing your user and before entering your password, click the settings cog wheel under the password entry box and choose "Gnome for Xorg".

## Edit config

Next, you must enable the four hardware UARTs within the Raspberry Pi. Navigate to `/boot/` and edit `config.txt` however you prefer. This is an example using `nano`

```
sudo nano /boot/config.txt
``` 

At the end of the file, add on the following statements

```
force_eeprom_read=0
disable_poe_fan=1
dtoverlay=uart2
dtoverlay=uart3
dtoverlay=uart4
dtoverlay=uart5
```

> The first two lines disable the GPIO 0 and 1 functionality to be used for uart2. If you would like to use a hat or a POE fan with the Pi at the same time, remove the first three lines.

Now, you will be able to clone the FEDWatcher github repository into your project and use the functions within it to run your own programs.

---
## Hardware

### Arduino side

On the Arduino side of things, you should have a few modifications to your sketch

Use

```
#include "FED3.h"
```
This will make use of a local `FED3.h` file, instead of the installed FED3 library. We are currently trying to work out a way to merge FEDWatcher into the common FED3 library but for the time being you will need to use a local file.


Use `setSerial(true)` to enable FEDWatcher.

```
void setup() {
  fed3.begin();                                         //Setup the FED3 hardware
  fed3.DisplayPokes = false;                            //Customize the DisplayPokes option to 'false' to not display the poke indicators
  fed3.timeout = 3; //Set a timeout period (in seconds) after each pellet is taken
  
  // Turn to true if you are using FEDWatcher
  fed3.setSerial(true);
}
```

You can check the `sampleSketch` folder which has a free feeding example with 3 second inter trial interval (time between pellets).


### Pinout

To connect the FED3 devices to the Raspberry Pi, you will need a cable that takes the BNC female from the FED3 (old version) or a 3.5 mm male jack to fit the 3.5 mm female jack (new version) and ends to interface with the Raspberry Pi (see below). 

We have made custom cable using awg22 cable, BNC adapters, and male 3.5 mm jacks (see links below). If you are using the newer version of the FED3, any commercial stereo cable will work just fine.

For this program, up to four FED3 devices can be hooked up to a single Raspberry Pi. There are four activated UART ports with receivers at GPIO pins 1, 5, 9, and 13, corresponding to port1, port2, port3, port 4, in order. The unused send pins are located at 0, 4, 8, and 12. **These pins cannot be used while this program is running**. However, if not all ports are used, they can be disabled in the setup function. 

For this setup, the red/hot wire will go to one of the receiver post listed above, and the black/ground wire will go to any ground pin on the Raspberry Pi.

For more information on the pinout of the Raspberry pi visit the [Official Raspberry Documentation](https://www.raspberrypi.org/documentation/usage/gpio/). See below the official pinout for the Raspberry from the docs.

![image](https://user-images.githubusercontent.com/7494967/124830013-53691600-df47-11eb-8e53-1c78fbac09ee.png)

### Design of FEDWatcher HAT

We have also designed a little PCB board that sits on top of the RPi, so that it is easier for users to get started. This board was designed using KiCad 5.1 and 
relies on the following libraries (for footprints and parts):
- https://componentsearchengine.com/part-view/RASPBERRY%20PI%204B%20%2B%20Samtec%20ESP-120-33-G-D/RASPBERRY-PI

Here's how the PCB looks like

![FEDWatcher PCB](https://github.com/matiasandina/FEDWatcher/blob/main/hardware/RPi_shield/RPi_shield.png?raw=true)


There's a bit of soldering involved, but it makes things cleaner:

* Solder female pins to PCB to match Raspberry Pi's pinout.
* Solder female headphone jacks to PCB
* Solder male pins to match fan female connectors

These is how it looks like in our lab.

![fedwatcher-top](https://github.com/matiasandina/FEDWatcher/blob/main/docs/img/fedwatcher-top.jpg?raw=true) 
![fedwatcher-side](https://github.com/matiasandina/FEDWatcher/blob/main/docs/img/fedwatcher-side.jpg?raw=true)

The designs live on the [hardware](https://github.com/matiasandina/FEDWatcher/tree/main/hardware/RPi_shield) folder in this repository, where you can also find the bill of materials for the HAT.
There are a few generic parts that we recommend using, but similar parts should work.

* [Heat Sink and Fan](https://www.amazon.com/GeeekPi-Raspberry-Cooling-Aluminum-Heatsink/dp/B07PCMTZHF/ref=sr_1_3?crid=Q8C55QA09LS2&keywords=raspberry+pi+fan+aluminum+heatsink&qid=1659374343&sprefix=raspberry+pi+fan+aluminum+heatsink%2Caps%2C65&sr=8-3)
* [BNC adapter](https://www.amazon.com/Connector-Coaxial-Terminal-Adpater-Surveillance/dp/B091Z1V55J/ref=sr_1_22_sspa?crid=16I3NQ8L51GTH&keywords=bnc+adapter+wire&qid=1659374513&sprefix=bnc+adapters+wire,aps,61&sr=8-22-spons&psc=1)
* [M2.5 brass standoff](https://www.amazon.com/HanTof-Raspberry-Standoffs-Standoff-Cylinder/dp/B07KM27KC6/ref=pd_sbs_5/136-6686908-1264224?pd_rd_w=xld4t&pf_rd_p=0f56f70f-21e6-4d11-bb4a-bcdb928a3c5a&pf_rd_r=T61GBPY4VQAJ1AG9K1SB&pd_rd_r=d5b09aac-2d40-4798-8f3f-64e0f1895e47&pd_rd_wg=2Fxwf&pd_rd_i=B07KM27KC6&psc=1)


## Contribute

This is a primary release, please file [issues](https://github.com/matiasandina/FEDWatcher/issues) to contribute to this project.




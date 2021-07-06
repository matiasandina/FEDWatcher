# Fedwatch
Fedwatch is a program for a Raspberry Pi 4 to connect to up to 4 FED3 feeder devices from KravitzLabDevices. The code is written in Python and using standard Raspberry Pi software and Python packages. This repository also contains the software serial library used on the FED3 devices

The Raspberry Pi communicates with the FED3 devices using software serial from the BNC port of the Adafruit feather into one of the four activated UART channels on the Pi.

## Installation
To set up the Raspberry Pi, begin with flashing a standard image of Raspbian to an SD card. The project was coded and tested using Raspbian Lite with a Gnome Desktop, but any version of Raspbian should work.

For installing the operating system, the official Raspberry Pi Imager can be used. If you would like to install the Gnome desktop, the install will require that you have at least an 8GB SD card, the pi plugged directly into a monitor, and a wifi or ethernet connection. first run

>sudo raspi-config

Go into advanced options, select GL driver, install necessary packages if asked, and set the driver to fake KMS. Next, go back into advanced options and make sure you expand filesystem, as this is a large download. Then, back in bash, run

>git clone https://github.com/TerraGitHuB/gnomeforpi.git && cd gnomeforpi && sudo bash gnomeforpi-install

This will take a long time. When the install is finished, the Raspberry Pi will reboot and you will be able to log into the Gnome desktop. In addition, the wifi will be disconnected, but you will be able to reconnect after logging in. After choosing your user and before entering your password, click the settings cog wheel under the password entry box and choose "Gnome for Xorg".

Now, you will be able to clone the Fedwatch github repository into your project and use the functions within it to run your own programs.

## Pinout
To connect the FED3 devices to the Raspberry Pi, you will need some kind of cable that takes the BNC female from the FED3 and ends in bare wires to interface with the Raspberry Pi. You can find this by googling BNC to wire leads or if desired, BNC to alligator clips. For this program, up to four FED3 devices can be hooked up to a single Raspberry Pi. There are four activated UART ports with receivers at pins 1, 5, 9, and 13, corresponding to port1, port2, port3, port 4, in order. The unused send pins are located at 0, 4, 8, and 12. These pins cannot be used while this program is running. However, if not all ports are used, they can be disabled in the setup function.
# linkbot-firmware-updater

The linkbot-firmware-updater is a tool used to update the firmware of a Barobo [Linkbot](http://linkbotlabs.com). Typically, Linkbots are updating through the Linkbot Labs environment. However, there are some older computer systems that may not be able to run the full version of Linkbot Labs. For those systems, this utility can be used to update the firmware of Linkbots.

This software first checks to see if Linkbot Labs is installed and tries to update Linkbots to the version provided by Linkbot Labs. If Linkbot Labs is not installed, it falls back to the version of firmware that comes with the updater.

## Requirements

The firmware updater requires the program `avrdude` to be installed. For Ubuntu or Raspbian systems, the utility can be installed with the command

    sudo apt-get install avrdude

The user running the utility will also need to be a member of the "dialout" group (as well as the "gpio" group for Raspbian). To add a user to these groups, use the commands

    sudo usermod -G dialout $USER
    sudo usermod -G gpio $USER # Required only for Raspbian

## Installation

The linkbot-firmware-updater is hosted by barobo. To install it using pip or easy_install, use the command

    sudo easy_install3 --upgrade --index-url=http://barobo.com:8080/simple/ linkbot-firmware-updater
  
or

    sudo pip3 install --upgrade --index-url=http://barobo.com:8080/simple/ linkbot-firmware-updater

## Running the updater

To start the updater utility, type the command

    linkbot-firmware-updater

on a terminal command line. A dialog window will appear guiding you through the rest of the process.


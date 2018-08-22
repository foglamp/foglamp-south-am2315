********************************
FogLAMP South Enviro Phat Plugin
********************************

This directory contains a plugin that pulls readings from Enviro pHAT sensor.
Enviro pHAT is an environmental sensing board that lets you measure temperature,
pressure, light, colour, motion and analog sensors.

The polling is done at fixed intervals which is configurable via "pollInterval"
configuration item.

All sensors can be enabled/disabled separately vide setting suitable configuration
parameters. All sensors can also be named as desired vide setting suitable
configuration parameters.

Installing the software:
========================
It is always recommended using the most up-to-date version of Raspbian, and it
often helps to start with a completely fresh install of Raspbian, although this isn't
necessary.

Please use an easy one-line-installer to get your Enviro pHAT set up. We'd suggest that
you use this method to install the Enviro pHAT software.

Open a new terminal, and type the following, making sure to type 'y' or 'n' when prompted:

           curl https://get.pimoroni.com/envirophat | bash

Once that's done, it's probably a good idea to reboot your Pi to let the changes propagate.

For more help, please visit https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-enviro-phat.


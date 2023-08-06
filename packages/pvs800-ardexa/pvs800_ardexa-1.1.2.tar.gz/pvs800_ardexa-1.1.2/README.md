# Purpose
ABB supply retail and grid grade Solar PV inverters. The purpose of this project is to collect data from ABB PVS 800 Inverters and send the data to your cloud using Ardexa. Data from ABB PVS 800 solar inverters is read using an Ethernet connection using Modbus RTU (over Ethernet) and a Linux device such as a Raspberry Pi, or an X86 intel powered computer. 

# How does it work
This application is written in Python. This application will query 1 or more connected inverters at regular intervals. Data will be written to log files on disk in a directory specified by the user. Usage and command line parameters are shown below.

## Install
On a raspberry Pi, or other Linux machines (arm, intel, mips or whetever), make sure Python is installed (which it should be). Then install the package as follows:
```
sudo pip install pvs800_ardexa
```

## Usage
To discover RS485 address range and print out the inverter metadata
```
Usage: pvs800_ardexa discover IP_address Port RS485 Addresses
Eg; pvs800_ardexa discover 192.168.1.3 502 1-5 
```

Send production data to a file on disk 
```
Usage: pvs800_ardexa get IP_address port bus_addresses output_directory
Eg; pvs800_ardexa log 192.168.1.3 502 1-4 /opt/ardexa
```
- IP Address = ..something like: 192.168.1.4
- Bus Addresses = List of bus addresses using commas and hyphens, e.g. `1-4,6,10-20` (this is an RS485 address, NOT Ethernet). 
- ouput directory = logging directory; eg; /opt/logging/

To view debug output, increase the verbosity using the `-v` flag.
- standard (no messages, except errors), `-v` (discovery messages) or `-vv` (all messages)


## Collecting to the Ardexa cloud
Collecting to the Ardexa cloud is free for up to 3 x Raspberry Pis (or equivalent). Ardexa provides free agents for ARM, Intel x86 and MIPS based processors. To collect the data to the Ardexa cloud do the following:
- Create a `RUN` scenario to schedule the Ardexa PVS 800 script to run at regular intervals (say every 300 seconds/5 minutes).
- Then use a `CAPTURE` scenario to collect the csv (comma separated) data from the filename (say) `/opt/ardexa/logs/`. This file contains a header entry (as the first line) that describes the CSV elements of the file.

## Help
Contact Ardexa at support@ardexa.com, and we'll do our best efforts to help.

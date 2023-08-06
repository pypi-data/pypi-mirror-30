"""
This script will query a single PVS800 inverters.
Usage: python kostal-ardexa.py ip_address start_address end_address log_directory
Eg; python kostal-ardexa.py 192.168.1.3 1 4 /opt/ardexa RUNTIME 0
{IP Address} = IP address of the inverter, eg; 192.168.1.4
{Port} = Modbus port of the inverter, eg; 502
{RS485 Address(es)} = RS485 address or range of addresses, eg; 1-5 or 1,2,3 or 4 (for example)
{log directory} = logging directory, eg; /opt/logging/
{type of query} = RUNTIME
{debug type} = 0 (no messages, except errors), 1 (discovery messages) or 2 (all messages)
    DEBUG = 0 ; No Debug information
    DEBUG = 1 ; Important Debug information
    DEBUG = 2 ; ALL Debug information
"""

# Copyright (c) 2018 Ardexa Pty Ltd
#
# This code is licensed under the MIT License (MIT).
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from __future__ import print_function
import sys
import time
import os
from subprocess import Popen, PIPE
import click
import ardexaplugin as ap

PY3K = sys.version_info >= (3, 0)

# Status codes for the PVS800 Inverter
STATUS_CODES = {"1" : "STANDBY", "2" : "SLEEP", "3" : "START ISU", "4" : "MPPT", "5" : "ISU LOCAL", "6" : "FAULTED", "7" : "Q POWER"}
PIDFILE = 'pvs800-ardexa.pid'
START_REG = "1"
REGS_TO_READ = "51"



def write_line(line, ip_address, inverter_addr, base_directory, header_line, debug):
    """This will write a line to the base_directory
    Assume header and lines are already \n terminated"""
    # Write the log entry, as a date entry in the log directory
    date_str = (time.strftime("%Y-%b-%d"))
    log_filename = date_str + ".csv"
    log_directory = os.path.join(base_directory, ip_address)
    log_directory = os.path.join(log_directory, inverter_addr)
    ap.write_log(log_directory, log_filename, header_line, line, debug, True, log_directory, "latest.csv")

    return True


def read_inverter(ip_address, port, rtu_address, debug):
    """Get the inverter data"""
    # initialise stdout and stderr to NULL
    stdout = ""
    stderr = ""
    retval = True
    register_dict = {}

    # These commands are used to get the parameters from the inverters. There's needs to be 3 separate comnmand issued
    # modpoll -m enc -a {rtu address} -r {start reg} -c {regs to read} -t 4:float -1 -4 10 -b {BAUD} {device}
    # Example: modpoll -a 7 -r 104 -c 10 -1 -p 501 192.168.1.1
    ps = Popen(['modpoll', '-a', rtu_address, '-r', '104', '-c', '10', '-1', '-p', port, ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()

    # Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
    if debug >= 2:
        print("STDOUT: ", stdout)
        print("STDERR: ", stderr)

    # for each line, split the register and return values
    for line in stdout.splitlines():
        # if the line starts with a '[', then process it
        if line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', '')
            register, value = line.split(':')
            register = register.strip()
            value = value.strip()
            register_dict[register] = value


    # modpoll -m enc -a {rtu address} -r {start reg} -c {regs to read} -t 4:float -1 -4 10 -b {BAUD} {device}
    # Example: modpoll -a 7 -r 118 -c 12 -1 -p 502 192.168.1.1
    ps = Popen(['modpoll', '-a', rtu_address, '-r', '118', '-c', '12', '-1', '-p', port, ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()

    # Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
    if debug >= 2:
        print("STDOUT: ", stdout)
        print("STDERR: ", stderr)

    # for each line, split the register and return values
    for line in stdout.splitlines():
        # if the line starts with a '[', then process it
        if line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', '')
            register, value = line.split(':')
            register = register.strip()
            value = value.strip()
            register_dict[register] = value


    # modpoll -m enc -a {rtu address} -r {start reg} -c {regs to read} -t 4:float -1 -4 10 -b {BAUD} {device}
    # Example: modpoll -a 7 -r 301 -c 16 -1 -p 502 192.168.1.1
    ps = Popen(['modpoll', '-a', rtu_address, '-r', '301', '-c', '16', '-1', '-p', port, ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()

    # Modpoll will send the data to stderr, but also send errors on stderr as well. weird.
    if debug >= 2:
        print("STDOUT: ", stdout)
        print("STDERR: ", stderr)

    # for each line, split the register and return values
    for line in stdout.splitlines():
        # if the line starts with a '[', then process it
        if line.startswith('['):
            line = line.replace('[', '')
            line = line.replace(']', '')
            register, value = line.split(':')
            register = register.strip()
            value = value.strip()
            register_dict[register] = value

    vac1 = vac2 = vac3 = iac1 = iac2 = iac3 = pac = freq = cosphi = ""
    idc = pdc = temp = status = alarm = fault = total_energy = ""
    idc_string1 = idc_string2 = idc_string3 = idc_string4 = idc_string5 = idc_string6 = idc_string7 = idc_string8 = ""
    idc_string9 = idc_string10 = idc_string11 = idc_string12 = idc_string13 = idc_string14 = idc_string15 = idc_string16 = ""

    count = 0
    # Get Parameters. If there are 0 parameters, then report an error
    # Otherwise accept the line
    if "104" in register_dict:
        vac1 = register_dict["104"]
        count += 1
    if "105" in register_dict:
        vac2 = register_dict["105"]
        count += 1
    if "106" in register_dict:
        vac3 = register_dict["106"]
        count += 1
    if "107" in register_dict:
        iac1 = register_dict["107"]
        count += 1
    if "108" in register_dict:
        iac2 = register_dict["108"]
        count += 1
    if "109" in register_dict:
        iac3 = register_dict["109"]
        count += 1
    if "110" in register_dict:
        pac_raw = register_dict["110"]
        pac, result = ap.convert_to_float(pac_raw)
        if result:
            pac = pac * 100 # Multiply by 100 to get W
            count += 1
    if "112" in register_dict:
        freq_raw = register_dict["112"]
        freq, result = ap.convert_to_float(freq_raw)
        if result:
            freq = freq / 100 # Divide by 100
            count += 1
    if "113" in register_dict:
        cosphi_raw = register_dict["113"]
        cosphi, result = ap.convert_to_float(cosphi_raw)
        if result:
            cosphi = cosphi / 100 # Divide by 100
            count += 1
    if "118" in register_dict:
        idc = register_dict["118"]
        count += 1
    if "119" in register_dict:
        pdc_raw = register_dict["119"]
        pdc, result = ap.convert_to_float(pdc_raw)
        if result:
            pdc = pdc * 1000 # Multiply by 1000 to get W
            count += 1
    if "120" in register_dict:
        temp = register_dict["120"]
        count += 1
    if "121" in register_dict:
        status = register_dict["121"]
        if status in STATUS_CODES:
            status = STATUS_CODES[status]
        count += 1
    if "122" in register_dict:
        fault = register_dict["122"]
        count += 1
    if "123" in register_dict:
        alarm = register_dict["123"]
        count += 1

    # Total energy is calculated using 3 values as follows
    if ("127" in register_dict) and (("128" in register_dict)) and (("129" in register_dict)):
        overall = True
        energy_kwh_raw = register_dict["127"]
        energy_kwh, result = ap.convert_to_float(energy_kwh_raw)
        if not result:
            overall = False
        energy_mwh_raw = register_dict["128"]
        energy_mwh, result = ap.convert_to_float(energy_mwh_raw)
        if not result:
            overall = False
        energy_gwh_raw = register_dict["129"]
        energy_gwh, result = ap.convert_to_float(energy_gwh_raw)
        if not result:
            overall = False
        if overall:
            total_energy = (1000000*energy_gwh) + (1000*energy_mwh) + energy_kwh

    # These are all the string values
    if "301" in register_dict:
        idc_string1 = register_dict["301"]
        count += 1
    if "302" in register_dict:
        idc_string2 = register_dict["302"]
        count += 1
    if "303" in register_dict:
        idc_string3 = register_dict["303"]
        count += 1
    if "304" in register_dict:
        idc_string4 = register_dict["304"]
        count += 1
    if "305" in register_dict:
        idc_string5 = register_dict["305"]
        count += 1
    if "306" in register_dict:
        idc_string6 = register_dict["306"]
        count += 1
    if "307" in register_dict:
        idc_string7 = register_dict["307"]
        count += 1
    if "308" in register_dict:
        idc_string8 = register_dict["308"]
        count += 1
    if "309" in register_dict:
        idc_string9 = register_dict["309"]
        count += 1
    if "310" in register_dict:
        idc_string10 = register_dict["310"]
        count += 1
    if "311" in register_dict:
        idc_string11 = register_dict["311"]
        count += 1
    if "312" in register_dict:
        idc_string12 = register_dict["312"]
        count += 1
    if "313" in register_dict:
        idc_string13 = register_dict["313"]
        count += 1
    if "314" in register_dict:
        idc_string14 = register_dict["314"]
        count += 1
    if "315" in register_dict:
        idc_string15 = register_dict["315"]
        count += 1
    if "316" in register_dict:
        idc_string16 = register_dict["316"]
        count += 1

    if count < 1:
        retval = False

    if debug > 0:
        print("For inverter at IP address: " + ip_address + " and RTU Address: " + rtu_address)
        print("\tAC Voltage 1 (V): ", vac1)
        print("\tAC Voltage 2 (V): ", vac2)
        print("\tAC Voltage 3 (V): ", vac3)
        print("\tAC Current 1 (V): ", iac1)
        print("\tAC Current 2 (V): ", iac2)
        print("\tAC Current 3 (V): ", iac3)
        print("\tAC Power (W): ", pac)
        print("\tGrid Frequency (Hz): ", freq)
        print("\tPower Factor: ", cosphi)
        print("\tDC Current (A): ", idc)
        print("\tDC Power (W): ", pdc)
        print("\tInverter Temperature (C): ", temp)
        print("\tStatus: ", status)
        print("\tFault: ", fault)
        print("\tAlarm: ", alarm)
        print("\tTotal Energy (kWh): ", total_energy)
        print("\tString Current 1 (A): ", idc_string1)
        print("\tString Current 2 (A): ", idc_string2)
        print("\tString Current 3 (A): ", idc_string3)
        print("\tString Current 4 (A): ", idc_string4)
        print("\tString Current 5 (A): ", idc_string5)
        print("\tString Current 6 (A): ", idc_string6)
        print("\tString Current 7 (A): ", idc_string7)
        print("\tString Current 8 (A): ", idc_string8)
        print("\tString Current 9 (A): ", idc_string9)
        print("\tString Current 10 (A): ", idc_string10)
        print("\tString Current 11 (A): ", idc_string11)
        print("\tString Current 12 (A): ", idc_string12)
        print("\tString Current 13 (A): ", idc_string13)
        print("\tString Current 14 (A): ", idc_string14)
        print("\tString Current 15 (A): ", idc_string15)
        print("\tString Current 16 (A): ", idc_string16)

    datetime_str = ap.get_datetime_str()

    header = "# Datetime, AC Voltage 1 (V), AC Voltage 2 (V), AC Voltage 3 (V), AC Current 1 (A), AC Current 2 (A), AC Current 3 (A), AC Power (W), Grid Frequency (Hz), Power Factor, DC Current (A), DC Power (W), Temperature (C), Status, Alarm, Fault, Energy total (kWh), String Current 1 (A), String Current 2 (A), String Current 3 (A), String Current 4 (A), String Current 5 (A), String Current 6 (A), String Current 7  (A),String Current 8 (A), String Current 9 (A), String Current 10 (A), String Current 11 (A), String Current 12 (A), String Current 13 (A), String Current 14 (A), String Current 15 (A),String Current 16 (A)\n"

    output_str = datetime_str + "," +  str(vac1) + "," + str(vac2) + "," + str(vac3) + "," + str(iac1) + "," + str(iac2) + "," \
                  + str(iac3) + "," + str(pac) + "," + str(freq) + "," + str(cosphi) + "," + str(idc) + "," + str(pdc) + "," \
                  + str(temp) + "," + str(status) + "," + str(alarm) + "," + str(fault) + "," + str(total_energy) + "," \
                  + str(idc_string1) + "," + str(idc_string2) + "," + str(idc_string3) + "," + str(idc_string4) + "," \
                  + str(idc_string5) + "," + str(idc_string6) + "," + str(idc_string7) + "," + str(idc_string8) + "," \
                  + str(idc_string9) + "," + str(idc_string10) + "," + str(idc_string11) + "," + str(idc_string12) + "," \
                  + str(idc_string13) + "," + str(idc_string14) + "," + str(idc_string15) + "," + str(idc_string16) + "\n"

    # return the header and output
    return header, output_str, retval


class Config(object):
    """Config object for click"""
    def __init__(self):
        self.verbosity = 0


CONFIG = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('-v', '--verbose', count=True)
@CONFIG
def cli(config, verbose):
    """Command line entry point"""
    config.verbosity = verbose


@cli.command()
@click.argument('ip_address')
@click.argument('port')
@click.argument('bus_addresses')
@CONFIG
def discover(config, ip_address, port, bus_addresses):
    """Connect to the target IP address and run a scan of 485 addresses"""
    # Check that no other scripts are running
    pidfile = os.path.join("/tmp", PIDFILE)
    if ap.check_pidfile(pidfile, config.verbosity):
        print("This script is already running")
        sys.exit(4)

    start_time = time.time()

    # This will check each inverter. If a bad line is received, it will try one more time
    for inverter_addr in ap.parse_address_list(bus_addresses):
        time.sleep(1) # ... wait between reads
        # First get the inverter parameter data
        header, line, retval = read_inverter(ip_address, port, str(inverter_addr), config.verbosity)
        if retval:
            print("Found inverter at IP Address: ", ip_address, " and RS485 address: ", inverter_addr)
            if config.verbosity > 0:
                print("Header: ", header)
                print("Line: ", line)
        else:
            print("NO inverter/not responding at IP Address: ", ip_address, " and RS485 address: ", inverter_addr)

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")

    # Remove the PID file
    if os.path.isfile(pidfile):
        os.unlink(pidfile)


@cli.command()
@click.argument('ip_address')
@click.argument('port')
@click.argument('bus_addresses')
@click.argument('output_directory')
@CONFIG
def get(config, ip_address, bus_addresses, output_directory, port):
    """Connect to the target IP address and log the inverter output for the given bus addresses"""
    # If the logging directory doesn't exist, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Check that no other scripts are running
    pidfile = os.path.join(output_directory, PIDFILE)
    if ap.check_pidfile(pidfile, config.verbosity):
        print("This script is already running")
        sys.exit(4)

    start_time = time.time()

    # This will check each inverter. If a bad line is received, it will try one more time
    for inverter_addr in ap.parse_address_list(bus_addresses):
        time.sleep(1) # ... wait between reads
        # First get the inverter parameter data
        header, line, retval = read_inverter(ip_address, port, str(inverter_addr), config.verbosity)
        if retval:
            # Write the log entry, as a date entry in the log directory
            write_line(line, ip_address, str(inverter_addr), output_directory, header, config.verbosity)

    elapsed_time = time.time() - start_time
    if config.verbosity > 0:
        print("This request took: ", elapsed_time, " seconds.")

    # Remove the PID file
    if os.path.isfile(pidfile):
        os.unlink(pidfile)

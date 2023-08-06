# coding=utf-8

from logging import getLogger
from os import makedirs
from os.path import exists, join

from fabric.api import env, run, get
from file_read_backwards import FileReadBackwards
from numpy import arange
from pandas import read_csv

from ..configuration.configuration import Configuration
from ..utils.utils import custom_exit

# Create the logger
logger = getLogger(__name__)
# Get the instance of Configuration
cf = Configuration.get_instance()


def collect_data():
    """
    Collect stats from the host system
    :return:
    """
    # Additional arguments for formatting the output
    base_command = "LC_ALL=C nohup sar {0} {1} | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+{2}' | tr ',' '.' | tr -s ' ' ' '" \
                   " > {3}"
    # Create a list where to store the commands
    commands = []
    for hw in cf.hardware:
        # Create the RAW dir
        raw_dir_path = join("/tmp/raw", hw)
        # Build the command depending on the hardware
        egrep_args = ""
        if hw == "cpu":
            egrep_args = 'all'
        elif hw in ["memory", "swap"]:
            egrep_args = '[0-9]'
        elif hw in ["disk", "network"]:
            devices = cf.filesystem_names if hw == "disk" else cf.net_interfaces
            if devices is None:
                logger.warn("No devices specified, aborting {} data collection".format(hw))
                return
            if (type(devices) is list) or (type(devices) is set) or (type(devices) is tuple):
                egrep_args = "({})".format("|".join(devices))
            elif type(devices) is str:
                egrep_args = devices
            else:
                logger.warn("Aborting the data collection! Expected type(devices)=list|set|tuple|str "
                            "Actual type(devices)={1}!".format(type(devices)))
                return
        else:
            # Throw an error message and exit
            logger.error("Aborting the data collection. Expected hardware=cpu|memory|swap|disk|network"
                         " Actual hardware={}".format(hw))
            custom_exit(-7)
        # Creating the output file path
        command = base_command.format(cf.sar_args[hw], cf.interval, egrep_args, join(raw_dir_path, env.host_string))
        commands.append(command)
    # Creating the commands
    rm_command = "rm -rf /tmp/raw"
    mkdir_command = "mkdir -p /tmp/raw/{}".format("{" + ",".join(cf.hardware) + "}")
    final_command = "{0}; {1}; {2} &".format(rm_command, mkdir_command, " & ".join(commands))
    logger.info("[{0}] {1}".format(env.host_string, final_command))
    run(final_command, pty=False)


def kill_process(process_name):
    """
    Kill processes using their name
    :param process_name: Process' name
    :return:
    """
    command = "pkill -f {}".format(process_name)
    logger.info("[{0}] {1}".format(env.host_string, command))
    run(command, pty=False)


def download_data(remote_path, local_path):
    """
    Download collected data
    :param remote_path: The remote path to download data from
    :param local_path: The local path to download data to
    :return:
    """
    logger.info("[localhost] scp -r {0}:{1} {2}".format(env.host_string, remote_path, local_path))
    get(remote_path, local_path)


def parse_data(hw=None):
    """
    Parse the data of a given hardware monitoring output
    :param hw: Type of hardware (cpu, memory, swap, disk, network)
    :return: 
    """
    # Check if hardware is not None
    if type(hw) is not str:
        logger.warn("Aborting the data parsing! Expected type(hardware)=str "
                    "Actual type(hardware)={}!".format(type(hw)))
        return
    
    # Check if hardware's value is valid
    if hw not in cf.hardware:
        logger.warn("Aborting the data parsing! Expected hardware=cpu|memory|swap|disk|network "
                    "Actual hardware={}!".format(hw))
        return
    
    # Create the parsed directory
    raw_dir_path = join(cf.output_dir, 'raw')
    if exists(raw_dir_path) is False:
        logger.error("Aborting the data parsing! Can't find the raw directory : {}.".format(raw_dir_path))
        custom_exit(-8)
    
    # Logging
    logger.info("Parsing {} data".format(hw))
    
    # Managing the directories
    raw_dir_path = join(raw_dir_path, hw)
    parsed_dir_path = join(cf.output_dir, 'parsed', hw)
    if exists(parsed_dir_path) is False:
        makedirs(parsed_dir_path)
        
    # Get the min time in all files
    min_time = "00:00:00"
    for host in cf.hosts:
        # Read the file line by line
        with open(join(cf.output_dir, "raw", hw, host)) as f:
            for line_number, line in enumerate(f):
                # Only the second line since the first line is the header line
                if line_number == 1:
                    line_time = line.strip().split()[0]
                    min_time = line_time if line_time > min_time else min_time

    # Get the max time in all files
    max_time = "23:59:59"
    for host in cf.hosts:
        # Read the file backwards line by line
        f = FileReadBackwards(join(cf.output_dir, "raw", hw, host))
        last_line = True
        for line in f:
            try:
                if last_line is True:
                    last_line = False
                    continue
                line_time = line.strip().split()[0]
                max_time = line_time if line_time < max_time else max_time
                # Break because we only need the value of the last line
                break
            except IndexError:
                continue
    
    # Loop through all the hosts
    for host in cf.hosts:
        # Loading the data
        parsed_file_path = join(parsed_dir_path, host)
        hardware_df = read_csv(filepath_or_buffer=join(raw_dir_path, host), header=None, names=cf.raw_columns[hw],
                               delim_whitespace=True, index_col=False)
        
        # Deleting all rows with time < min time
        for index, row in hardware_df.iterrows():
            if row['time'] < min_time:
                hardware_df = hardware_df.drop(index)
            else:
                break

        # Deleting all rows with time > max time
        last_line = True
        for index, row in hardware_df.iloc[::-1].iterrows():
            if last_line is True:
                # Fix for sar output since it can be truncated and lead to issues with pandas
                hardware_df = hardware_df.drop(index)
                last_line = False
                continue
            if row['time'] > max_time:
                hardware_df = hardware_df.drop(index)
            else:
                break
        
        # Removing all the non-relevant columns
        hardware_df = hardware_df[cf.relevant_columns[hw]]
        # Fix for the time. Convert the column values into integers instead of parsing the time.
        hardware_df.loc[:, 'time'] = arange(0, len(hardware_df) * cf.interval, cf.interval)
        # Rename the columns name
        hardware_df.rename(index=str, columns=cf.renamed_columns[hw], inplace=True)
        
        if hw == 'cpu':
            hardware_df['%util'] = 100.0 - hardware_df['%i/o_wait'] - hardware_df['%idle']
            hardware_df = hardware_df.drop('%idle', axis=1)
        elif hw == 'memory':
            # Convert the values from KB to MB
            hardware_df['memory_used_mb'] /= 1024
        elif hw == 'swap':
            # Convert the values from KB to MB
            hardware_df['swap_used_mb'] /= 1024
        elif hw == 'disk':
            if cf.filesystem_names is not None:
                # Convert the values from Sector to MB
                hardware_df['read_mb/s'] = hardware_df['read_mb/s'] * 512 / float(1024 * 1024)
                hardware_df['write_mb/s'] = hardware_df['write_mb/s'] * 512 / float(1024 * 1024)
                for device in cf.filesystem_names:
                    device_df = hardware_df[hardware_df['device'] == device]
                    # No need for the device column
                    device_df = device_df.drop('device', axis=1)
                    # Update the time column
                    device_df.loc[:, "time"] = arange(0, len(device_df) * cf.interval, cf.interval)
                    # Export data to csv
                    device_df.to_csv("{0}.{1}".format(parsed_file_path, device), sep=' ', index=False)
        else:
            if cf.net_interfaces is not None:
                hardware_df['read_mb/s'] /= 1024
                hardware_df['transmitted_mb/s'] /= 1024
                for device in cf.net_interfaces:
                    device_df = hardware_df[hardware_df['interface'] == device]
                    # No need for the interface column
                    device_df = device_df.drop('interface', axis=1)
                    # Update the time column
                    device_df.loc[:, 'time'] = arange(0, len(device_df) * cf.interval, cf.interval)
                    # Export data to csv
                    device_df.to_csv("{0}.{1}".format(parsed_file_path, device), sep=' ', index=False)
        # Export data to csv file
        if hw not in ['disk', 'network']:
            hardware_df.to_csv(parsed_file_path, sep=' ', index=False)


def plot_data(hw=None):
    """
    Plot the data given the hardware.
    :param hw: Type of hardware (cpu, memory, swap, disk, network)
    :return: 
    """
    # Check if hardware is not None
    if type(hw) is not str:
        logger.warn("Aborting the data plotting! Expected type(hardware)=str "
                    "Actual type(hardware)={}!".format(type(hw)))
        return
    
    # Check if hardware's value is valid
    if hw not in cf.hardware:
        logger.warn("Aborting the data plotting! Expected hardware=cpu|memory|swap|disk|network "
                    "Actual hardware={}!".format(hw))
        return
    
    # Check if the parsed directory exists
    parsed_dir_path = join(cf.output_dir, 'parsed')
    if exists(parsed_dir_path) is False:
        logger.error("Aborting the data plotting! Can't find the parsed directory : {}".format(parsed_dir_path))
        custom_exit(-9)
    
    # Check if the parsed directory of the specific hardware exists
    parsed_dir_path = join(parsed_dir_path, hw)
    if exists(parsed_dir_path) is False:
        logger.error(
            "Aborting the {0} data plotting! Can't find the parsed directory : {1}".format(hw, parsed_dir_path))
        return
    
    # Logging
    logger.info("Plotting {} data".format(hw))
    
    # Managing directories
    plot_dir_path = join(cf.output_dir, 'plot', hw)
    if exists(plot_dir_path) is False:
        makedirs(plot_dir_path)

    from itertools import cycle
    # Import matplotlib
    import matplotlib
    # Change the backend used by matplotlib (plotting without running X server)
    matplotlib.use("agg")
    # Import pyplot
    import matplotlib.pyplot as plt
    # Use a seaborn-like style
    plt.style.use('seaborn-whitegrid')

    white_color_int_representation = int('FFFFFF', 16)
    colors_hex = ['#{0:06X}'.format(int(white_color_int_representation / len(cf.hosts) * i)) for i in range(20)]

    # List files in parsed directory
    if hw == 'cpu':
        iowait_plot = plt.figure()
        utilization_plot = plt.figure()

        ax_iowait = iowait_plot.add_subplot(111)
        ax_utilization = utilization_plot.add_subplot(111)

        ax_iowait.set_title("CPU I/O wait")
        ax_utilization.set_title("CPU Utilization")

        ax_iowait.set_xlabel("Total execution time (s)")
        ax_utilization.set_xlabel("Total execution time (s)")

        ax_iowait.set_ylabel("I/O wait (%)")
        ax_utilization.set_ylabel("CPU utilization (%)")

        colors = cycle(colors_hex)

        for host in cf.hosts:
            # Replace the host string by the alias
            try:
                if host in cf.aliases['hosts'].keys():
                    host_alias = cf.aliases['hosts'][host]
                else:
                    host_alias = host
            except KeyError:
                host_alias = host

            hardware_df = read_csv(filepath_or_buffer=join(parsed_dir_path, host), delim_whitespace=True,
                                   index_col=False, dtype=cf.columns_dtype[hw])
            
            color = next(colors)

            ax_iowait.plot(hardware_df['time'], hardware_df['%i/o_wait'], color=color, label=host_alias)
            ax_utilization.plot(hardware_df['time'], hardware_df['%util'], color=color, label=host_alias)

        ax_iowait.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True, shadow=True)
        ax_utilization.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True,
                              shadow=True)

        # Save the figures
        logger.info("Plotting CPU I/O wait data")
        iowait_plot.savefig(join(plot_dir_path, 'iowait.eps'), format='eps', dpi=1500, bbox_inches="tight")
        logger.info("Plotting CPU utilization data")
        utilization_plot.savefig(join(plot_dir_path, 'utilization.eps'), format='eps', dpi=1500, bbox_inches="tight")

    elif hw == 'memory':
        utilization_plot = plt.figure()

        ax_utilization = utilization_plot.add_subplot(111)

        ax_utilization.set_title("Memory utilization (MB/s)")

        ax_utilization.set_xlabel("Total execution time (s)")

        ax_utilization.set_ylabel("Memory utilization (MB)")

        colors = cycle(colors_hex)

        for host in cf.hosts:
            # Replace the host string by the alias
            try:
                if host in cf.aliases['hosts'].keys():
                    host_alias = cf.aliases['hosts'][host]
                else:
                    host_alias = host
            except KeyError:
                host_alias = host

            hardware_df = read_csv(filepath_or_buffer=join(parsed_dir_path, host), delim_whitespace=True,
                                   index_col=False, dtype=cf.columns_dtype[hw])
            
            color = next(colors)

            ax_utilization.plot(hardware_df['time'], hardware_df['memory_used_mb'], color=color, label=host_alias)

        ax_utilization.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True,
                              shadow=True)

        # Save the figures
        logger.info("Plotting memory utilization data")
        utilization_plot.savefig(join(plot_dir_path, 'utilization.eps'), format='eps', dpi=1500, bbox_inches="tight")

    elif hw == 'swap':
        utilization_plot = plt.figure()

        ax_utilization = utilization_plot.add_subplot(111)

        ax_utilization.set_title("Swap utilization (MB/s)")

        ax_utilization.set_xlabel("Total execution time (s)")

        ax_utilization.set_ylabel("Swap utilization (MB)")

        colors = cycle(colors_hex)

        for host in cf.hosts:
            # Replace the host string by the alias
            try:
                if host in cf.aliases['hosts'].keys():
                    host_alias = cf.aliases['hosts'][host]
                else:
                    host_alias = host
            except KeyError:
                host_alias = host

            hardware_df = read_csv(filepath_or_buffer=join(parsed_dir_path, host), delim_whitespace=True,
                                   index_col=False, dtype=cf.columns_dtype[hw])

            color = next(colors)

            ax_utilization.plot(hardware_df['time'], hardware_df['swap_used_mb'], color=color, label=host_alias)

        ax_utilization.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True,
                              shadow=True)

        # Save the figures
        logger.info("Plotting swap utilization data")
        utilization_plot.savefig(join(plot_dir_path, 'utilization.eps'), format='eps', dpi=1500, bbox_inches="tight")

    elif hw == 'disk':
        for device in cf.filesystem_names:
            # Replace the host string by the alias
            try:
                if device in cf.aliases['filesystem_names'].keys():
                    device_alias = cf.aliases['filesystem_names'][device]
                else:
                    device_alias = device
            except KeyError:
                device_alias = device

            # Each device has its own plot
            # Read MB/s plot
            read_plot = plt.figure()
            write_plot = plt.figure()
            utilization_plot = plt.figure()

            ax_read = read_plot.add_subplot(111)
            ax_write = write_plot.add_subplot(111)
            ax_utilization = utilization_plot.add_subplot(111)

            ax_read.set_title("{} : read".format(device_alias))
            ax_write.set_title("{} : write".format(device_alias))
            ax_utilization.set_title("{} : utilization".format(device_alias))

            ax_read.set_xlabel("Total execution time (s)")
            ax_write.set_xlabel("Total execution time (s)")
            ax_utilization.set_xlabel("Total execution time (s)")

            ax_read.set_ylabel("Read (MB)")
            ax_write.set_ylabel("Write (MB)")
            ax_utilization.set_ylabel("Utilization (%)")

            colors = cycle(colors_hex)

            for host in cf.hosts:
                # Replace the host string by the alias
                try:
                    if host in cf.aliases['hosts'].keys():
                        host_alias = cf.aliases['hosts'][host]
                    else:
                        host_alias = host
                except KeyError:
                    host_alias = host

                hardware_df = read_csv(filepath_or_buffer=join(parsed_dir_path, "{0}.{1}".format(host, device)),
                                       delim_whitespace=True, index_col=False, dtype=cf.columns_dtype[hw])

                color = next(colors)

                ax_read.plot(hardware_df['time'], hardware_df['read_mb/s'], color=color, label=host_alias)
                ax_write.plot(hardware_df['time'], hardware_df['write_mb/s'], color=color, label=host_alias)
                ax_utilization.plot(hardware_df['time'], hardware_df['%util'], color=color, label=host_alias)

            ax_read.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True, shadow=True)
            ax_write.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True, shadow=True)
            ax_utilization.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True,
                                  shadow=True)

            # Save the figures
            logger.info("Plotting disk {} read (MB/s) data".format(device_alias))
            read_plot.savefig(join(plot_dir_path, '{}_read.eps'.format(device_alias)), format='eps', dpi=1500,
                              bbox_inches="tight")
            logger.info("Plotting disk {} write (MB/s) data".format(device_alias))
            write_plot.savefig(join(plot_dir_path, '{}_write.eps'.format(device_alias)), format='eps', dpi=1500,
                               bbox_inches="tight")
            logger.info("Plotting disk {} utilization data".format(device_alias))
            utilization_plot.savefig(join(plot_dir_path, '{}_utilization.eps'.format(device_alias)), format='eps',
                                     dpi=1500, bbox_inches="tight")

    elif hw == 'network':
        for device in cf.net_interfaces:
            # Replace the host string by the alias
            try:
                if device in cf.aliases['net_interfaces'].keys():
                    device_alias = cf.aliases['net_interfaces'][device]
                else:
                    device_alias = device
            except KeyError:
                device_alias = device

            # Each device has its own plot
            # Read MB/s plot
            in_plot = plt.figure()
            out_plot = plt.figure()

            ax_in = in_plot.add_subplot(111)
            ax_out = out_plot.add_subplot(111)

            ax_in.set_title("{} : in".format(device_alias))
            ax_out.set_title("{} : out".format(device_alias))

            ax_in.set_xlabel("Total execution time (s)")
            ax_out.set_xlabel("Total execution time (s)")

            ax_in.set_ylabel("Read (MB)")
            ax_out.set_ylabel("Transmit (MB)")

            colors = cycle(colors_hex)

            for host in cf.hosts:
                # Replace the host string by the alias
                try:
                    if host in cf.aliases['hosts'].keys():
                        host_alias = cf.aliases['hosts'][host]
                    else:
                        host_alias = host
                except KeyError:
                    host_alias = host

                hardware_df = read_csv(filepath_or_buffer=join(parsed_dir_path, "{0}.{1}".format(host, device)),
                                       delim_whitespace=True, index_col=False,
                                       dtype=cf.columns_dtype[hw])

                color = next(colors)

                ax_in.plot(hardware_df['time'], hardware_df['read_mb/s'], color=color, label=host_alias)
                ax_out.plot(hardware_df['time'], hardware_df['transmitted_mb/s'], color=color, label=host_alias)

            ax_in.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True, shadow=True)
            ax_out.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, fancybox=True, shadow=True)

            # Save the figures
            logger.info("Plotting {} interface read (MB/s) data".format(device_alias))
            in_plot.savefig(join(plot_dir_path, '{}_in.eps'.format(device_alias)), format='eps', dpi=1500,
                            bbox_inches="tight")
            logger.info("Plotting {} interface transmitted (MB/s) data".format(device_alias))
            out_plot.savefig(join(plot_dir_path, '{}_out.eps'.format(device_alias)), format='eps', dpi=1500,
                             bbox_inches="tight")

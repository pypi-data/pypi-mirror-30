#!/usr/bin/env python
# coding=utf-8

from argparse import ArgumentParser
from os import getcwd
from os.path import join

from fabric.network import disconnect_all

from .core.fabfile import start as _start, stop as _stop, parse as _parse, plot as _plot


def init(args):
    """
    Create a config.yml file from the template
    :param args: Parsed arguments from command line interface
    :return:
    """
    template_config_file = """# Enables SSH-driven gatewaying through the indicated host. When this is set, newly created connections will be set
# to route their SSH traffic through the remote SSH daemon to the final destination.
# You can either comment or remove the line if you don't need a gateway
ssh_gateway: gateway.com

# The username to use in any SSH connection
# You can comment or remove this line if you're current username is the same as in the remote machines'
ssh_username: user

# The password to use in any SSH connection
# You can comment or remove this line if you're current username is the same as in the remote machines'
ssh_password: password

# The hostnames/IP@ of nodes to be profiled.
hosts:
    - host_1.com: HOST_1
    - host_2.com: HOST_2
    - host_3.com: HOST_3
    - host_4.com: HOST_4
    - host_5.com: HOST_5

# Filesystem names to profile.
# You can get the list of block devices by running : df -h
# If you don't want to profile any filesystem, then you can either comment or remove the lines.
filesystem_names:
    - sda: OS
    - sdb

# Network interfaces to profile.
# You can get the list of network interfaces by running : sar -n DEV 0
# If you don't want to profile any network interface, then you can either comment or remove the lines.

net_interfaces:
    - wlp2s0: WIFI
    - em0: 10_Gigabit_Ethernet
    - em1: 1_Gigabit_Ethernet
    - p5p2

# Time interval between two data points
interval: 10"""
    # Write the config file
    with open(join(getcwd(), 'config.yml'), 'w') as f:
        f.write(template_config_file)


def start(args):
    """
    Run the start function
    :param args: Parsed arguments from command line interface
    :return:
    """
    # Run the start function
    _start()
    # Disconnect from all hosts
    disconnect_all()


def stop(args):
    """
    Run the stop function
    :param args: Parsed arguments from command line interface
    :return:
    """
    # Run the stop function
    _stop()
    # Disconnect from all hosts
    disconnect_all()
    # Depending of the value of with_parse
    if args.with_parse is True:
        parse(args)
    elif args.with_plot is True:
        print("Ignoring the --with-plot flag")


def parse(args):
    """
    Run the parse function
    :param args: Parsed arguments from command line interface
    :return:
    """
    # Run the parse function
    _parse()
    # Depending of the value of with_plot
    if args.with_plot is True:
        plot(args)


def plot(args):
    """
    Run the plot function
    :param args: Parsed arguments from command line interface
    :return:
    """
    # Run the plot function
    _plot()


def main():
    """
    Main program entry point
    :return:
    """
    # Create the top-level parser
    parser = ArgumentParser(prog="clusterp", description="Cluster profiling made easy")
    subparsers = parser.add_subparsers()

    # Create the parser for the "start" command
    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)

    # Create the parser for the "start" command
    parser_start = subparsers.add_parser('start')
    parser_start.set_defaults(func=start)

    # Create the parser for the "stop" command
    parser_stop = subparsers.add_parser('stop')
    parser_stop.add_argument('--with-parse', action='store_true', help='Parse after stop')
    parser_stop.add_argument('--with-plot', action='store_true', help='Plot after parse')
    parser_stop.set_defaults(func=stop)

    # Create the parser for the "parse" command
    parser_parse = subparsers.add_parser('parse')
    parser_parse.add_argument('--with-plot', action='store_true', help='Plot after parse')
    parser_parse.set_defaults(func=parse)

    # Create the parser for the "plot" command
    parser_plot = subparsers.add_parser('plot')
    parser_plot.set_defaults(func=plot)

    # Parse the command line arguments
    args = parser.parse_args()
    args.func(args)

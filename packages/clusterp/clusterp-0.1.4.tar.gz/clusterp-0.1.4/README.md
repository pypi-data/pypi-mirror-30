clusterp: cluster profiling made easy
============
clusterp is a tool that aims to collect **CPU**, **memory**, **disk** and **network** usage data from a cluster of nodes and 
visualizes the data with a set of plots. This tool aims to help the system administrators and developers (especially the 
ones designing some distributed jobs) identify bottlenecks.
This project is 

## Main features
* Uses only SSH connections
* Parallel task execution
* Use of aliases for the device names and hosts

## How it works ?

```bash
$ clusterp -h
usage: clusterp [-h] {init,start,stop,parse,plot} ...

Cluster profiling made easy

positional arguments:
  {init,start,stop,parse,plot}

optional arguments:
  -h, --help            show this help message and exit
```

The clusterp tool makes 4 commands available for the user :
* The `init` command will generate a config.yml file that the user can modify in order to user 
* The `start` command is used to start the profiler on a number of nodes in a cluster. The profiler starts a sar process that periodically writes system activities in a temporary file on the local filesystem.
* The `stop` command is used to stop the profiler on a number of nodes in a cluster. The profiler kills the sar processes on all the nodes and download all the system activities files written on all the nodes on their local filesystem.
* The `parse` command is used to parse the collected system activities from the nodes. The profiler looks at all the log files, and parses the logs into files that are easier to read, and ready for plotting.
* The `plot` command is used to plot the parsed data. The profiler generates a set of .eps plots to help the final user visualize the system activities easily to detect bottlenecks if they exist.

## Requirements
* Python 2.7+
    * PyYAML 3.12+
    * file_read_backwards 1.1.2+
    * Fabric 1.13+
    * Pandas 0.20.2+
    * NumPy 1.12+
    * matplotlib 2.0.2+
* Sysstat 10.0.3+

## Install
You can install `clusterp` directly from pip :
```bash
$ pip install clusterp
```

You can also use Git to clone the repository from Github and install it manually:
```bash
$ git clone https://github.com/abdelkafiahmed/clusterp.git
$ cd clusterp
$ git clean -xdf
$ python setup.py install
```

## Usage
### Init
Before to start, let's create a new directory named : test under our home directory. (Neither the name of the directory nor the it's path are important)
We need to create a YAML config file in the current working directory before to start using the `clusterp` tool.
We can either create it manually from the template or run the following command:

```bash
$ clusterp init
```

A new file names : config.yml is created with the following content :

```yaml
# Enables SSH-driven gatewaying through the indicated host. When this is set, newly created connections will be set
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
interval: 10
```

`ssh_gateway` is set to enables SSH-driven gatewaying through the indicated host. When this is set, newly created connections will be set to route their SSH traffic through the remote SSH daemon to the final destination. This is optional.

`ssh_username` is the username to use in any SSH connection. This is optional too if the remote username matches your current one.
 
`ssh_password` is the password to use in any SSH connection. This is optional too if you have already configured passwordless SSH connections.
 
`hosts` is the a list of remote hostnames or IP addresses to profile. This attribute must be set for the profiler to work. 
You can set an alias for every host like shown in the example :
`host_1.com: HOST_1`
 
`filesystem_names` is the list of filesystems to profile. The list of filesystems mounted can be listed using the shell command : `df`. Aliases can be set for the filesystems too.

`net_interfaces` is the list of network interfaces to profile. The list of network interfaces can be listed using the shell command : `sar -n DEV`. Aliases can be set for the network interfaces too.

`interval` is the time interval between two data points. This is attribute must be set.

PS: If `filesystem_names` and `net_interfaces` set, the profiler will collect only system activities related to **CPU**, **RAM** and **Swap**.


### Start
To start profiling your cluster you can run the following command :

```bash
$ clusterp start
```

The console output will look like this:

    [host_1.com] Executing task 'start'
    [host_1.com] Executing task 'collect_data'
    [host_1.com] run: rm -rf /tmp/raw; mkdir -p /tmp/raw/{cpu,memory,swap,disk,network}; nohup sar -u 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+all' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/cpu/host_1.com & nohup sar -r 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+[0-9]' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/memory/host_1.com & nohup sar -S 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+[0-9]' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/swap/host_1.com & nohup sar -d -p 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+(sda|sdb)' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/disk/host_1.com & nohup sar -n DEV 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+(wlp0|em0|em1|p5p2)' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/network/host_1.com &
    [host_2.com] Executing task 'collect_data'
    [host_2.com] run: rm -rf /tmp/raw; mkdir -p /tmp/raw/{cpu,memory,swap,disk,network}; nohup sar -u 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+all' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/cpu/host_2.com & nohup sar -r 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+[0-9]' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/memory/host_1.com & nohup sar -S 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+[0-9]' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/swap/host_2.com & nohup sar -d -p 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+(sda|sdb)' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/disk/host_2.com & nohup sar -n DEV 10 | egrep '^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\s+(wlp0|em0|em1|p5p2)' | tr ',' '.' | tr -s ' ' ' ' > /tmp/raw/network/host_2.com &
    
    Done.
    Disconnecting from host_1.com... done.
    Disconnecting from host_2.com... done.

### Stop
Then, you can launch your programs and when they are finished or you want to stop the system activities data collection, you can stop the profiler by running the following command :

```bash
$ clusterp stop
```

The console output will look like this :
    
    [host_1.com] Executing task 'stop'
    [host_1.com] Executing task 'kill_process'
    [host_1.com] run: pkill -f sar
    [host_2.com] Executing task 'kill_process'
    [host_2.com] run: pkill -f sar
    [host_2.com] Executing task 'kill_process'
    Downloading collected data from nodes
    [host_1.com] Executing task 'download_data'
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/disk/host_1.com <- /tmp/raw/disk/host_1.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/swap/host_1.com <- /tmp/raw/swap/host_1.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/memory/host_1.com <- /tmp/raw/memory/host_1.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/cpu/host_1.com <- /tmp/raw/cpu/host_1.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/network/host_1.com <- /tmp/raw/network/host_1.com
    [host_2.com] Executing task 'download_data'
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/disk/host_2.com <- /tmp/raw/disk/host_2.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/swap/host_2.com <- /tmp/raw/swap/host_2.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/memory/host_2.com <- /tmp/raw/memory/host_2.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/cpu/host_2.com <- /tmp/raw/cpu/host_2.com
    [cedar005.saclay.inria.fr] download: /home/user/test/raw/network/host_2.com <- /tmp/raw/network/host_2.com

    Done.
    Disconnecting from host_1.com... done.
    Disconnecting from host_2.com... done.

Actually, the `stop` command has a few flags that we can use :
```bash
$ clusterp stop --help
usage: clusterp stop [-h] [--with-parse] [--with-plot]

optional arguments:
  -h, --help    show this help message and exit
  --with-parse  Parse after stop
  --with-plot   Plot after parse
```

For example, by running this command :
```bash
$ clusterp stop --with-parse --with-plot
```

We tell `clusterp` to `stop` the profiler and run the `plot` command after running the `parse` command. Useful!

Running this command :
```bash
$ clusterp stop --with-plot
```
will ignore the `--with-plot` flag and only run the `stop` command.

Running the `stop` command will not only stop the data collection but it will also download the collected data into a `raw` directory inside the current working directory (`~/test` remember ?).  Be careful, if the `raw` directory exists, the `stop` command will override all the files existing in it. For this reason, it's strongly advised to delete or move the previous data before running the profiler again.
This is the hierarchy of the `test` directory after running the `stop` command:

    test
    ├── raw
    │   ├── cpu
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── disk
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── memory
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── network
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   └── swap
    │       ├── host_1.com
    │       └── host_2.com
    ├── clusterp.log
    └── config.yml

### Parse
Now that the profiler has stopped the data collection. We can parse the data downloaded from the nodes.
In the data parsing phase, the profiler tries to eliminate irrelevant data from the downloaded files.
To start parsing the downloaded data, you need run the following command :

```bash
$ clusterp parse
```
The `parse` command has a flag that we can use too:
```bash
$ clusterp parse -h
usage: clusterp parse [-h] [--with-plot]

optional arguments:
  -h, --help   show this help message and exit
  --with-plot  Plot after parse
```
For example, by running this command :
```bash
$ clusterp parse --with-plot
```
We tell `clusterp` to run the `plot` command just after running the `parse` command! Useful!


The parsed data will be saved inside `parsed` directory under the current working directory.
This is the hierarchy of the `test` directory after running the `parse`command:

    test
    ├── parsed
    │   ├── cpu
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── disk
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── memory
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── network
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   └── swap
    │       ├── host_1.com
    │       └── host_2.com
    ├── raw
    │   ├── cpu
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── disk
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── memory
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── network
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   └── swap
    │       ├── host_1.com
    │       └── host_2.com
    ├── clusterp.log
    └── config.yml

### Plot
And now we can plot the parsed data using the following command :
```bash
$ clusterp plot
```

Executing the `plot` command will generate a set of plots (based on the aliases provided) saved inside `plot` directory under the current working directory.
This is the hierarchy of the `test` directory after running the `plot`command:

    test
    ├── parsed
    │   ├── cpu
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── disk
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── memory
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── network
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   └── swap
    │       ├── host_1.com
    │       └── host_2.com
    ├── plot
    │   ├── cpu
    │   │   ├── iowait.eps
    │   │   └── utilization.eps
    │   ├── disk
    │   │   ├── OS_read.eps
    │   │   ├── OS_utilization.eps
    │   │   ├── OS_write.eps
    │   │   ├── sdb_read.eps
    │   │   ├── sdb_utilization.eps
    │   │   └── sdb_write.eps
    │   ├── memory
    │   │   └── utilization.eps
    │   ├── network
    │   │   ├── 1_Gigabit_Ethernet_in.eps
    │   │   ├── 1_Gigabit_Ethernet_out.eps
    │   │   ├── 10_Gigabit_Ethernet_in.eps
    │   │   ├── 10_Gigabit_Ethernet_out.eps
    │   │   ├── p5p2_in.eps
    │   │   ├── p5p2_out.eps
    │   │   ├── wlp0_in.eps
    │   │   └── wlp0_out.eps
    │   └── swap
    │       └── utilization.eps
    ├── raw
    │   ├── cpu
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── disk
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── memory
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   ├── network
    │   │   ├── host_1.com
    │   │   └── host_2.com
    │   └── swap
    │       ├── host_1.com
    │       └── host_2.com
    ├── clusterp.log
    └── config.yml

## Example
The most convenient way of using clusterp is by writing a Shell script that will handle everything for you.
You can find under the [Example](Example) directory, some examples of how to run the clusterp using shell scripts.

## Known bugs
Strange behaviour when running clusterp inside a screen.
Sometimes, the SSH library used in Fabric called Paramiko asks for a password even if the SSH connections are passwordless but I think it's a Paramiko bug.

## Contributing
Please see [contribution-guide.org](http://www.contribution-guide.org) for details on what we expect from contributors. Thanks!


## Licensing
clusterp project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text.
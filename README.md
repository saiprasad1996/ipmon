Monitoring IP Addresses
=========================

This project is a simple tool to monitor the reachability of IP addresses.

It will send a ping request to each IP address and report whether the IP address
is reachable or not.

The tool is written in Python and uses the `os` and `subprocess` modules to
execute the ping command.

It has zero dependency on 3rd party packages (till now).

The project is available on [GitHub](https://github.com/saiprasad1996/ipmon.git).

How to use
------------

1. Clone the repository:

    git clone https://github.com/saiprasad1996/ipmon.git

2. Install the requirements:

    pip install -r requirements.txt

3. Run the script:

    python monitoring.py

4. The script will ask you to enter the IP addresses you want to monitor.

5. The script will then send a ping request to each IP address and report
   whether the IP address is reachable or not.

6. The script will continue to run until you stop it.

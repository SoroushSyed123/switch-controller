
import requests
import logging
from envauthprovider import EnvAuthProvider
from cliauthprovider import CLIAuthProvider
from os import environ
from restadapter import RESTSwitchAdapter
from manuf import ManufDatabase
from logging import getLogger
from datetime import datetime

log = getLogger(__name__)

class NetworkSwitch:
    def __init__(self, adapter, manuf_db):
        self.adapter = adapter
        self.manuf_db = manuf_db
    def backup_running_config(self, dest_path, head_path):
        """
        Backup the current running configuration of the network switch to the
        specified file path. Appends to the destination file. Kind of a hack,
        but that is better than overwriting the existing configuration.
        """
        response = self.adapter.run_cmd("show run")

        # FIXME: Hardcoding file paths! Make this configurable.
        # A separate HEAD file is saved and compared to the running
        # config to determine if there were actually any changes made.
        with open(head_path, "r+") as handle:
            if response.results == handle.read():
                log.info("no changes, nothing to backup")
                return
            else:
                handle.seek(0)
                handle.write(response.results)
                handle.truncate()

        with open(dest_path, "a") as handle:
            time = datetime.now().isoformat()
            pad = "*" * 20
            # Add a little message to make things easier to read.
            msg = f"{pad} Running Configuration Change On {time} {pad}\n"
            handle.write(msg)
            handle.write(response.results)
    def save_cmd_results(self, cmd, dest_path):
        """
        Run the specified CLI command against the switch and save the textual
        output to the specified path.
        """
        response = self.adapter.run_cmd(cmd)
        with open(dest_path, "w") as handle:
            handle.write(response.results)
    def mac_address_printout(self):
        """
        Give a printout of MAC address to manufacturer mappings for each port
        on the switch. Useful to figure out what is connected to your network.
        """
        results = self.mac_addr_report()
        for portno in results:
            log.info(f"port {portno}")
            for entry, mac_addr in results[portno]:
                log.info(f"{mac_addr}: {entry.manuf}")

    def mac_addr_report(self):

        response = self.adapter.run_cmd("show mac-address")
        results = response.results.split("\n")[5:]
        mappings = {}

        for result in results:
            try:
                [ mac_addr, port, vlan_id ] = result.split()
            except ValueError:
                continue
            entry = self.manuf_db.query(mac_addr.replace("-", ""))
            if entry is None:
                continue
            try:
                mappings[port].append((entry, mac_addr))
            except KeyError:
                mappings[port] = [ (entry, mac_addr) ]

        return mappings

def setup_logging(name=__name__, level=logging.DEBUG, fmt=logging.BASIC_FORMAT):
    log = logging.getLogger(name)
    log.setLevel(level)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log

def main():
    # Setup logging.
    log = setup_logging(__name__)
    # Setup authentication provider for the switch.
    auth = CLIAuthProvider()
    host = input("Host: ")
    # Setup an adapter to communicate with the network switch.
    adapter = RESTSwitchAdapter("http", host, requests, auth)
    # Load a database of MAC address to manufactuer mappings.
    manuf_db = ManufDatabase("manuf.txt")
    # Create the switch object.
    switch = NetworkSwitch(adapter, manuf_db)
    # This is where we acutally do our operations on the switch.
    switch.scan_ports()

if __name__ == "__main__":
    main()


import requests
import logging
from envauthprovider import EnvAuthProvider
from cliauthprovider import CLIAuthProvider
from os import environ
from restadapter import RESTSwitchAdapter
from manuf import ManufDatabase

class NetworkSwitch:
    def __init__(self, adapter, manuf_db):
        self.adapter = adapter
        self.manuf_db = manuf_db
    def backup_running_config(self, dest_path):
        """
        Backup the current running configuration of the network switch to the
        specified file path.
        """
        self.save_cmd_results("show run", dest_path)
    def save_cmd_results(self, cmd, dest_path):
        """
        Run the specified CLI command against the switch and save the textual
        output to the specified path.
        """
        response = self.adapter.run_cmd(cmd)
        with open(dest_path, "wb") as handle:
            handle.write(response.results)
    def scan_ports(self):
        """
        Give a printout of MAC address to manufacturer mappings for each port
        on the switch. Useful to figure out what is connected to your network.
        """
        response = self.adapter.run_cmd("show mac-address")
        # There are 5 lines of pretty printed borders and table headers.
        results = str(response.results, encoding="utf-8").split("\n")[5:]
        # MAC-Address Port VLAN
        mapping = {}
        for result in results:
            try:
                [ mac_addr, port, vlan_id ] = result.split()
            except ValueError:
                continue
            try:
                mapping[port].append(mac_addr)
            except KeyError:
                mapping[port] = [ mac_addr ]

        # TODO: Return a class with all this information instead of just 
        # printing it out.
        sorted_keys = [ *mapping.keys() ]
        sorted_keys.sort()
        for key in sorted_keys:
            print(f"Port #{key}")
            for addr in mapping[key]:
                addr = addr.replace("-", "")
                manuf = self.manuf_db.query(addr)
                if manuf is None:
                    manuf = "Unknown"
                print(f"{addr} = {manuf.manuf}")

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
    adapter = RESTSwitchAdapter("http", host, requests, auth,
            log=log)
    # Load a database of MAC address to manufactuer mappings.
    manuf_db = ManufDatabase("manuf.txt")
    # Create the switch object.
    switch = NetworkSwitch(adapter, manuf_db)
    # This is where we acutally do our operations on the switch.
    switch.scan_ports()

if __name__ == "__main__":
    main()

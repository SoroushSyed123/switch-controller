
from dataclasses import dataclass

class SwitchAdapter:
    """
    Abstracts away the process of transmitting CLI commands to a switch.
    An implmentation could use the switch's REST API, or a serial port.
    """
    def run_cmd(self, cmd):
        raise NotImplementedError()

@dataclass
class SwitchResponse:
    cmd: str
    results: str
    uri: str
    status: str
    error_msg: str

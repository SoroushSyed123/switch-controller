
commands = {}

def command(name):
    def inner(callback):
        commands[name] = callback
        return callback
    return inner

@command("backup-running-config")
def backup_config(switch, args):
    switch.backup_running_config(args.dest_path)

@command("save-cmd-results")
def save_cmd_results(switch, args):
    if args.cmd is None:
        raise ValueError("Must supply command through -c 'command' switch")
    switch.save_cmd_results(args.cmd, args.dest_path)

@command("scan-ports")
def scan_ports(switch, args):
    switch.scan_ports()

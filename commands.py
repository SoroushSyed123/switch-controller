
import logging

log = logging.getLogger(__name__)

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
    if not hasattr(args, "cli_command"):
        raise ValueError("Must supply command through -c 'command' switch")
    log.info(f"running \"{args.cli_command}\" -> {args.dest_path}")
    switch.save_cmd_results(args.cli_command, args.dest_path)

@command("mac-addr-printout")
def mac_address_printout(switch, args):
    switch.mac_address_printout()

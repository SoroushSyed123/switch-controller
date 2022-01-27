
commands = {}

def command(name):
    def inner(callback):
        commands[name] = callback
        return callback
    return inner

@command("backup-config")
def backup_config(switch, args):
    switch.backup_running_config(args.dest_path)

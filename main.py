
from os import environ
import requests
from logging import (DEBUG, getLogger, Formatter, BASIC_FORMAT, StreamHandler,
        FileHandler)
from argparse import ArgumentParser
from simpleauthprovider import SimpleAuthProvider
from envauthprovider import EnvAuthProvider
from curlhttpprovider import CurlHTTPProvider
from commands import commands
from restadapter import RESTSwitchAdapter
from manuf import ManufDatabase
from switch import NetworkSwitch

def setup_parser():

    # Setup some command line argument parsing.
    parser = ArgumentParser(description="Switch controler program")
    parser.add_argument("command")
    parser.add_argument("host")
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    parser.add_argument("--http-provider", default="requests")
    parser.add_argument("--dest-path", default="output.txt")
    parser.add_argument("-s", "--scheme", default="http")
    parser.add_argument("-m", "--manuf", default="manuf.txt")
    parser.add_argument("-c", "--cli-command", default=None)
    parser.add_argument("-l", "--log-path", default="log.txt")
    parser.add_argument("--head-path", default="HEAD.txt")

    return parser

def setup_logging(log_path="log.txt", fmt=BASIC_FORMAT):
    """Sets up the root logger.
    :param log_path: Log file path.
    :param fmt: Formatter string.
    :returns: A tuple. First value is the logging, object, and second is either
        None, for no errors, or an IOError if the log file cannot be opened.
    """

    log = getLogger()
    log.setLevel(DEBUG)
    formatter = Formatter(fmt)
    handler = StreamHandler()

    handler.setFormatter(formatter)
    log.addHandler(handler)

    if log_path is not None:
        try:
            handler = FileHandler(log_path)
        except IOError as error:
            return (log, error)

        handler.setFormatter(formatter)
        log.addHandler(handler)
    return (log, None)

def _main(args, log):

    if args.username is not None and args.password is not None:
        auth = SimpleAuthProvider(args.username, args.password)
    else:
        auth = EnvAuthProvider(environ)

    curl_http = CurlHTTPProvider()
    http_providers = {
        "requests": requests,
        "curl": curl_http
    }

    try:
        http = http_providers[args.http_provider]
    except KeyError:
        log.error(f"invalid HTTP provider specified: {args.http_provider}")
        log.error(f"valid HTTP providers: {','.join(http_providers.keys())}")
        return

    scheme = args.scheme
    if scheme != "http" and scheme != "https":
        log.error(f"invalid scheme, schemes are http,https")
        return
    if scheme == "http":
        log.warning("HTTP REST requests are not secure")

    # Lets us specify the hostname in stdin instead of CLI args.
    if args.host == "-":
        args.host = input()
    adapter = RESTSwitchAdapter(scheme, args.host, http, auth)
    manuf_db = ManufDatabase(args.manuf)
    switch = NetworkSwitch(adapter, manuf_db)

    try:
        commands[args.command](switch, args)
    except KeyError:
        log.error(f"unknown command \"{args.command}\"")
        log.error(f"valid commands are {','.join(commands.keys())}")
        return

def main():

    parser = setup_parser()
    args = parser.parse_args()
    log, exc = setup_logging(log_path=args.log_path)

    if isinstance(exc, IOError):
        # We couldn't open our log file, show traceback an exit.
        exc_info = (IOError, exc, exc.__traceback__)
        log.exception("cannot open log file for writing", exc_info=exc_info)
        exit(-1)

    try:
        _main(args, log)
    except Exception:
        log.exception("unhandled exception in main()")

if __name__ == "__main__":
    main()

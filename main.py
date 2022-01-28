
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

    return parser

def setup_logging(log_path="log.txt", fmt=BASIC_FORMAT):

    log = getLogger()
    log.setLevel(DEBUG)
    formatter = Formatter(fmt)
    handler = StreamHandler()

    handler.setFormatter(formatter)
    log.addHandler(handler)

    if log_path is not None:
        handler = FileHandler(log_path)

        handler.setFormatter(formatter)
        log.addHandler(handler)
    return log

def main():

    parser = setup_parser()
    log = setup_logging()
    args = parser.parse_args()
    log.debug(args)

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

    adapter = RESTSwitchAdapter(scheme, args.host, http, auth, log=log)
    manuf_db = ManufDatabase(args.manuf)
    switch = NetworkSwitch(adapter, manuf_db)

    try:
        commands[args.command](switch, args)
    except KeyError:
        log.error(f"unknown command \"{args.command}\"")
        log.error(f"valid commands are {','.join(commands.keys())}")
        return

if __name__ == "__main__":
    main()

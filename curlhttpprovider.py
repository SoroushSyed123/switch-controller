
from httpprovider import HTTPProvider
import types
import subprocess
from logging import getLogger, DEBUG, BASIC_FORMAT, StreamHandler, Formatter

log = getLogger(__name__)

class CurlHTTPProvider(HTTPProvider):
    """
    Launches a cURL subprocess instead of using the requests module. Made this
    as a learning experiment.
    """
    def request(self, method, url, data=None, headers=None, cookies=None):
        """Makes an HTTP request. headers and cookies can either be dicts or
            lists. If they are dicts, their key and values are appended. If
            They are lists, they must contain only strings, and they will not
            be modified.
        """
        cmd = [ "curl", "-q", "-i", "-X", method, url ]
        if data is not None:
            cmd.extend([ "-d", data ])

        if isinstance(cookies, dict):
            result = []
            for cookie in cookies:
                result.append(cookie + "=" + cookies[cookie])
            result = ";".join(result)
            cmd.extend([ "-b", result ])

        if isinstance(cookies, list):
            result = ";".join(cookies)
            cmd.extend([ "-b", result ])

        if isinstance(headers, dict):
            result = []
            for header in headers:
                result.extend([ "-H", header + ": " + headers[header]])
            cmd.extend(result)

        if isinstance(headers, list):
            for header in headers:
                cmd.extend([ "-H", header])

        log.debug(f"command: {cmd}")
        completed = subprocess.run(cmd, capture_output=True, check=True)
        return self._parse_curl_stdout(completed.stdout)
    def _parse_curl_stdout(self, stdout):
        """Parses the stdout output of the cURL subprocess, returning a 
            `SimpleNamespace` object with the same attirubes as a 
            requests.Response object
        """

        headers_end = stdout.find(b"\r\n\r\n")
        if headers_end == -1:
            raise ValueError("Cannot find end of headers")
        [ status, *header_lines ] = str(stdout[:headers_end], 
                encoding="utf-8").split("\r\n")

        ns = types.SimpleNamespace()
        ns.headers = {}

        for header in header_lines:
            [ key, value ] = header.split(":", 1)
            ns.headers[key.lower()] = value

        if not "content-type" in ns.headers:
            raise ValueError("Expected content-type in response")

        ns.charset = "ISO-8859-1"
        # Read here for more info:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
        content_type = ns.headers["content-type"]
        if ";" in content_type:
            [ content_type, directives ] = ns.headers["content-type"].split(";",
                    1)

            ns.directives = {}

            for directive in directives.strip().split(" "):
                [ key, value ] = directive.split("=")
                ns.directives[key] = value

            try:
                ns.charset = ns.directives["charset"]
            except KeyError:
                # We have already set the default, do nothing.
                pass

        ns.content = stdout[headers_end+4:]
        log.debug(f"received {len(ns.content)} chars")
        ns.text = str(ns.content, encoding=ns.charset)

        print(f"server responded with: {status}")
        [ ver, code, reason ] = status.split(" ", 2)
        ns.status_code = int(code)
        ns.reason = reason
        return ns

# Some simple tests to make sure our program works.
def main():

    host = input()
    http = CurlHTTPProvider()
    resp = http.request("GET", host, 
            headers=[ "User-Agent: Chrome" ])
    # TODO: Raise an exception if we get a bad response.
    log.info(resp.status_code)

    resp = http.request("GET", host, 
            headers={ "User-Agent": "Chrome" })
    log.info(resp.status_code)

    resp = http.request("GET", host,
            cookies={ "sessionId": "test-thing" })
    log.info(resp.status_code)

    resp = http.request("GET", host,
            cookies=[ "sessionId=test-thing" ])

if __name__ == "__main__":
    log.setLevel(DEBUG)
    handler = StreamHandler()
    handler.setFormatter(Formatter(BASIC_FORMAT))
    log.addHandler(handler)
    main()

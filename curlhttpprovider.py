
from httpprovider import HTTPProvider
import types
import subprocess

class CurlHTTPProvider(HTTPProvider):
    """
    Launches a cURL subprocess instead of using the requests module. Made this
    as a learning experiment.
    """
    def request(self, method, url, data=None, headers=None, cookies=None):
        cmd = [ "curl", "-q", "-i", "-X", method, url ]
        if data is not None:
            cmd.extend([ "-d", data ])
        if cookies is not None:
            if isinstance(cookies, dict):
                result = []
                for cookie in cookies:
                    result.append(cookie + "=" + cookies[cookie])
                result = ";".join(result)
                cmd.extend([ "-b", result ])
            if isinstance(cookies, list):
                result = ";".join(cookies)
                cmd.extend([ "-b", result ])
        print(cmd)
        completed = subprocess.run(cmd, capture_output=True, check=True)
        return self._parse_curl_stdout(completed.stdout)
    def _parse_curl_stdout(self, stdout):
        headers_end = stdout.find(b"\r\n\r\n")
        if headers_end == -1:
            raise ValueError("Cannot find end of headers")
        [ status, *header_lines ] = str(stdout[:headers_end], 
                encoding="utf-8").split("\r\n")
        ns = types.SimpleNamespace()
        ns.headers = {}
        for header in header_lines:
            [ key, value ] = header.split(":", 1)
            ns.headers[key] = value
        ns.content = stdout[headers_end+4:]
        ns.text = str(ns.content, encoding="utf-8")
        print(status)
        [ ver, code, reason ] = status.split(" ", 2)
        ns.status_code = int(code)
        ns.reason = reason
        return ns

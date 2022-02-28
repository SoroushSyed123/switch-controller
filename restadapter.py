
import logging
import json
from adapter import SwitchAdapter, SwitchResponse
import requests
from requests.exceptions import HTTPError
import base64

log = logging.getLogger(__name__)

class RESTSwitchAdapter(SwitchAdapter):
    def __init__(self, scheme, host, http, auth, version=3):

        self.scheme = scheme
        self.host = host
        self.http = http
        self.auth = auth
        # Defaulting log to none makes sure we always supply it.
        self.version = "v" + str(version)

        self.base_url = f"{scheme}://{host}/rest/{self.version}/"
        log.debug(f"base URL: {self.base_url}")
        self.session_url = self.base_url + "login-sessions"
    def run_cmd(self, cmd):
        with self.Session(self.http, self.auth, self.session_url) as cookies:
            url = self.base_url + "cli"
            data = { "cmd": cmd }
            resp = self.http.request("POST", url, cookies=cookies,
                    data=json.dumps(data))
            # FIXME: Make an ok property on the HTTPprovider interface.
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            resp_json = json.loads(resp.text)
            result = base64.b64decode(resp_json.pop("result_base64_encoded"))
            # We don't need this info for now ...
            resp_json.pop("uri")
            resp_json["results"] = str(result, encoding="utf-8")
            return SwitchResponse(**resp_json)
    class Session:
        def __init__(self, http, auth, url):
            self.http = http
            self.auth = auth
            self.url = url
        def __enter__(self):
            username, password = self.auth.get_auth()
            data = {
                "userName": username,
                "password": password
            }
            resp = self.http.request("POST", self.url, data=json.dumps(data))
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            log.info("successfully logged into session")
            resp_json = json.loads(resp.text)
            [ key, value ] = resp_json["cookie"].split("=", 1)
            self.cookies = { key: value }
            return self.cookies
        def __exit__(self, etype, evalue, traceback):
            is_good = True
            if etype is not None:
                is_good = False
                log.exception("exception thrown while in session:")
            resp = self.http.request("DELETE", self.url, cookies=self.cookies)
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            log.info("successfully logged out of session")
            return is_good

class AuthProvider:
    def get_auth(self):
        return input("username: "), input("password: ")

# FIXME: broken test, setup_logging() does not exist.
def main():
    log = setup_logging()
    auth = AuthProvider()
    host = input("Host: ")
    adapter = RESTSwitchAdapter("http", host, requests, auth)
    response = adapter.run_cmd("show run")
    print(response)

if __name__ == "__main__":
    main()

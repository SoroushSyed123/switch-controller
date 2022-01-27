
import logging
import json
from adapter import SwitchAdapter, SwitchResponse
import requests
from requests.exceptions import HTTPError
import base64

class RESTSwitchAdapter(SwitchAdapter):
    def __init__(self, scheme, host, http, auth, version=3, log=None):

        self.scheme = scheme
        self.host = host
        self.http = http
        self.auth = auth
        # Defaulting log to none makes sure we always supply it.
        self.log = log
        self.version = "v" + str(version)

        self.base_url = f"{scheme}://{host}/rest/{self.version}/"
        self.log.debug(f"base URL: {self.base_url}")
        self.session_url = self.base_url + "login-sessions"
    def run_cmd(self, cmd):
        with self.Session(self.http, self.auth, self.session_url,
                log=self.log) as cookies:
            url = self.base_url + "cli"
            data = { "cmd": cmd }
            resp = self.http.request("POST", url, cookies=cookies,
                    data=json.dumps(data))
            # FIXME: Make an ok property on the HTTPprovider interface.
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            resp_json = json.loads(resp.text)
            result = base64.b64decode(resp_json.pop("result_base64_encoded",
                None))
            resp_json["results"] = result
            return SwitchResponse(**resp_json)
    class Session:
        def __init__(self, http, auth, url, log=None):
            self.http = http
            self.auth = auth
            self.url = url
            self.log = log
        def __enter__(self):
            username, password = self.auth.get_auth()
            data = {
                "userName": username,
                "password": password
            }
            resp = self.http.request("POST", self.url, data=json.dumps(data))
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            self.log.info("successfully logged into session")
            resp_json = json.loads(resp.text)
            [ key, value ] = resp_json["cookie"].split("=", 1)
            self.cookies = { key: value }
            return self.cookies
        def __exit__(self, etype, evalue, traceback):
            if etype is not None:
                self.log.exception("exception thrown while in session:")
            resp = self.http.request("DELETE", self.url, cookies=self.cookies)
            if not (199 < resp.status_code < 399):
                raise HTTPError(resp)
            self.log.info("successfully logged out of session")
            return True

class AuthProvider:
    def get_auth(self):
        return input("username: "), input("password: ")

def main():
    log = setup_logging()
    auth = AuthProvider()
    host = input("Host: ")
    adapter = RESTSwitchAdapter("http", host, requests, auth,
            log=log)
    response = adapter.run_cmd("show run")
    print(response)

if __name__ == "__main__":
    main()

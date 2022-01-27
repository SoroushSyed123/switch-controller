
from authprovider import AuthProvider

class EnvAuthProvider(AuthProvider):
    def __init__(self, env):
        self.env = env
    def get_auth(self):
        return (self.env["_USERNAME"], self.env["_PASSWORD"])

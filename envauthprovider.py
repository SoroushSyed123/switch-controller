
from authprovider import AuthProvider

class EnvAuthProvider(AuthProvider):
    def __init__(self, env):
        self.env = env
    def get_auth(self):
        try:
            return (self.env["_USERNAME"], self.env["_PASSWORD"])
        except KeyError as error:
            raise ValueError("missing required env") from error

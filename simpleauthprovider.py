
from authprovider import AuthProvider

class SimpleAuthProvider(AuthProvider):
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def get_auth(self):
        return self.username, self.password

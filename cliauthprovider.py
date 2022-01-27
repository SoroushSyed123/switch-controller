
from getpass import getpass
from authprovider import AuthProvider

class CLIAuthProvider(AuthProvider):
    def get_auth(self):
        username = input("Username: ")
        password = getpass()
        return username, password

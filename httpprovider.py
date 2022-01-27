
class HTTPProvider:
    """
    Interface for sending / receiving HTTP requests. Any part of the program
    that requires an instance of HTTPProivder can be passed the `request` module.
    """
    def request(self, *args, **kwargs):
        raise NotImplementedError()

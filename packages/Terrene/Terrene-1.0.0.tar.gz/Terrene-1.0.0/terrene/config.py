"""
Configures the SDK
"""

from . import api_protocol, api_host, api_port


class URL:
    def __init__(self, protocol: str, host: str, port: int):
        self.protocol, self.host, self.port = protocol, host, port

    def __call__(self, *args, **kwargs):
        return '{}://{}:{}'.format(self.protocol, self.host, self.port)


api = URL(api_protocol, api_host, api_port)

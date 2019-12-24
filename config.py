import os
from socket import gethostname, gethostbyname

from secret import SecretConfig


class Config(SecretConfig):
    SERVER_PORT = os.environ.get('PORT') or '8000'
    SERVER_URL = os.environ.get('SERVER_URL') or f"http://{gethostbyname(gethostname())}:{SERVER_PORT}"
    TOKEN = str()
    TEST_DATA = dict()


config = Config()

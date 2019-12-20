import os

from secret import SecretConfig


class Config(SecretConfig):
    SERVER_PORT = os.environ.get('PORT') or '8010'
    SERVER_URL = os.environ.get('SERVER_URL') or f"http://localhost:{SERVER_PORT}"


config = Config()

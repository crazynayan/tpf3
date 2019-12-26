import os
from socket import gethostname, gethostbyname

from secret import SecretConfig


class Config(SecretConfig):
    SERVER_PORT = os.environ.get('PORT') or '8000'
    SERVER_URL = os.environ.get('SERVER_URL') or f"http://{gethostbyname(gethostname())}:{SERVER_PORT}"
    TOKEN = str()
    TEST_DATA = dict()
    REGISTERS: tuple = ('R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14',
                        'R15')
    # SERVER_URL = f"http://localhost:8010"


config = Config()

import sys
sys.path.append("..")

from abc import ABC, abstractmethod
from api.bybit import Bybit

apis = {
    'bybit': Bybit,
}

class Api(ABC):
    @staticmethod
    def create_api(config):
        return apis[config['general']['api']](config)
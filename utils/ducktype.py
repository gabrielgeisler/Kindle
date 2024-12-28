
from typing import Any


class Duck:
    def __init__(self, data):
        self._data = data

    @property
    def __dict__(self):
        return {
            k: self._convert(v)
            for k, v in self._data.items()
        }
    
    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        
        value = self._data.get(name)
        return self._convert(value)
    
    def __getitem__(self, item):
         return self.__getattribute__(item)

    def _convert(self, value):
        if type(value) is list:
            return [self._convert(v) for v in value]
        
        if type(value) is dict:
            return Duck(value)
        
        return value
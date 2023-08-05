import re
from typing import Tuple

IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
IP_MAX = 0xFFFFFFFF

class IPv4Address(object):
    def __init__(self, addr: str=None, _int_addr:int=None):
        if addr:
            self._addr = self.parse_addr(addr)
        elif _int_addr is not None:
            if _int_addr > IP_MAX or _int_addr < 0:
                raise ValueError('_int_addr is out of range')
            self._addr = _int_addr
        else:
            raise ValueError('either addr or _int_addr must be set')


    @staticmethod
    def parse_addr(addr: str) -> int:
        if not IP_REGEX.search(addr):
            raise ValueError('The parameter addr must be a valid IPv4 address')
        decaddr = [int(i) for i in addr.split('.')]
        addr = 0
        addr += decaddr[0] << 24
        addr += decaddr[1] << 16
        addr += decaddr[2] << 8
        addr += decaddr[3]
        return addr
    
    @property
    def intaddr(self):
        return self._addr


    def __add__(self, addr: 'IPv4Address'):
        return IPv4Address(_int_addr=self._addr + addr._addr)


    def __sub__(self, addr: 'IPv4Address'):
        return IPv4Address(_int_addr=self._addr - addr._addr)
    
    def __str__(self):
        b1 = (self._addr & 0XFF000000) >> 24
        b2 = (self._addr & 0x00FF0000) >> 16
        b3 = (self._addr & 0x0000FF00) >> 8
        b4 = self._addr & 0x000000FF
        return '{}.{}.{}.{}'.format(b1, b2, b3, b4)

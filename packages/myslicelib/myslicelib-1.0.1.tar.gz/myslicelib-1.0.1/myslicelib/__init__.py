import sys

try:
    assert sys.version_info >= (3,5)
except AssertionError:
    exit("MySlice Lib requires Python 3.5")

from typing import Set
from myslicelib.util import Authentication, Endpoint

class Setup():

    def __init__(self):
        self._setup = True
        self._authentication = None
        self._endpoints = None

    @property
    def authentication(self) -> Authentication:
        return self._authentication

    @authentication.setter
    def authentication(self, authentication: Authentication) -> None:
        self._authentication = authentication

    @authentication.deleter
    def authentication(self) -> None:
        del self._authentication

    @property
    def endpoints(self) -> Set[Endpoint]:
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints: Set[Endpoint]) -> None:
        self._endpoints = endpoints

    @endpoints.deleter
    def endpoints(self) -> None:
        del self._endpoints

setup = Setup()

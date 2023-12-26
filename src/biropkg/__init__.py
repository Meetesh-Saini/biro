from abc import abstractclassmethod
import re


class BiroPkg(object):
    @abstractclassmethod
    def list_pkg(self):
        pass

    @abstractclassmethod
    def fetch_metadata(self, pkgname):
        pass

    @abstractclassmethod
    def install(self, pkg):
        pass


delimiter = "\\ "
pkg_encode = lambda x: x.replace(" ", delimiter)
pkg_split = lambda x: re.split(r"(?<!\\) ", x)
pkg_decode = lambda x: x.replace(delimiter, " ")

# Import the installer classes and register them
from biropkg.github import BiroGithub
from biropkg.db import pre_db

__all__ = (
    "BiroGithub",
    "pkg_encode",
    "pkg_split",
    "pkg_decode",
    "pre_db"
)

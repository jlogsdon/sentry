import os

from click import echo
from itertools import chain
from operator import itemgetter
from hashlib import md5
from django.contrib.staticfiles.management.commands.collectstatic import Command as BaseCommand


BUFFER_SIZE = 65536
VERSION_PATH = "version"


def checksum(file_):
    hasher = md5()
    with open(file_[1], "rb") as fp:
        buf = fp.read(BUFFER_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fp.read(BUFFER_SIZE)
    return hasher.hexdigest()


def get_bundle_version(files):
    hasher = md5()
    for (short, _), sum in list(zip(files, list(map(checksum, files)))):
        echo(f"{sum}  {short}")
        hasher.update(f"{sum}  {short}\n".encode("utf-8"))
    return hasher.hexdigest()


class Command(BaseCommand):
    def collect(self):
        try:
            os.remove(self.storage.path(VERSION_PATH))
        except OSError:
            pass

        collected = super().collect()
        paths = sorted(set(chain(*itemgetter(*collected.keys())(collected))))
        abs_paths = list(map(self.storage.path, paths))
        version = get_bundle_version(list(zip(paths, abs_paths)))
        echo("-----------------")
        echo(version)
        with open(self.storage.path(VERSION_PATH), "wb") as fp:
            fp.write(version.encode("utf-8"))
        return collected

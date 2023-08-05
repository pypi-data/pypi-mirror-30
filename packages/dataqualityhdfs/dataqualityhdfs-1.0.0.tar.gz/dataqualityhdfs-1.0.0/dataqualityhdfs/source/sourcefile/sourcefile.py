import abc

from dataqualityhdfs.source.source import Source


class SourceFile(Source,object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, path,file_name):
        self._path = path
        self._file_name = file_name

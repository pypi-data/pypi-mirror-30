from dataqualityhdfs.source.source import Source

from pyspark.context import SparkContext
from pyspark.sql import HiveContext


class SourceHIVE(Source):

    def __init__(self,query):
        self._query = query

    @property
    def query(self):
        return self._query

    def retrieve_dataset(self):
        sc = SparkContext.getOrCreate()
        hivec = HiveContext(sc)

        return hivec.sql(self._query)
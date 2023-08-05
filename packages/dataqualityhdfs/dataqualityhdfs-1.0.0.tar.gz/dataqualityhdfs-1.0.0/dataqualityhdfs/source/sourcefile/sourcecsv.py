from dataqualityhdfs.source.sourcefile import SourceFile
import os
from pyspark.sql import HiveContext,SQLContext,Row
from pyspark.context import SparkContext

class SourceCSV(SourceFile):

    def __init__(self, path, file_name,delimitator,header,columns):
        super(SourceCSV, self).__init__(path, file_name)
        self._delimitator = delimitator
        self._header = header
        self._columns = columns

    def retrieve_dataset(self):
        sc = SparkContext.getOrCreate()
        sqlContext = SQLContext(sc)
        return sqlContext.createDataFrame(sc.textFile(os.path.join(self._path, self._file_name)).map(lambda line: line.split(self._delimitator)),self._columns)
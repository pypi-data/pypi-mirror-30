import os
import sys
import glob

from parsers import merge_dict
from output import OUT

def ntimes(n, f):
    def ff(x):
        for i in range(0,n):
            x = f(x)
        return x
    return ff

class Spark:

    def __init__(self, spark_home):
        self.context = None
        self.spark_home = spark_home
 
    def setup_env(self):
        # Check for empty spark home
        if not self.spark_home:
            OUT.fail("spark home is undefined")
        #So the choice for now would be not to allow for changing spark home
        abs_spark_home = os.path.abspath(self.spark_home)
        #check if pyspark is aleady loaded
        spark_module = sys.modules.get('pyspark')
        if spark_module is not None:
            OUT.debug("PySpark aleady loaded at: %s" % spark_module)
            current_spark_home = ntimes(5, os.path.dirname)(os.path.abspath(spark_module.__file__))
            OUT.debug("Current SPARK_HOME: %s" % current_spark_home)
            if current_spark_home != abs_spark_home:
                OUT.fail("Cannot change SPARK_HOME from: %s to: %s" %(current_spark_home, abs_spark_home)) 
        else:
            if not os.path.isdir(self.spark_home):
                OUT.fail("SPARK_HOME : %s does not exist" % self.spark_home)      
            for spc in glob.glob(os.path.join(abs_spark_home,'python','lib','*.zip')):
                sys.path.insert(0, spc)
        os.environ['SPARK_HOME']=abs_spark_home
    

    def setup(self, config):
        self.setup_env()
        from pyspark.sql import SparkSession
        from pyspark import SparkConf
        
        self.conf = SparkConf().setAll(config.items())
        OUT.debug("Creating spark session with config:")        
        OUT.debug(self.conf.toDebugString())        

        self.spark = SparkSession.Builder().config(conf=self.conf).getOrCreate()
        self.sc = self.spark.sparkContext

    def teardown(self):
        if self.spark is not None:
            self.spark.stop()
            self.spark = None
            self.sc = None


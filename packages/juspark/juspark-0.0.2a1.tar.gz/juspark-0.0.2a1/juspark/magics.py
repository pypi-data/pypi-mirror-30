import shlex
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from juspark.parsers import PySparkParser,  parse_opts_from_cell, merge_dict, ExitError
from juspark.spark import Spark
from juspark.output import OUT
import os
from IPython.display import HTML
import json

def mute_exit(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ExitError:
            return None
    return wrapper

@magics_class
class PySparkMagics(Magics):

    def __init__(self, shell):
        super(PySparkMagics, self).__init__(shell)
        self.spark = None

    def load_profile(self, profile):
        profile_dirs = [os.path.join(os.environ['HOME'],".juspark", "profiles"), '/etc/juspark/profiles']
        OUT.debug("Looking for  profile: %s in %s" % (profile, profile_dirs))
        profile_files = filter(os.path.isfile, map(lambda pd: os.path.join(pd, profile), profile_dirs))
        if not profile_files:
            OUT.fail("Profile file does not exists for: %s in %s" % (profile, profile_dirs))
        else:
            profile_file = profile_files[0]
        #this is somewhat tricky but it should work
        with open(profile_file,'r') as profile_f:
            return json.load(profile_f)
        
    def load_profiles(self, profiles):
        return merge_dict(dict(),*[self.load_profile(p) for p in profiles])    
    
    @mute_exit
    @line_cell_magic
    def juspark(self, line, cell=""):
        #print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        #print("Line", line)
        parser = PySparkParser()
        args = parser.parse_args(filter(lambda s:len(s)>0,shlex.split(line)))
        OUT.configure(args.silent, args.verbose)
        OUT.debug("Passed params: %s" % vars(args))
        profile_conf = self.load_profiles(args.profile.split(',')) if args.profile else dict()
        options = merge_dict(profile_conf, json.loads(cell)) if cell else profile_conf 
        #options = parse_opts_from_cell(cell)
        if self.spark:  
            if args.force:
                self.teardown()
            elif args.strict:
                OUT.fail("There is a existing spark context. Please use --force to force reloading")
            else:
                OUT.info("Reusing exising context with master: %s" % self.spark.sc.master)
        if not self.spark:
            spark = Spark(os.environ['SPARK_HOME'])
            self.spark = spark
            spark.setup( options)
            self.shell.user_ns['spark'] = spark.spark 
            self.shell.user_ns['sc'] = spark.sc 
        OUT.info("PySpark initialised: spark context available as sc")
        return HTML('<a href="%s" target="_blank" >SparkUI</a>' % self.shell.user_ns['sc'].uiWebUrl)
    def teardown(self):
        if self.spark:
            OUT.debug("Will try to tear down the exising instance %s" % self.spark)
            self.shell.user_ns['sc'] = None
            self.shell.user_ns['spark'] = None
            self.spark.teardown()
            self.spark = None            

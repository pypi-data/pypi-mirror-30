from exceptions import IPySparkError

class Output:

    def __init__(self, silent=False, verbose = False):
        self.silent = silent
        self.verbose = verbose

    def configure(self, silent=False, verbose = False):
        self.silent = silent
        self.verbose = verbose

    def info(self,s):
        if not self.silent:
            print(s)    

    def debug(self, s):
        if not self.silent and self.verbose:
            print(s)

    def fail(self, msg):
        self.info(msg)
        raise IPySparkError(msg)


OUT = Output()

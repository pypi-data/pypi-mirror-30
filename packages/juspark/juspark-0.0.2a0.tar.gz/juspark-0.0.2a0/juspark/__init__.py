import juspark.magics

pyspark_magics = None

def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    global pyspark_magics
    pyspark_magics = juspark.magics.PySparkMagics(ipython)
    ipython.register_magics(pyspark_magics)
    
    

def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    # TODO: stop the context and remove home
    global pyspark_magics
    if pyspark_magics:
    	pyspark_magics.teardown()
    pyspark_magics = None




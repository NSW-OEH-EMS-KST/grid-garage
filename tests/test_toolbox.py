import os
import shutil
from unittest import TestCase
# from grid-garage import Grid Garage.pyt
sp = (os.path.dirname(os.path.realpath(__file__)))

ggtbx = __import__(os.path.join(sp, "Grid Garage.pyt"))
# foo_bar_mod = importlib.import_module("path.to.foo bar")

srcfile = 'a/long/long/path/to/file.py'
dstroot = '/home/myhome/new_folder'


assert not os.path.isabs(srcfile)
dstdir =  os.path.join(dstroot, os.path.dirname(srcfile))

os.makedirs(dstdir) # create all directories, raise an error if it already exists
shutil.copy(srcfile, dstdir)
class TestToolbox(TestCase):
    """
    """
    pass
    # tb = Toolbox()
    # for t in tb.tools:
    #     try:
    #         tool = t()
    #         print "Load test - {}".format(tool.label)
    #         tool.execute(tool.getParameterInfo(), None)
    #     except Exception as e:
    #         print e

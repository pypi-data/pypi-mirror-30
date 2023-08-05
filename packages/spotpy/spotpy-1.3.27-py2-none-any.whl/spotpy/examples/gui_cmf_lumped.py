"""
Shows the usage of the matplotlib GUI

Needs at least Python 3.5
"""

from __future__ import division, print_function, unicode_literals


import datetime
import spotpy
from spotpy.gui.mpl import GUI
from spotpy.examples.spot_setup_hymod_python import spot_setup
#from spotpy.examples.spot_setup_cmf_lumped import SingleStorage

if __name__ == '__main__':
    # Create the model
    model = spot_setup()
    #spotpy.describe.setup(model)
    gui = GUI(model)
    gui.show()

#!/usr/bin/env python3
import sys
import os
sys.path.append("./src/")

try:
	import PyQt4
except:
	print("You need to install PyQt 4 for Python 3!\nsudo apt-get install python3-pyqt4")
	sys.exit(1)

from bp.Tools.IDE.bp_ide import *
os.chdir("./src/bp/Tools/IDE/")
main()

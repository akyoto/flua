#!/usr/bin/env python3
import sys
import os

if os.name == "nt":
	appendPath = (os.path.abspath("src/") + "/").replace("\\", "/")
	pyqtPath = (os.path.abspath("../python/Lib/site-packages/PyQt4")).replace("\\", "/")
	print(sys.version)
	print(appendPath)
	print(pyqtPath)
	sys.path.append(pyqtPath)
else:
	appendPath = (os.path.abspath("src/") + "/")

sys.path.append(appendPath)

try:
	import PyQt4
except:
	print("You need to install PyQt 4 for Python 3!\nsudo apt-get install python3-pyqt4")
	sys.exit(1)

from bp.Tools.IDE.bp_ide import *
os.chdir("./src/bp/Tools/IDE/")
main()

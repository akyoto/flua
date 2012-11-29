#!/usr/bin/env python3
####################################################################
# Header
####################################################################
# Flua IDE
# 
# Website: flua-lang.org
# Started: 26.04.2012 (Thu, Apr 26 2012)

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
# 
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import sys
import os

scriptPath = os.path.dirname(os.path.realpath(__file__)) + "/"

if os.name == "nt":
	scriptPath = scriptPath.replace("\\", "/")
	appendPath = scriptPath + "src/"
	pyqtPath = (os.path.abspath(scriptPath + "../python/Lib/site-packages/PyQt4"))
	sys.path.append(pyqtPath)
	print(sys.version)
else:
	appendPath = (scriptPath + "src/")

####################################################################
# Temporarily add the module directory to PATH
####################################################################
sys.path.append(appendPath)

####################################################################
# PyQt4 installed?
####################################################################
try:
	import PyQt4
except:
	print("You need to install PyQt 4 for Python 3!\nsudo apt-get install python3-pyqt4")
	sys.exit(1)

####################################################################
# They see me runnin'. They hatin'.
####################################################################
from flua.Tools.IDE.flua_ide import *
os.chdir(scriptPath + "src/flua/Tools/IDE/")

if __name__ == "__main__":
	# Modes
	MODE_RUN = 0
	MODE_INSPECT = 1
	MODE_PROFILE = 2
	
	# Current mode
	FLUA_STUDIO_MODE = MODE_RUN
	
	# Let's go!
	if FLUA_STUDIO_MODE == MODE_RUN:
		main()
	elif FLUA_STUDIO_MODE == MODE_INSPECT:
		os.system("pyprof2calltree -i /home/eduard/Projects/flua.prof -k")
	elif FLUA_STUDIO_MODE == MODE_PROFILE:
		import cProfile
		cProfile.run("main(multiThreading = False)", "/home/eduard/flua.prof")
		os.system("pyprof2calltree -i /home/eduard/Projects/flua.prof -k")

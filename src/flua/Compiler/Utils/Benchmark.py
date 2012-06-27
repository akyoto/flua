####################################################################
# Header
####################################################################
# File:		Benchmarking utilities
# Author:   Eduard Urbach

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
import time

####################################################################
# Classes
####################################################################
class Benchmarkable:
	def __init__(self):
		self.benchmarkName = ""
		self.benchmarkTimerStart = 0
		self.benchmarkTimerEnd = 0
	
	def startBenchmark(self, name = ""):
		self.benchmarkName = name
		self.benchmarkTimerStart = time.time()
		
	def endBenchmark(self):
		self.benchmarkTimerEnd = time.time()
		buildTime = self.benchmarkTimerEnd - self.benchmarkTimerStart
		
		if self.benchmarkName:
			bName = self.benchmarkName + ":"
		else:
			bName = ""
		print((bName).ljust(69) + str(int(buildTime * 1000)).rjust(7) + " ms")
		
		return int(buildTime * 1000)

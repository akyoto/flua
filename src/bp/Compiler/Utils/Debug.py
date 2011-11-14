####################################################################
# Header
####################################################################
# Debugging functions

####################################################################
# License
####################################################################
# This file is part of Blitzprog.

# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Global
####################################################################

dbgTabLevel = 0

####################################################################
# Classes
####################################################################
class CompilerException(Exception):
	
	def __init__(self, value):
		self.value = value
		self.line = -1
		
	def getMsg(self):
		return self.value
		
	def getLine(self):
		return self.line
		
	def setLine(self, line):
		self.line = line
		
	def __str__(self):
		return repr(self.value)

def CompilerWarning(msg):
	print("[Warning] " + msg)

####################################################################
# Functions
####################################################################
def debug(msg):
	print("\t" * dbgTabLevel + str(msg))
	
def debugPush():
	global dbgTabLevel
	dbgTabLevel += 1
	
def debugPop():
	global dbgTabLevel
	dbgTabLevel -= 1

def debugStop():
	import pdb
	pdb.set_trace()

def printTraceback():
	import traceback
	traceback.print_exc()
	
def compilerWarning(msg):
	print("[Warning] " + msg)
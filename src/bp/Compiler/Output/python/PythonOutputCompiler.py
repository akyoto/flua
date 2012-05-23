####################################################################
# Header
####################################################################
# Target:   Python 3 Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
# 
# This file is part of Blitzprog.
# 
# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from bp.Compiler.Output.BaseOutputCompiler import *
from bp.Compiler.Output.python.PythonOutputFile import *

####################################################################
# Classes
####################################################################
class PythonOutputCompiler(BaseOutputCompiler):
	
	def __init__(self, inpCompiler):
		super().__init__(inpCompiler)
		
	def compile(self, inpFile):
		pyOut = PythonOutputFile(self, inpFile.getFilePath(), inpFile.getRoot())
		self.genericCompile(inpFile, pyOut)
		
	def writeToFS(self):
		pass
		
	def getExePath(self):
		return ""
		
	def build(self, compilerFlags = [], fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		return 0
		
	def getTargetName(self):
		return "Python 3"

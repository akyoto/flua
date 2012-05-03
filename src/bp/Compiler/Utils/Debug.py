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
		
	def getMsg(self):
		return self.value
	
	def setMsg(self, msg):
		self.value = msg
		
	def __str__(self):
		return self.getMsg()

class InputCompilerException(CompilerException):
	
	def __init__(self, value, inpFile):
		#super.__init__(value)
		self.setMsg(value)
		self.inpFile = inpFile
		
	def getLine(self):
		return self.inpFile.getLastLine()
		
	def getLineNumber(self):
		return self.inpFile.getLastLineCount()
		
	def getFilePath(self):
		return self.inpFile.getFilePath()
		
	def __str__(self):
		filePath = self.inpFile.getFilePath()
		line = self.getLine()
		lineCount = self.getLineNumber()
		sep = "\n" + "-" * (80) + "\n"
		return sep + "In " + filePath + (" [line %d]" % lineCount) + sep + line + sep + self.getMsg() + sep

class PostProcessorException(CompilerException):
	
	def __init__(self, value, filePath):
		self.setMsg(value)
		self.filePath = filePath
		
	def __str__(self):
		return self.filePath + ":\n" + self.getMsg()
 
class OutputCompilerException(CompilerException):
	
	def __init__(self, value, outFile):
		#super.__init__(value)
		self.setMsg(value)
		self.outFile = outFile
		
	def getFilePath(self):
		return self.outFile.getFilePath()
		
	def getLineNumber(self):
		# TODO: Implement getLineNumber
		return 1
		
	def getLastParsedNode(self):
		return self.outFile.getLastParsedNode()
		
	def __str__(self):
		basicSep = "-" * (80) + "\n"
		sep = "\n" + basicSep
		
		filePath = self.outFile.getFilePath()
		node = self.outFile.getLastParsedNode()
		nodeXML = ""
		nodeExpr = ""
		nodeToOriginalLine = self.outFile.nodeToOriginalLine
		if node and nodeToOriginalLine:
			while not node in nodeToOriginalLine:
				node = node.parentNode
			
			nodeXML = node.toprettyxml()
			nodeExpr = nodeToOriginalLine[node] + sep
		
		return sep + "In " + filePath + sep + node.toprettyxml() + basicSep + nodeExpr + self.getMsg() + sep

def CompilerWarning(msg):
	print("[Warning] " + msg)

####################################################################
# Functions
####################################################################
def debug(msg):
	pass#print("\t" * dbgTabLevel + str(msg))
	
def debugPP(msg):
	pass#print("\t" * dbgTabLevel + str(msg))
	
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

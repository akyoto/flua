####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
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
from Utils import *
import codecs

####################################################################
# Classes
####################################################################
class CPPOutputCompiler:
	
	def __init__(self, inpCompiler):
		self.inputCompiler = inpCompiler
		self.inputFiles = inpCompiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.projectDir = self.inputCompiler.projectDir
	
	def compile(self):
		for inpFile in self.inputFiles:
			cppOut = CPPOutputFile(self, inpFile)
			cppOut.compile()
			self.compiledFiles[inpFile] = cppOut
	
	def writeToFS(self, dirOut):
		dirOut = fixPath(os.path.abspath(dirOut)) + "/"
		
		for cppFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + ".cpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				outStream.write(cppFile.getCode())
	
	def build(self):
		pass
	
class CPPOutputFile:
	
	def __init__(self, compiler, inpFile):
		self.compiler = compiler
		self.file = inpFile.file
		self.root = inpFile.getRoot()
		self.codeNode = self.root.getElementsByTagName("code")[0]
		self.topLevel = ""
		
	def compile(self):
		print("Output: " + self.file)
		
		for node in self.codeNode.childNodes:
			if isTextNode(node):
				self.topLevel += node.nodeValue
			elif node.tagName == "call":
				self.topLevel += self.parseExpr(node.getElementsByTagName("function")[0].childNodes[0]) + ";\n";
		
	def parseExpr(self, node):
		if isTextNode(node):
			return node.nodeValue
		
	def getCode(self):
		return self.topLevel
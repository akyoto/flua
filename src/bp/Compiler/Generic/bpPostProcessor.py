####################################################################
# Header
####################################################################
# bp XML post processing unit

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
# Imports
####################################################################
from Utils import *

####################################################################
# Classes
####################################################################
class BPClass:
	
	def __init__(self, name):
		self.name = name

class BPPostProcessor:
	
	def __init__(self, compiler):
		self.inputCompiler = compiler
		self.inputFiles = compiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.classes = {}
	
	def process(self, inpFile):
		bpOut = BPPostProcessorFile(self, inpFile)
		self.compiledFiles[inpFile] = bpOut
		
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.process(inFile)
		
		bpOut.process()

class BPPostProcessorFile:
	
	def __init__(self, processor, inpFile):
		self.processor = processor
		self.inpFile = inpFile
		
	def process(self):
		print("Processing: " + self.inpFile.file)
		
		self.findDefinitions(getElementByTagName(self.inpFile.root, "code"))
		self.processNode(getElementByTagName(self.inpFile.root, "code"))
		
		print(self.inpFile.doc.toprettyxml())
		
	def findDefinitions(self, node):
		for child in node.childNodes:
			self.findDefinitions(child)
		
		if isTextNode(node):
			return
		elif node.tagName == "class":
			className = getElementByTagName(node, "name").childNodes[0].nodeValue
			
			# TODO: Class extending
			self.processor.classes[className] = BPClass(className)
		
	def processNode(self, node):
		for child in node.childNodes:
			self.processNode(child)
		
		if isTextNode(node):
			return
		elif node.tagName == "call":
			funcNameNode = getElementByTagName(node, "function").childNodes[0]
			
			funcName = ""
			if isTextNode(funcNameNode):
				funcName = funcNameNode.nodeValue
			elif funcNameNode.tagName == "template-call":
				funcName = funcNameNode.childNodes[0].childNodes[0].nodeValue
			
			if funcName in self.processor.classes:
				node.tagName = "new"
				getElementByTagName(node, "function").tagName = "type"
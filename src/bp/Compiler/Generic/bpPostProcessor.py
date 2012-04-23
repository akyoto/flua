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
		self.dataDeps = dict()
		
	def process(self):
		print("Processing: " + self.inpFile.file)
		
		self.findDefinitions(getElementByTagName(self.inpFile.root, "code"))
		self.processNode(getElementByTagName(self.inpFile.root, "code"))
		
		if not self.inpFile.file.endswith("Core.bpc"):
			pass#print(self.inpFile.doc.toprettyxml())
		
	def findDefinitions(self, node):
		for child in node.childNodes:
			self.findDefinitions(child)
		
		if isTextNode(node):
			return
		elif node.tagName == "class":
			className = getElementByTagName(node, "name").childNodes[0].nodeValue
			
			# TODO: Class extending
			self.processor.classes[className] = BPClass(className)
		
	def getInstructionDependencies(self, node):
		if isTextNode(node):
			name = node.nodeValue
			if isBPStringIdentifier(name):
				return []
			if isNumeric(name):
				return []
			if name[0].isupper():
				return []
			return [name]
		elif node.tagName == "call": # Ignore function name, only parse parameters
			return self.getInstructionDependencies(getElementByTagName(node, "parameters"))
		elif node.tagName == "return":
			return self.getInstructionDependencies(node.childNodes[0])
		
		deps = list()
		for child in node.childNodes:
			deps = deps + self.getInstructionDependencies(child)
		return deps
		
	def processNode(self, node):
		for child in node.childNodes:
			self.processNode(child)
		
		if isTextNode(node):
			return
		elif node.tagName.startswith("assign"):
			# DTree
			op1 = node.childNodes[0].childNodes[0]
			op2 = node.childNodes[1].childNodes[0]
			
			deps = self.getInstructionDependencies(op2)
			if node.tagName.startswith("assign-"):
				deps = deps + self.getInstructionDependencies(op1)
			if deps:
				self.dataDeps[node] = deps
			
			debugPP(tagName(op1) + " |--[" + node.tagName + "]--> " + tagName(op2))
			
			# Check
			if node.tagName == "assign" and isElemNode(op2) and op2.tagName == "template-call":
				raise CompilerException("You forgot the brackets to initialize the object")
		elif node.tagName == "call":
			funcNameNode = getElementByTagName(node, "function").childNodes[0]
			
			deps = self.getInstructionDependencies(node)
			if deps:
				self.dataDeps[node] = deps
			
			funcName = ""
			if isTextNode(funcNameNode):
				funcName = funcNameNode.nodeValue
			elif funcNameNode.tagName == "template-call":
				funcName = funcNameNode.childNodes[0].childNodes[0].nodeValue
			
			if funcName in self.processor.classes: #or funcName == "Actor":
				node.tagName = "new"
				getElementByTagName(node, "function").tagName = "type"
		elif node.tagName == "return":
			# Data dependency
			deps = self.getInstructionDependencies(node)
			if deps:
				self.dataDeps[node] = deps
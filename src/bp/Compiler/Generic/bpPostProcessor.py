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

class DTree:
	
	def __init__(self, name, instruction):
		self.name = name
		self.instruction = instruction
		self.dependencies = list()
		self.strength = 1
		self.parents = list()
		self.vars = set()
		self.functions = set()
		
	def addVar(self, name):
		self.vars.add(name)
		
	def addFunction(self, name):
		self.functions.add(name)
		
	def addTree(self, dTreeObj):
		self.dependencies.append(dTreeObj)
		dTreeObj.parents.append(self)
		
	def removeTree(self, dTreeObj):
		self.dependencies.remove(dTreeObj)
		dTreeObj.parents.remove(self)
		
	def setInstruction(self, inst):
		self.instruction = inst
		
	def printNodes(self, tabLevel = 0):
		if tabLevel > 0:
			sep = "|_"
		else:
			sep = ""
		print("  " * tabLevel + sep + "[" + self.name + "]")
		for node in self.dependencies:
			node.printNodes(tabLevel + 1)

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
		self.dTrees = dict() # Node -> DTree
		self.dTreeByFunctionName = dict() # String -> DTree
		self.lastOccurence = dict() # String -> DTree
		self.currentDTree = None
		
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
		
	def getInstructionDependencies(self, tree, xmlNode):
		if isTextNode(xmlNode):
			name = xmlNode.nodeValue
			if isBPStringIdentifier(name):
				return
			if isNumeric(name):
				return
			if name[0].isupper():
				return
			
			if name in self.lastOccurence:
				varTree = self.lastOccurence[name]
				tree.addVar(name)
				if len(varTree.parents) == 1 and varTree.parents[0] == self.currentDTree:
					self.currentDTree.removeTree(varTree)
				tree.addTree(varTree)
			elif name in self.dTreeByFunctionName:
				tree.addFunction(name)
				tree.addTree(self.dTreeByFunctionName[name])
		elif xmlNode.tagName == "access":
			# TODO: Parse it
			return
		elif xmlNode.tagName == "call": # Ignore function name, only parse parameters
			self.getInstructionDependencies(tree, getElementByTagName(xmlNode, "parameters"))
		elif xmlNode.tagName == "return":
			self.getInstructionDependencies(tree, xmlNode.childNodes[0])
		
		for child in xmlNode.childNodes:
			self.getInstructionDependencies(tree, child)
		
	def getVarName(self, node):
		if isTextNode(node):
			return node.nodeValue
		else:
			# TODO: Access
			return "UNKNOWN_VAR_NAME"
		
	def processNode(self, node, depth = 0):
		hasSetCurrentTree = False
		if isElemNode(node) and node.tagName == "function":
			nameNode = getElementByTagName(node, "name")
			if nameNode:
				funcName = nameNode.childNodes[0].nodeValue
				self.currentDTree = DTree(funcName, node)
				self.dTreeByFunctionName[funcName] = self.currentDTree
				hasSetCurrentTree = True
			else:
				# Probably a call
				pass
		
		# Process child nodes
		for child in node.childNodes:
			self.processNode(child, depth + 1)
		
		# Reset
		if hasSetCurrentTree:
			self.currentDTree = None
		
		# Process
		if isTextNode(node):
			return
		elif node.tagName.startswith("assign"):
			# DTree
			op1 = node.childNodes[0].childNodes[0]
			op2 = node.childNodes[1].childNodes[0]
			
			thisOperation = DTree(self.getVarName(op1), node)
			self.getInstructionDependencies(thisOperation, op2)
			if node.tagName.startswith("assign-"):
				self.getInstructionDependencies(thisOperation, op1)
			
			self.dTrees[node] = thisOperation
			self.lastOccurence[thisOperation.name] = thisOperation
			
			if self.currentDTree:
				self.currentDTree.addTree(thisOperation)
			
			#if depth == 1:
			#	self.dTree.addTree(thisOperation)
			
			debugPP(tagName(op1) + " |--[" + node.tagName + "]--> " + tagName(op2))
			
			# Check
			if node.tagName == "assign" and isElemNode(op2) and op2.tagName == "template-call":
				raise CompilerException("You forgot the brackets to initialize the object")
		elif node.tagName == "call":
			funcNameNode = getElementByTagName(node, "function").childNodes[0]
			
			funcName = ""
			if isTextNode(funcNameNode):
				funcName = funcNameNode.nodeValue
			elif funcNameNode.tagName == "template-call":
				funcName = funcNameNode.childNodes[0].childNodes[0].nodeValue
			
			if funcName in self.processor.classes: #or funcName == "Actor":
				node.tagName = "new"
				getElementByTagName(node, "function").tagName = "type"
			
			# TODO: Is funcName appropriate?
			#funcTree = self.dTree #DTree(funcName, node)
			#self.getInstructionDependencies(funcTree, node)
			
			#if depth == 1:
			#	self.dTree.addTree(funcTree)
		elif node.tagName == "return":
			# Data dependency
			#self.getInstructionDependencies(DTree("return", node), node)
			pass
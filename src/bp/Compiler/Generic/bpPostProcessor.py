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
# Global
####################################################################
# (time for 100000000 operations) / 10 - 30
dTreeByFunctionName = dict() # String -> DTree
dTreeByNode = dict() # Node -> DTree
defaultInstructionTime = 1
operationTimes = {
	# Operators
	"call.unused" : 5,
	"template-call" : 0,
	"access" : 1,
	"index.unused" : 1,
	"call" : 5,
	"index" : 1,
	"unmanaged" : 1,
	"declare-type" : 0,
	"not" : 1,
	"negative" : 0,
	"greater-or-equal" : 1,
	"greater" : 1,
	"less-or-equal" : 1,
	"less" : 1,
	"equal" : 1,
	"not-equal" : 1,
	"almost-equal" : 1,
	"and" : 1,
	"or" : 1,
	"add" : 2,
	"subtract" : 2,
	"multiply" : 18,
	"divide" : 26,
	"divide-floor" : 15,
	"modulo" : 8,
	"shift-left" : 5,
	"shift-right" : 5,
	"assign-add" : 6,
	"assign-subtract" : 6,
	"assign-multiply" : 10,
	"assign-divide" : 15,
	"assign-shift-left" : 6,
	"assign-shift-right" : 6,
	"assign" : 1.2,
	"flow-delayed-to" : 1,
	"flow-delayed-from" : 1,
	"flow-to" : 1,
	"flow-from" : 1,
	"separate" : 1,
	
	# Keywords
	"return" : 1,
	
	# Extern functions
	"bp_print" : 30,
	"bp_println" : 30,
	"bp_usleep" : 100,
	"bp_sizeOf" : 0,
	"bp_systemTime" : 13970,
	"bp_systemCPUClock" : 5290,
	"bp_swap" : 47,
	"bp_strlen" : 870,
	"bp_copyMem" : 400,	#guess
	"bp_cos" : 594,
	"bp_sin" : 684,
	"bp_atan2" : 910,
	"bp_log" : 503,
	"bp_log10" : 525,
	"bp_sqrt" : 252,
}

# Times
floatAccessTime = 2	# Float
intAccessTime = 0.5	# Int
variableAccessTime = 2.4 # Variables
dependencyDepthCost = 3

####################################################################
# Functions
####################################################################

def getInstructionTime(xmlNode):
	global variableAccessTime
	
	if isinstance(xmlNode, list):
		t = 0
		for child in xmlNode:
			op = child.parentNode
			if op.tagName.startswith("assign"):
				op1 = child
				op2 = op.childNodes[1].childNodes[0]
				old = variableAccessTime
				
				variableAccessTime = 1
				op1Time = getInstructionTime(op1)
				
				variableAccessTime = old
				op2Time = getInstructionTime(op2)
				
				return op1Time + op2Time #op1Time * 0.5 + op2Time * 5
			else:
				t += getInstructionTime(child)
		return t
	
	if isTextNode(xmlNode):
		name = xmlNode.nodeValue
		if isNumeric(name):
			if name.find(".") != -1:
				return floatAccessTime	# Float
			else:
				return intAccessTime	# Int
		return variableAccessTime	# Variable access
	
	nodeName = xmlNode.tagName
	if nodeName == "function":
		code = getElementByTagName(xmlNode, "code")
		if code:
			return getInstructionTime(code.childNodes)
	elif nodeName in operationTimes:
		tOP = operationTimes[nodeName]
		return tOP + getInstructionTime(xmlNode.childNodes)
	elif xmlNode.childNodes: #isinstance(xmlNode, xml.dom.minidom.Node) and
		return getInstructionTime(xmlNode.childNodes)
	elif xmlNode.tagName == "parameters":
		pass
	else:
		raise CompilerException(nodeName)
	
	return 0

def getVarName(node):
	if isTextNode(node):
		return node.nodeValue
	elif node.tagName == "access":
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		return getVarName(op1) + "." + getVarName(op2)
	elif node.tagName == "declare-type":
		op1 = node.childNodes[0].childNodes[0]
		return getVarName(op1)
	else:
		raise CompilerException("Could not find out the variable name for node of type '%s'" % (node.tagName))

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
		self.parents = list()
		self.vars = set()
		self.functionCalls = list()
		self.costCalculationRunning = False
		self.timeNeeded = 0
		
	def getParentsDepth(self):
		return max(self.getParentsDepthPriv() - 1, 0)
		
	def getParentsDepthPriv(self):
		depthParents = 0
		
		for par in self.parents:
			if not par.isFunctionDefinition():
				depth = par.getParentsDepthPriv()
				if depth > depthParents:
					depthParents = depth
		
		return depthParents + 1
		
	def isFunctionDefinition(self):
		return self.instruction.tagName == "function"
		
	def addVar(self, name):
		if not name in self.vars:
			self.vars.add(name)
			return True
		
		return False
		
	def addFunctionCall(self, name):
		self.functionCalls.append(name)
		
	def addTree(self, dTreeObj):
		self.dependencies.append(dTreeObj)
		dTreeObj.parents.append(self)
		
	def removeTree(self, dTreeObj):
		self.dependencies.remove(dTreeObj)
		dTreeObj.parents.remove(self)
		
	def setInstruction(self, inst):
		self.instruction = inst
		
	def updateTime(self):
		# TODO: Recursion check: Prevents endless loops?
		if self.costCalculationRunning:
			return defaultInstructionTime * 2
		self.costCalculationRunning = True
		
		# Instruction
		if self.instruction and not self.isFunctionDefinition():
			myCost = getInstructionTime(self.instruction)
		else:
			myCost = defaultInstructionTime
		
		# Dependencies
		for dep in self.dependencies:
			if len(dep.parents) <= 1 or dep.parents[0] == self:
				myCost += dep.getTime()
		
		# Depth
		depth = self.getParentsDepth()
		myCost += depth * dependencyDepthCost
		
		# Function calls
		for call in self.functionCalls:
			if call.startswith("bp_"):
				myCost += operationTimes[call]
			else:
				tree = dTreeByFunctionName[call]
				myCost += tree.getTime()
		
		self.costCalculationRunning = False
		self.timeNeeded = myCost
	
	def getTime(self):
		if self.timeNeeded == 0:
			self.updateTime()
		return self.timeNeeded
		
	def getTimeMS(self):
		return self.getTime() * 10000000
		
	def getGraphVizCode(self):
		connections = ""
		myLabel = self.name
		myID = fixID(myLabel) + str(id(self.instruction))
		depLabel = ""
		depID = ""
		
		for dep in self.dependencies:
			depLabel = dep.name
			depID = fixID(depLabel) + str(id(dep.instruction))
			connections += "%s -> %s;\n" % (depID, myID)
			graph = dep.getGraphVizCode()
			connections += graph
		
		connections += "%s [label=\"%s\", style=filled, fillcolor=\"#cccccc\"];\n" % (myID, myLabel)
		return connections
		
	def getFullGraphVizCode(self):
		connections, specialID = self.getGraphVizCode()
		return "digraph %s {%s}" % (self.name, connections)
		
	def printNodes(self, tabLevel = 0):
		if tabLevel > 0:
			sep = "∟"
		else:
			sep = ""
		
		depth = ""
		depthCount = self.getParentsDepth()
		if depthCount > 0:
			depth = " -> %d" % (depthCount)
		
		print("  " * tabLevel + sep + ("[%s] (%d)%s (%s)" % (self.name, self.getTime(), depth, str(self.functionCalls))))
		
		#print("Deps: " + str(len(self.dependencies)))
		#print("Pars: " + str(len(self.parents)))
		#print("Vars: " + str(len(self.vars)))
		#print("Func: " + str(len(self.functionCalls)))
		#print("")
		
		for node in self.dependencies:
			if node.parents[0] == self:
				node.printNodes(tabLevel + 1)
			else:
				print("  " * (tabLevel + 1) + sep + ("[%s]>") % node.name)

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
		self.lastOccurenceStack = list()
		self.lastOccurence = dict() # String -> DTree
		self.currentDTree = None
		self.currentClassName = ""
		
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
				if tree.addVar(name):
					varTree = self.lastOccurence[name]
					if len(varTree.parents) == 1 and varTree.parents[0] == self.currentDTree:
						self.currentDTree.removeTree(varTree)
					tree.addTree(varTree)
		elif xmlNode.tagName == "access":
			# TODO: Parse it
			op1 = xmlNode.childNodes[0].childNodes[0]
			op2 = xmlNode.childNodes[1].childNodes[0]
			#varName = tagName(op1) + "." + tagName(op2)
			self.getInstructionDependencies(tree, op1)
			self.getInstructionDependencies(tree, op2)
			return
		elif xmlNode.tagName == "call": # Ignore function name, only parse parameters
			funcName = getElementByTagName(xmlNode, "function").childNodes[0].nodeValue
			if funcName:
				tree.addFunctionCall(funcName)
			#tree.addTree(self.dTreeByFunctionName[name])
			self.getInstructionDependencies(tree, getElementByTagName(xmlNode, "parameters"))
			return
		
		# Childs
		for child in xmlNode.childNodes:
			self.getInstructionDependencies(tree, child)
		
	def processNode(self, node, depth = 0):
		hasSetCurrentTree = False
		hasSetCurrentClassName = False
		if isElemNode(node):
			if node.tagName == "function" and node.parentNode.tagName != "call":
				nameNode = getElementByTagName(node, "name")
				if nameNode:
					self.lastOccurenceStack.append(self.lastOccurence)
					self.lastOccurence = dict()
					funcName = nameNode.childNodes[0].nodeValue
					if self.currentClassName:
						funcName = self.currentClassName + "." + funcName
					debugPP("Function definition: " + funcName)
					if funcName:
						self.currentDTree = DTree(funcName, node)
						dTreeByFunctionName[funcName] = self.currentDTree
						hasSetCurrentTree = True
			elif node.tagName == "class":
				self.currentClassName = getElementByTagName(node, "name").childNodes[0].nodeValue
				hasSetCurrentClassName = True
				
		# Process child nodes
		for child in node.childNodes:
			self.processNode(child, depth + 1)
		
		# Reset
		if hasSetCurrentTree:
			self.currentDTree = None
			self.lastOccurence = self.lastOccurenceStack.pop()
		if hasSetCurrentClassName:
			self.currentClassName = ""
		
		# Process
		if isTextNode(node):
			return
		elif node.tagName.startswith("assign"):
			# DTree
			op1 = node.childNodes[0].childNodes[0]
			op2 = node.childNodes[1].childNodes[0]
			
			thisOperation = DTree(getVarName(op1), node)
			self.getInstructionDependencies(thisOperation, op2)
			if node.tagName.startswith("assign-"):
				self.getInstructionDependencies(thisOperation, op1)
			
			dTreeByNode[node] = thisOperation
			self.lastOccurence[thisOperation.name] = thisOperation
			
			if self.currentDTree:
				self.currentDTree.addTree(thisOperation)
			
			#if depth == 1:
			#	self.dTree.addTree(thisOperation)
			
			#if self.currentDTree:
			#	debugPP("%s (%s)" % (self.currentDTree.name, self.currentDTree.dependencies[0].name))
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
			#elif funcName:
			#	thisOperation = DTree("Call.Procedure: " + funcName, node)
			#	self.getInstructionDependencies(thisOperation, node)
			#	dTreeByNode[node] = thisOperation
			#	if self.currentDTree:
			#		self.currentDTree.addTree(thisOperation)
			
			# TODO: Is funcName appropriate?
			#funcTree = self.dTree #DTree(funcName, node)
			#self.getInstructionDependencies(funcTree, node)
			
			#if depth == 1:
			#	self.dTree.addTree(funcTree)
		elif node.tagName == "return":
			# Data dependency
			thisOperation = DTree("return value", node)
			self.getInstructionDependencies(thisOperation, node)
			if self.currentDTree:
				self.currentDTree.addTree(thisOperation)
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
from bp.Compiler.Utils import *
from bp.Compiler.Input import *

####################################################################
# Global
####################################################################
# (time for 100000000 operations) / 10 - 30
defaultInstructionTime = 1
operationTimes = {
	# Operators
	#"call.unused" : 5,
	"template-call" : 0,
	"access" : 1,
	"index.unused" : 1,
	#"call" : 5,
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
}

# Extern functions
externOperationTimes = {
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
minimumTimeForParallelization = 1

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
	elif nodeName == "call":
		funcNameNode = getFuncNameNode(xmlNode)
		funcName = funcNameNode.nodeValue
		if funcName:
			debugPP("USING TIME OF " + funcName)
			if funcName in externOperationTimes:
				return externOperationTimes[funcName]
				
			# TODO: Add params
			funcNamePolymorphized = funcName	
			
			return self.processor.getDTreeByPolyFuncName(funcNamePolymorphized).getTime()
	elif xmlNode.childNodes: #isinstance(xmlNode, xml.dom.minidom.Node) and
		return getInstructionTime(xmlNode.childNodes)
	elif xmlNode.tagName == "parameters":
		pass
	else:
		raise CompilerException(nodeName)
	
	return 0
	
def automaticallyParallelize(dTreeDict):
	for dTree in dTreeDict.values():
		if len(dTree.parents) == 0:
			spawnPoint = dTree.getNextThreadSpawnPoint()
			#if spawnPoint is None:
			#	return False
			if spawnPoint:#dTree.name.find("paraFunc") != -1:
				print("---")
				dTree.printNodes()
				print("---")
				

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
		#self.functionCalls = list()
		self.costCalculationRunning = False
		self.timeNeeded = 0
		
	def hasSideEffects(self):
		for dep in self.dependencies:
			if dep.hasSideEffects():
				return True
		
		return self.instructionHasSideEffects()
		
	def instructionHasSideEffects(self):
		node = self.instruction
		nodeName = node.tagName
		if nodeName == "call":
			funcName = getCalledFuncName(node)
		
	def worthParallelizing(self):
		return self.getTime() >= minimumTimeForParallelization
		
	def canParallelizeSubtrees(self):
		if len(self.dependencies) < 2:
			return False
		
		numSideEffects = 0
		for dep in self.dependencies:
			if dep.hasSideEffects():
				numSideEffects += 1
				if numSideEffects > 1:
					return False
		
		return True
		
	def getNextThreadSpawnPoint(self):
		if self.canParallelizeSubtrees():
			return self
		
		for dep in self.dependencies:
			dTree = dep.getNextThreadSpawnPoint()
			if dTree is not None:
				return dTree
		
		return None
		
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
		
	#def addFunctionCall(self, name):
	#	self.functionCalls.append(name)
		
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
		#for call in self.functionCalls:
		#	if call.startswith("bp_"):
		#		myCost += operationTimes[call]
		#	else:
		#		tree = self.processor.dTreeByFunctionName[call]
		#		myCost += tree.getTime()
		
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
		myID = "node" + str(id(self.instruction))
		depLabel = ""
		depID = ""
		
		for dep in self.dependencies:
			depLabel = dep.name
			depID = "node" + str(id(dep.instruction))
			connections += "%s -> %s;\n" % (depID, myID)
			graph = dep.getGraphVizCode()
			connections += graph
		
		connections += "%s [label=\"%s\", style=filled, fillcolor=\"#cccccc\"];\n" % (myID, myLabel)
		return connections
		
	def getFullGraphVizCode(self):
		connections = self.getGraphVizCode()
		return "digraph %s {%s}" % (self.name, connections)
		
	def getDependencyPreview(self, tabLevel = 0, includeTime = False, includeDepthCount = False):
		tab = "    "
		if tabLevel > 0:
			sep = "∟"
		else:
			sep = ""
		
		if self.canParallelizeSubtrees():
			sep = "➤"
		
		depth = ""
		if includeDepthCount:
			depthCount = self.getParentsDepth()
			if depthCount > 0:
				depth = " [Depth = %d]" % (depthCount)
		
		# Remove ()
		def fixNodeName(name):
			if name[0] == '(' and name[-1] == ')':
				return name[1:-1]
			return name
		
		instTime = ""
		if includeTime:
			instTime = "(" + str(self.getTime()) + ")"
		
		myInst = tab * tabLevel + sep + ("[%s] %s%s" % (fixNodeName(self.name), instTime, depth)) + "\n"
		
		#print("Deps: " + str(len(self.dependencies)))
		#print("Pars: " + str(len(self.parents)))
		#print("Vars: " + str(len(self.vars)))
		#print("Func: " + str(len(self.functionCalls)))
		#print("")
		
		depInst = ""
		for node in self.dependencies:
			if node.parents[0] == self:
				depInst += node.getDependencyPreview(tabLevel + 1)
			else:
				depInst += tab * (tabLevel + 1) + sep + ("* [%s] *") % fixNodeName(node.name) + "\n"
		
		return myInst + depInst
		
	def printNodes(self, tabLevel = 0):
		print(self.getDependencyPreview(tabLevel))

class BPPostProcessor:
	
	def __init__(self, compiler = None):
		if compiler:
			self.inputCompiler = compiler
			self.inputFiles = compiler.getCompiledFiles()
			self.compiledInputFiles = dict()
		
		self.compiledFiles = dict()
		self.compiledFilesList = list()
		self.externFuncNameToMetaDict = dict()
		self.classes = {}
		self.mainFilePath = ""
		self.funcCount = 0
	
	def getFunctionCount(self):
		return self.funcCount
	
	def resetDTreesForFile(self, filePath):
		if not filePath in self.compiledFiles:
			return#raise CompilerException("%s has not been processed yet" % filePath)
		
		ppFile = self.compiledFiles[filePath]
		ppFile.resetDTreeByNode()
		ppFile.resetDTreesByFunctionName()
	
	def getDTreeByPolyFunctionName(self, polyFuncName):
		# TODO: Polymorphism
		return self.getFirstDTreeByFunctionName(polyFuncName)
	
	def getFirstDTreeByFunctionName(self, funcName):
		for ppFile in self.compiledFilesList:
			if funcName in ppFile.dTreesByFunctionName:
				# Return "first" item
				return next(iter(ppFile.dTreesByFunctionName[funcName].values()))
		return None
	
	def getDTreeByNode(self, node):
		for ppFile in self.compiledFilesList:
			if node in ppFile.dTreeByNode:
				return ppFile.dTreeByNode[node]
		return None
	
	def getFunctionsDict(self):
		funcs = dict()
		for ppFile in self.compiledFilesList:
			for funcName, funcVariations in ppFile.dTreesByFunctionName.items():
				if funcName.find('.') == -1:
					funcs[funcName] = funcVariations
		return funcs
	
	def setMainFile(self, path):
		self.mainFilePath = path
	
	def processExistingInputFile(self, inpFile):
		bpOut = BPPostProcessorFile(self, inpFile.root, inpFile.file)
		self.compiledInputFiles[inpFile] = bpOut
		
		for imp in inpFile.importedFiles:
			try:
				inFile = self.inputCompiler.getFileInstanceByPath(imp)
				if (not inFile in self.compiledInputFiles):
					self.processExistingInputFile(inFile)
			except:
				self.processFile(imp)
		
		bpOut.process()
		
	def getCompiledFiles(self):
		return self.compiledFiles
	
	def changeCompiledFilePath(self, oldPath, newPath):
		# TODO: Can we do this faster in Python?
		self.compiledFiles[newPath] = self.compiledFiles[oldPath]
		del self.compiledFiles[oldPath]
		self.compiledFiles[oldPath] = None
	
	def getCompiledFilesList(self):
		return self.compiledFilesList
	
	def getProjectDir(self):
		return extractDir(self.mainFilePath)
		
	def getFileInstanceByPath(self, filePath):
		return self.compiledFiles[filePath]
		
	def cleanUpFile(self, filePath):
		if filePath in self.compiledFiles:
			bpOut = self.compiledFiles.pop(filePath)
			del bpOut.root
			#del bpOut.dTreesByFunctionName
			del bpOut.dTreeByNode
			del bpOut.lastOccurence
			del bpOut.lastOccurenceStack
			self.compiledFilesList.remove(bpOut)
			del bpOut
		return
		
	def processFile(self, filePath):
		xmlCode = loadXMLFile(filePath)
		root = parseString(xmlCode).documentElement
		self.process(root, filePath)
		
	def process(self, root, filePath = ""):
		try:
			bpOut = BPPostProcessorFile(self, root, filePath)
			
			if filePath:
				if not self.compiledFiles:
					self.setMainFile(filePath)
				
				self.compiledFiles[filePath] = bpOut
				self.compiledFilesList.append(bpOut)
				#print("\n".join(self.compiledFiles))
				#print("----")
			
			# Get a list of imported files
			bpOut.updateImportedFiles()
			
			# Process imported files
			for importedFile in bpOut.getImportedFiles():
				if (not importedFile in self.compiledFiles):
					self.processFile(importedFile)
			
			# Process the actual file
			bpOut.processXML()
			
			return bpOut
		except CompilerException as e:
			raise PostProcessorException(str(e), filePath)

class BPPostProcessorFile:
	
	def __init__(self, processor, root, filePath = ""):
		self.processor = processor
		self.root = root
		self.lastOccurenceStack = list()
		self.lastOccurence = dict() # String -> DTree
		self.currentDTree = None
		self.currentClassName = ""
		self.filePath = filePath
		self.importedFiles = None
		self.funcCount = 0
		self.resetDTreesByFunctionName()
		self.resetDTreeByNode()
	
	def resetDTreesByFunctionName(self):
		self.processor.funcCount -= self.funcCount
		self.funcCount = 0
		self.dTreesByFunctionName = dict() # String -> DTree
	
	def resetDTreeByNode(self):
		self.dTreeByNode = dict() # Node -> DTree
		
	def addFunctionDTree(self, funcName, funcNamePolymorphized, dTree):
		self.dTreesByFunctionName[funcName][funcNamePolymorphized] = dTree
		self.funcCount += 1
		
	def updateImportedFiles(self):
		self.importedFiles = []
		header = getElementByTagName(self.root, "header")
		dependencies = getElementByTagName(header, "dependencies")
		for child in dependencies.childNodes:
			if child.nodeType != Node.TEXT_NODE and child.tagName == "import":
				importedModule = child.childNodes[0].nodeValue.strip()
				modulePath = getModulePath(importedModule, extractDir(self.filePath), self.processor.getProjectDir(), ".bp")
				if modulePath:
					self.importedFiles.append(modulePath)
				else:
					#print(importedModule, "|", self.filePath, "|", extractDir(self.filePath), "|", self.processor.getProjectDir())
					raise CompilerException("Module not found: %s" % importedModule)
		
	def getFilePath(self):
		return self.filePath
	
	def getRoot(self):
		return self.root
		
	def getImportedFiles(self):
		return self.importedFiles
		
	def nodeToText(self, node):
		return tagName(node)
		
	def process(self):
		print("Processing: " + self.filePath)
		
		self.processXML()
		
		#if not self.filePath.endswith("Core.bpc"):
		#	pass#print(self.inpFile.doc.toprettyxml())
		
	def processXML(self):
		self.findDefinitions(getElementByTagName(self.root, "code"))
		self.processNode(getElementByTagName(self.root, "code"))
		self.processor.funcCount += self.funcCount
		
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
			if not name:
				return
			if isBPStringIdentifier(name):
				return
			if isNumeric(name):
				return
			if name[0].isupper():
				return
			if name == "my":
				return
			
			if name in self.lastOccurence:
				if tree.addVar(name):
					# Get the DTree for the last occurence of the variable name
					varTree = self.lastOccurence[name]
					debugPP(varTree.instruction)
					
					# Walk the tree up until we get to the same code node
					# code
					#	|_ x = 7
					# 	|_ if x
					#		|_ a = 5
					#	|_ b = a
					# which means 'b = a' should not depend on 'a = 5'
					# but on 'if x'.
					# 
					# [b = a]
					#	|_ [if x]
					#		|_ [x = 7]
					# 
					# Note: [a = 5] disappears but this ain't a problem
					# because it is still a subnode of [if x] and therefore
					# is used for the parallelization process.
					#
					# But we need to take care that 'node' is on a higher
					# indentation level than 'me'.
					# 
					# We saved this level as 'depth' in the input module.
					#
					# First get the nodes:
					node = varTree.instruction
					me = tree.instruction
					
					# Retrieve the depth by going up the tree
					# until we find a node with depth information.
					nodeTmp = node
					while not nodeTmp.hasAttribute("depth"):
						nodeTmp = nodeTmp.parentNode
						
						if nodeTmp.tagName == "module":
							raise CompilerException("Node has no depth information: %s" % node.toxml())
						
					nodeDepth = nodeTmp.getAttribute("depth")
					
					# Do the same for 'my' node
					myTmp = me
					while not myTmp.hasAttribute("depth"):
						myTmp = myTmp.parentNode
						
						if myTmp.tagName == "module":
							raise CompilerException("Node has no depth information: %s" % me.toxml())
						
					myDepth = myTmp.getAttribute("depth")
					
					# Debugging
					#print(self.filePath)
					#if not nodeDepth:
					#	print("node depth info missing >>" + node.toprettyxml())
					#	
					#if not myDepth:
					#	print("my depth info missing >>" + me.toprettyxml())
					
					# If the depth of the dependency was higher...
					if int(nodeDepth) > int(myDepth):
						myParent = me.parentNode
						
						#print("Node:", node.toprettyxml())
						#print("Me  :", tree.instruction.toprettyxml())	
						oldNode = node
						
						# Retrieve the parent they have in common
						while node.parentNode and not node.parentNode.isSameNode(myParent):
							node = node.parentNode
						
						if not node.parentNode:
							node = oldNode#raise CompilerException("Could not retrieve dependency information for '%s'" % nodeToBPC(xmlNode))
					
					# Now we have a node, but we need a DTree
					if not node in self.dTreeByNode:
						raise CompilerException("DTree for %s wasn't saved" % node.toxml())
					
					dependsOnTree = self.dTreeByNode[node]
					
					# WTH ?!
					if len(dependsOnTree.parents) == 1 and dependsOnTree.parents[0] == self.currentDTree:
						self.currentDTree.removeTree(dependsOnTree)
					
					tree.addTree(dependsOnTree)
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
			#if funcName:
			#	tree.addFunctionCall(funcName)
			
			callTree = DTree(self.nodeToText(xmlNode), xmlNode)
			if tree:
				tree.addTree(callTree)
			self.dTreeByNode[xmlNode] = callTree
			#tree.addTree(self.self.processor.dTreeByFunctionName[name])
			self.getInstructionDependencies(callTree, getElementByTagName(xmlNode, "parameters"))
			return
		elif xmlNode.tagName == "parameter":
			#paramTree = DTree(nodeToBPC(xmlNode), xmlNode)
			
			#if isElemNode(xmlNode.childNodes[0]):
			#	tree.addTree(paramTree)
			#else:
			#self.getInstructionDependencies(tree, xmlNode.childNodes[0])
			pass
			#for child in xmlNode.childNodes:
			#	self.getInstructionDependencies(paramTree, child)
		elif xmlNode.hasAttribute("depth"):#xmlNode.tagName == "if-block" or xmlNode.tagName == "try-block":
			newTree = DTree(self.nodeToText(xmlNode), xmlNode)
			self.dTreeByNode[xmlNode] = newTree
		elif xmlNode.tagName == "code":
			#newTree = DTree(nodeToBPC(xmlNode), xmlNode)
			#if tree:
			#	tree.addTree(newTree)
			
			#if xmlNode.tagName in {"if-block", "try-block"}:
			#	print("Yikes!")
			#self.getInstructionDependencies(tree, getElementByTagName(xmlNode, "parameters"))
			#self.dTreeByNode[xmlNode] = newTree
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
						
						# TODO: Add params to name
						funcNamePolymorphized = funcName
						
						if not funcName in self.dTreesByFunctionName:
							self.dTreesByFunctionName[funcName] = dict()
						self.addFunctionDTree(funcName, funcNamePolymorphized, self.currentDTree)
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
			
			thisOperation = DTree(self.nodeToText(node), node)
			self.getInstructionDependencies(thisOperation, op2)
			if node.tagName.startswith("assign-"):
				self.getInstructionDependencies(thisOperation, op1)
			
			self.dTreeByNode[node] = thisOperation
			
			# Access
			varToAdd = op1
			while 1:
				self.lastOccurence[self.nodeToText(varToAdd)] = thisOperation
				# access
				if isElemNode(varToAdd) and varToAdd.tagName == "access":
					accessOp1 = self.nodeToText(varToAdd.childNodes[0].childNodes[0])
					accessOp2 = self.nodeToText(varToAdd.childNodes[1].childNodes[0])
					self.lastOccurence[accessOp1] = thisOperation
					self.lastOccurence[accessOp2] = thisOperation
					varToAdd = varToAdd.childNodes[0].childNodes[0] # varToAdd = accessOp1
				else:
					break
			
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
			#elif funcNameNode.tagName == "template-call":
			#	funcName = funcNameNode.childNodes[0].childNodes[0].nodeValue
			
			#if funcName in self.processor.classes: #or funcName == "Actor":
			#	node.tagName = "new"
			#	getElementByTagName(node, "function").tagName = "type"
			if funcName and tagName(node.parentNode) == "code":
				#thisOperation = DTree("Procedure: " + nodeToBPC(node), node)
				#self.getInstructionDependencies(thisOperation, node)
				#self.processor.dTreeByNode[node] = thisOperation
				#if self.currentDTree:
				#	self.currentDTree.addTree(thisOperation)
				self.getInstructionDependencies(self.currentDTree, node)
			
			# TODO: Is funcName appropriate?
			#funcTree = self.dTree #DTree(funcName, node)
			#self.getInstructionDependencies(funcTree, node)
			
			#if depth == 1:
			#	self.dTree.addTree(funcTree)
		elif node.hasAttribute("depth") and not node.tagName in {
					# Have no dependencies
					"class",
					"getter",
					"setter",
					"cast-definition",
					"function",
					
					# if-block
					"if",
					"else-if",
					"else",
					
					# try-block
					"try",
					"catch"
				}:
			# Data dependency
			#debugPP("Getting dependencies for %s..." % node.tagName)
			
			#debugPush()
			if node.tagName == "extern-function":
				funcName = getElementByTagName(node, "name").firstChild.nodeValue
				metaNode = getElementByTagName(node, "meta")
				if metaNode:
					self.processor.externFuncNameToMetaDict[funcName] = createMetaDictFromNode(metaNode)
				else:
					self.processor.externFuncNameToMetaDict[funcName] = dict()
			
			thisOperation = DTree("%s: %s" % (node.tagName, self.nodeToText(node).replace("\n", ":").replace("\t", "")), node)
			self.getInstructionDependencies(thisOperation, node)
			
			#debugPop()
			
			if self.currentDTree:
				#debugPP("New child:\n\t[%s]\n\tof\n\t[%s]" % (self.currentDTree.name, thisOperation.name))
				self.currentDTree.addTree(thisOperation)
				
			self.dTreeByNode[node] = thisOperation

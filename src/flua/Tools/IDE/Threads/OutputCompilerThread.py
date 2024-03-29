####################################################################
# Imports
####################################################################
from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
from multiprocessing import Process, Pipe
import collections

####################################################################
# Classes
####################################################################
class BPOutputCompilerThreadData:
	def __init__(self):
		self.mainNamespace = BaseNamespace("", None)
		self.mainNamespace.classes = dict()
		self.mainNamespace.functions = dict()
		self.mainNamespace.externFunctions = dict()
		self.mainNamespace.externVariables = dict()
		
		self.defines = dict()
		self.functionCount = -1
		
		self.exceptionMsg = ""
		self.exceptionLineNumber = -1
		self.exceptionFilePath = ""

class BPOutputCompilerThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		Benchmarkable.__init__(self)
		
		self.codeEdit = codeEdit
		self.bpIDE = codeEdit.bpIDE
		self.lastException = None
		self.numTasksHandled = 0
		self.version = 0
		
		self.currentProcess = None
		self.currentJobQueue = None
		self.currentJobResultsQueue = None
		
		# Higher recursion limit for Windows to accept bigger objects
		#if os.name == "nt":
		#	factor = 200
		#else:
		#	factor = 1
		#
		#sys.setrecursionlimit(sys.getrecursionlimit() * factor)
		
		# Call bpIDE.backgroundCompilerFinished when finished
		self.finished.connect(self.codeEdit.backgroundCompilerFinished)
		
	def startWith(self):
		if 1:#self.codeEdit.backgroundCompilerOutstandingTasks > 0: #(not self.bpIDE.backgroundCompileIsUpToDate) and (self.codeEdit.backgroundCompilerOutstandingTasks > 0):
			#self.numTasksHandled = self.codeEdit.backgroundCompilerOutstandingTasks
			#self.outputCompiler = outputCompiler
			
			# To make the GUI more responsive
			eventLoop = QtCore.QEventLoop(self)
			self.finished.connect(eventLoop.quit)
			
			if self.bpIDE.threaded:
				self.start(QtCore.QThread.InheritPriority)
			else:
				self.run()
				self.finished.emit()
			
			# Execute event loop
			eventLoop.exec()
			
			#self.bpIDE.consoleDock.show()
			#print("Compiling")
		
	def run(self):
		self.version = self.codeEdit.version
		self.ppFile = self.codeEdit.ppFile
		
		try:
			if self.codeEdit: #and not self.codeEdit.disableUpdatesFlag:
				self.startBenchmark("[%s : %d] Background compiler" % (stripDir(self.codeEdit.getFilePath()), self.version))
				
				if os.name == "nt":
					self.outputCompiler = CPPOutputCompiler(
						self.ppFile.processor,
						background = True,
						guiCallBack = None,
					)
					self.outputCompiler.compile(self.ppFile, silent = True)
					
					# Try getting var types
					self.outputCompiler.tryGettingVariableTypesInUnimplementedFunctions()
					
					if not self.bpIDE.running:
						self.bpIDE.outputCompiler = self.outputCompiler
					
					data = self.codeEdit.outputCompilerData
					fillDataByCompiler(data, self.outputCompiler)
				else:
					jobs = Pipe()
					jobResults = Pipe()
					
					mainPipe = Pipe()
					sendPipe = mainPipe[1]
					recvPipe = mainPipe[0]
					
					try:
						#print("Starting process...")
						p = Process(target=compileXML, args=(sendPipe, self.ppFile, self.codeEdit.outputCompilerData, jobs[0], jobResults[0]))
						
						#print("Start...")
						p.start()
						
						#print("Waiting...")
						data = recvPipe.recv()
						if data:
							self.codeEdit.outputCompilerData = data
					#except InterruptedError:
					#	print("[%s] Exception: InterruptedError" % self.ppFile.getFilePath())
					except:
						printTraceback()
					
					# Exit old process
					if self.currentJobQueue:
						#jobs = self.currentJobQueue
						#self.currentJobQueue = None
						#self.currentJobResultsQueue = None
						self.currentJobQueue.send((0))
					
					self.currentJobQueue = jobs[1]
					self.currentJobResultsQueue = jobResults[1]
					self.currentProcess = p
					#p.join()
				
				# No exceptions
				if os.name == "nt":
					data.exceptionMsg = ""
					data.exceptionFilePath = ""
					data.exceptionLineNumber = -1
				
				self.lastException = None
		except OutputCompilerException as e:
			if self.bpIDE.config.developerMode:
				printTraceback()
			else:
				data = self.codeEdit.outputCompilerData
				data.exceptionMsg = e.getMsg()
				data.exceptionFilePath = e.getFilePath()
				data.exceptionLineNumber = e.getLineNumber()
		except CompilerException:
			printTraceback()
		except KeyError:
			printTraceback()
		finally:
			if self.benchmarkTimerStart:
				self.endBenchmark()
			
		#self.bpIDE.backgroundCompilerRan = True

class BaseFunctionWrapper:
	def __init__(self, filePath, paramTypesByDefinition, node):
		self.filePath = filePath
		self.paramTypesByDefinition = paramTypesByDefinition
		self.node = node

####################################################################
# Functions
####################################################################
def fillDataByCompiler(data, comp):
	allClasses = dict()
	
	# Replicate class functions
	for className, classObj in comp.mainClass.classes.items():
		obj = BaseClass(className, None, None)
		obj.functions = duplicateDictKeys(classObj.functions)
		obj.properties = duplicateDictKeys(classObj.properties)
		obj.publicMembers = duplicateDictKeys(classObj.publicMembers)
		
		# Auto complete
		obj.publicACList = classObj.getAutoCompleteList(private = False)
		obj.privateACList = classObj.getAutoCompleteList(private = True)
		
		# Jump to definition
		obj.filePath = classObj.cppFile.getFilePath()
		
		allClasses[className] = obj
	
	# Replicate functions
	allFunctions = dict()
	for funcName, funcList in comp.mainClass.functions.items():
		newFuncs = [BaseFunctionWrapper(x.cppFile.getFilePath(), x.paramTypesByDefinition, x.node) for x in funcList]
		allFunctions[funcName] = newFuncs
	
	# Replicate namespace
	ns = BaseNamespace("", None)
	ns.classes = allClasses
	ns.functions = allFunctions
	ns.externFunctions = duplicateDictKeys(comp.mainClass.externFunctions)
	ns.externVariables = duplicateDictKeys(comp.mainClass.externVariables)
	
	# Set data
	data.mainNamespace = ns
	data.defines = dict()
	data.functionCount = comp.getFunctionCount()

def compileXML(q, ppFile, data, jobs, jobResults):
	comp = CPPOutputCompiler(
		ppFile.processor,
		background = True,
		guiCallBack = None,
	)
	
	data.exceptionMsg = ""
	data.exceptionFilePath = ""
	data.exceptionLineNumber = -1
	
	try:
		comp.compile(ppFile, silent = True)
		comp.tryGettingVariableTypesInUnimplementedFunctions()
	except CompilerException as e:
		# Traceback
		with open(getConfigDir() + "studio/traceback.txt", "w") as f:
			import traceback
			traceback.print_exc(file = f)
			
		data.exceptionMsg = e.getMsg()
		data.exceptionFilePath = e.getFilePath()
		data.exceptionLineNumber = e.getLineNumber()
		q.send(data)
		return
	except BaseException as e:
		# Traceback
		with open(getConfigDir() + "studio/traceback.txt", "w") as f:
			import traceback
			traceback.print_exc(file = f)
		
		data.exceptionMsg = str(e)
		q.send(data)
		return
	
	try:
		fillDataByCompiler(data, comp)
	
		# Send it
		q.send(data)
	except BaseException as e:
		data.exceptionMsg = str(e)
		q.send(data)
		return
	
	while 1:
		try:
			cmd = jobs.recv()
			byteCode = cmd[0]
			
			# Exit
			if byteCode == 0:
				return
			# getExprDataType
			elif byteCode == 1:
				node = cmd[1]
				
				try:
					dataType = comp.mainFile.getExprDataType(node)
				except:
					jobResults.send("")
				else:
					jobResults.send(dataType)
			# restoreScopesOfNode
			elif byteCode == 2:
				scopesOfNode = cmd[1]
				restoreScopesOfNode(comp.mainFile, scopesOfNode)
			# getBubbleCode
			elif byteCode == 3:
				node = cmd[1]
				try:
					code = getBubbleCode(comp, node)
				except BaseException as e:
					code = ["Error while trying to request doc bubble code:\n%s" % str(e)]
				jobResults.send(code)
		except:
			continue

def duplicateDictKeys(d):
	n = dict()
	for x in d.keys():
		n[x] = None
	return n

# Old, old code...deprecated stuff, you know?
# But we need this in case we lack type data.
def bubbleAllFunctionVariants(code, call, shownFuncs, currentOutFile):
	realFuncDefNode = None
	
	funcName = getCalledFuncName(call)
	
	# TODO: Don't depend on self.funcsDict, replace with outputCompiler data
	funcsDict = currentOutFile.compiler.mainClass.functions
	if funcName in funcsDict:
		for func in funcsDict[funcName]: #.values():
			funcDefinitionNode = func.node
			
			# Don't show the same function twice
			if funcDefinitionNode in shownFuncs:
				continue
			
			if realFuncDefNode and realFuncDefNode != funcDefinitionNode:
				continue
			
			shownFuncs[funcDefinitionNode] = True
			
			# Documentation
			doc = getNodeComments(funcDefinitionNode)
			
			# Code
			bpcCode = nodeToBPC(funcDefinitionNode)
			#bpcCode = truncateBubbleCode(bpcCode)
			bpcCode = bubbleAddReturnType(bpcCode, call, currentOutFile)
			code.append(bpcCode)
			
			# Add the documentation afterwards
			if doc:
				code.append(doc)

def bubbleAddReturnType(bpcCode, call, currentOutFile):
	# Do we have more information about that call?
	if currentOutFile:
		dataType = None
		try:
			# Return value
			dataType = currentOutFile.getCallDataType(call)
			if dataType and dataType != "void":
				pos = bpcCode.find("\n")
				bpcCode = (bpcCode[:pos] + "  → " + dataType + "") + bpcCode[pos:]
				return bpcCode
		except:
			return bpcCode
	
	return bpcCode

def bubbleFunction(code, realFuncDefNode, call, currentOutFile, shownFuncs):
	# Don't show the same function twice
	if realFuncDefNode in shownFuncs:
		return
	
	shownFuncs[realFuncDefNode] = True
	
	# Documentation
	doc = getNodeComments(realFuncDefNode)
	
	# Code
	bpcCode = nodeToBPC(realFuncDefNode)
	#bpcCode = truncateBubbleCode(bpcCode)
	bpcCode = bubbleAddReturnType(bpcCode, call, currentOutFile)
	
	# Add it
	code.append(bpcCode)
	
	# Add the documentation afterwards
	if doc:
		code.append(doc)

def getBubbleCode(outputCompiler, node):
	#self.startBenchmark("Find calls in reversed order")
	calls = findCallsReversed(node)
	#self.endBenchmark()
	
	# TODO: Optimize as a dict lookup
	# If we have output compiler information
	currentOutFile = None
	if outputCompiler:
		currentOutFile = outputCompiler.mainFile
		
		#self.lastShownOutputCompiler = self.outputCompiler
		#cePath = self.getFilePath()
		#for outFile in self.outputCompiler.outFiles.values():
		#	if outFile.file == cePath:
		#		currentOutFile = outFile
		#		break
	
	# Let's see if we can get some information about those calls
	code = []
	shownFuncs = dict()
	
	for call in calls:
		callerType = ""
		funcName = ""
		
		if currentOutFile:
			# Restore scopes
			restoreScopesOfNode(currentOutFile, node)
			
			# Exceptions are your friends! ... or not?
			try:
				# Params
				if call.tagName == "call":
					#print(call.toxml())
					caller, callerType, funcName = currentOutFile.getFunctionCallInfo(call)
				elif call.tagName == "new":
					#caller = ""
					callerType = currentOutFile.getExprDataType(call)
					funcName = "init"
					
				params = getElementByTagName(call, "parameters")
				paramsString, paramTypes = currentOutFile.handleParameters(params)
				
				classImpl = currentOutFile.getClassImplementationByTypeName(callerType)
				
				try:
					realFunc = classImpl.getMatchingFunction(funcName, paramTypes)
					realFuncDefNode = realFunc.node
					
					if callerType:
						code.append("# %s" % (callerType))
					
					bubbleFunction(code, realFuncDefNode, call, currentOutFile, shownFuncs)
				except:
					try:
						candidates = classImpl.getCandidates(funcName)
						
						if callerType:
							code.append("# %s" % (callerType))
						
						for func in candidates:
							bubbleFunction(code, func.node, call, currentOutFile, shownFuncs)
						
						continue
					except:
						continue
			
			except:
				# Only show all function variants if code bubble is empty
				if (not code) and call.tagName == "call":
					if callerType:
						code.append("# %s" % (callerType))
					
					bubbleAllFunctionVariants(code, call, shownFuncs, currentOutFile)
				continue
		else:
			# Only show all function variants if code bubble is empty
			if (not code) and call.tagName == "call":
				if callerType:
					code.append("# %s" % (callerType))
				
				bubbleAllFunctionVariants(code, call, shownFuncs, currentOutFile)
			continue
	
	return code

def restoreScopesOfNode(outFile, selectedNode):
	#if not selectedNode:
	#	selectedNode = self.lastShownNode
	
	#if not self.codeEdit:
	#	return
	
	if outFile and selectedNode:
		#print("Before")
		#self.codeEdit.outFile.debugScopes()
		
		savedNode = selectedNode
		
		if savedNode.nodeType != Node.TEXT_NODE and hasattr(savedNode, "lineNumber"):
			savedNodeId = savedNode.lineNumber
		else:
			savedNodeId = None
		
		while (savedNode.nodeType == Node.TEXT_NODE or savedNode.tagName != "module") and ((not savedNodeId) or (not savedNodeId in outFile.nodeIdToScope)):
			#print("Trying: " + savedNode.getAttribute("id"))
			savedNode = savedNode.parentNode
			
			try:
				savedNodeId = savedNode.lineNumber
			except:
				savedNodeId = None
		
		if savedNode and not (savedNode.nodeType == Node.ELEMENT_NODE and savedNode.tagName == "module"):
			try:
				outFile.restoreScopesForNodeId(savedNodeId)
				#print("YAY! ID: %s" % savedNodeId)
				return
			except:
				print("Could not find scope information for node %s" % tagName(savedNode))
			#else:
			#	self.previousScopes = outFile.scopes
		else:
			pass#print("Scopes:")
			#self.codeEdit.outFile.debugNodeToScope()
			#self.codeEdit.outFile.debugScopes()
	
	# Okay we have a problem, but maybe we have old scope data?
	#if self.previousScopes and self.codeEdit.outFile:
	#	print("USING OLD SCOPE DATA")
	#	outFile.restoreScopes(self.previousScopes)

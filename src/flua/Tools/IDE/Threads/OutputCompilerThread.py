from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
from multiprocessing import Process, Queue
import collections

class BPOutputCompilerThreadData:
	def __init__(self):
		self.mainNamespace = None
		self.defines = None
		self.functionCount = -1
		self.exceptionMsg = ""
		self.exceptionLineNumber = -1
		self.exceptionFilePath = ""

def duplicateDictKeys(d):
	n = dict()
	for x in d.keys():
		n[x] = None
	return n

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

def compileXML(q, ppFile, jobs, jobResults):
	comp = CPPOutputCompiler(
		ppFile.processor,
		background = True,
		guiCallBack = None,
	)
	
	data = BPOutputCompilerThreadData()
	
	try:
		comp.compile(ppFile, silent = True)
		comp.tryGettingVariableTypesInUnimplementedFunctions()
	except CompilerException as e:
		data.exceptionMsg = e.getMsg()
		data.exceptionFilePath = e.getFilePath()
		data.exceptionLineNumber = e.getLineNumber()
	
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
		
		allClasses[className] = obj
	
	# Replicate namespace
	ns = BaseNamespace("", None)
	ns.classes = allClasses
	ns.functions = duplicateDictKeys(comp.mainClass.functions)
	ns.externFunctions = duplicateDictKeys(comp.mainClass.externFunctions)
	ns.externVariables = duplicateDictKeys(comp.mainClass.externVariables)
	
	# Set data
	data.mainNamespace = ns
	data.defines = dict()
	data.functionCount = comp.getFunctionCount()
	
	# Send it
	q.put(data)
	
	while 1:
		cmd = jobs.get()
		byteCode = cmd[0]
		
		# Exit
		if byteCode == 0:
			return
		# getExprDataType
		elif byteCode == 1:
			node = cmd[1]
			scopesOfNode = cmd[2]
			
			restoreScopesOfNode(comp.mainFile, scopesOfNode)
			
			try:
				dataType = comp.mainFile.getExprDataType(node)
			except:
				jobResults.put("")
			else:
				jobResults.put(dataType)
		# restoreScopesOfNode
		elif byteCode == 2:
			scopesOfNode = cmd[1]
			restoreScopesOfNode(comp.mainFile, scopesOfNode)

class BPOutputCompilerThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		
		self.bpIDE = bpIDE
		self.lastException = None
		self.codeEdit = None
		self.numTasksHandled = 0
		self.currentJobQueue = None
		
		self.finished.connect(self.bpIDE.backgroundCompilerFinished)
		
	def startWith(self, outputCompiler):
		self.codeEdit = self.bpIDE.codeEdit
		
		if self.codeEdit.backgroundCompilerOutstandingTasks > 0: #(not self.bpIDE.backgroundCompileIsUpToDate) and (self.codeEdit.backgroundCompilerOutstandingTasks > 0):
			self.numTasksHandled = self.codeEdit.backgroundCompilerOutstandingTasks
			
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
		try:
			self.ppFile = self.bpIDE.getCurrentPostProcessorFile()
			
			if self.codeEdit: #and not self.codeEdit.disableUpdatesFlag:
				self.startBenchmark("[%s] Background compiler" % (stripDir(self.codeEdit.getFilePath())))
				
				#self.outputCompiler.compile(self.ppFile, silent = True)
				
				# Try getting var types
				#self.outputCompiler.tryGettingVariableTypesInUnimplementedFunctions()
				
				#if not self.bpIDE.running:
				#	self.bpIDE.outputCompiler = self.outputCompiler
				
				jobs = Queue()
				jobResults = Queue()
				q = Queue()
				p = Process(target=compileXML, args=(q, self.ppFile, jobs, jobResults))
				p.start()
				self.codeEdit.outputCompilerData = q.get()
				
				# Exit old process
				if self.currentJobQueue:
					#jobs = self.currentJobQueue
					#self.currentJobQueue = None
					#self.currentJobResultsQueue = None
					self.currentJobQueue.put((0))
				
				self.currentJobQueue = jobs
				self.currentJobResultsQueue = jobResults
				#p.join()
				
				self.lastException = None
		except OutputCompilerException as e:
			if self.bpIDE.config.developerMode:
				printTraceback()
			else:
				self.lastException = e
		except CompilerException:
			if self.bpIDE.developerFlag:
				printTraceback()
		except KeyError:
			pass
		finally:
			if self.benchmarkTimerStart:
				self.endBenchmark()
		
		#self.bpIDE.backgroundCompilerRan = True

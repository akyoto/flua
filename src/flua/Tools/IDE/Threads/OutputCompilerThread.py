from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
from multiprocessing import Process, Queue
import collections

class BPOutputCompilerThreadData:
	def __init__(self):
		self.mainNamespace = None
		self.defines = None
		self.functionCount = -1

def compileXML(q, ppFile):
	comp = CPPOutputCompiler(
		ppFile.processor,
		background = True,
		guiCallBack = None,
	)
	try:
		comp.compile(ppFile, silent = True)
	except:
		q.put("Error")
	else:
		#q.put(ppFile.root.toprettyxml())
		allClasses = dict()
		allFunctions = dict()
		
		for className, classObj in comp.mainClass.classes.items():
			obj = BaseClass(className, None, None)
			obj.functions = dict()
			for funcName in classObj.functions.keys():
				obj.functions[funcName] = None
			allClasses[className] = obj
		
		for x in comp.mainClass.functions.keys():
			allFunctions[x] = None
		
		data = BPOutputCompilerThreadData()
		
		ns = BaseNamespace("", None)
		ns.classes = allClasses
		ns.functions = allFunctions
		
		data.mainNamespace = ns
		data.defines = dict()
		data.functionCount = comp.getFunctionCount()
		data.mainFile = None
		
		q.put(data)

class BPOutputCompilerThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		
		self.bpIDE = bpIDE
		self.lastException = None
		self.codeEdit = None
		self.numTasksHandled = 0
		
		self.finished.connect(self.bpIDE.backgroundCompilerFinished)
		
	def startWith(self, outputCompiler):
		self.codeEdit = self.bpIDE.codeEdit
		
		if (not self.bpIDE.backgroundCompileIsUpToDate) and (self.codeEdit.backgroundCompilerOutstandingTasks > 0):
			self.numTasksHandled = self.codeEdit.backgroundCompilerOutstandingTasks
			self.outputCompiler = outputCompiler
			
			# To make the GUI more responsive
			eventLoop = QtCore.QEventLoop(self)
			self.finished.connect(eventLoop.quit)
			
			if self.bpIDE.threaded:
				q = Queue()
				p = Process(target=compileXML, args=(q, self.bpIDE.getCurrentPostProcessorFile()))
				p.start()
				self.codeEdit.outputCompilerData = q.get()
				p.join()
				self.finished.emit()
				#self.start(QtCore.QThread.InheritPriority)
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
				
				self.outputCompiler.compile(self.ppFile, silent = True)
				
				# Try getting var types
				self.outputCompiler.tryGettingVariableTypesInUnimplementedFunctions()
				
				if not self.bpIDE.running:
					self.bpIDE.outputCompiler = self.outputCompiler
				
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

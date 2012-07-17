from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
import collections

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
			q = QtCore.QEventLoop(self)
			self.finished.connect(q.quit)
			
			if self.bpIDE.threaded:
				self.start(QtCore.QThread.InheritPriority)
			else:
				self.run()
				self.finished.emit()
			
			# Execute event loop
			q.exec()
			
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

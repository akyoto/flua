from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
import collections

class BPOutputCompilerThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		self.bpIDE = bpIDE
		self.lastException = None
		self.codeEdit = None
		self.finished.connect(self.bpIDE.backgroundCompilerFinished)
		
	def startWith(self, outputCompiler):
		self.codeEdit = self.bpIDE.codeEdit
		if (not self.bpIDE.backgroundCompileIsUpToDate) and (not self.bpIDE.backgroundCompilerRan):
			self.outputCompiler = outputCompiler
			
			if self.bpIDE.threaded:
				self.start()
			else:
				self.run()
				self.finished.emit()
			#self.bpIDE.consoleDock.show()
			#print("Compiling")
		
	def run(self):
		try:
			self.ppFile = self.bpIDE.getCurrentPostProcessorFile()
			
			if self.codeEdit and not self.codeEdit.disableUpdatesFlag:
				self.startBenchmark("[%s] Background compiler" % (stripDir(self.codeEdit.getFilePath())))
				
				self.outputCompiler.compile(self.ppFile, silent = True)
				
				# Try getting var types
				self.outputCompiler.tryGettingVariableTypesInUnimplementedFunctions()
				
				if not self.bpIDE.running:
					self.bpIDE.outputCompiler = self.outputCompiler
				
				self.lastException = None
		except OutputCompilerException as e:
			#if self.bpIDE.developerFlag:
			#	printTraceback()
			#else:
			self.lastException = e
		except CompilerException:
			pass
		except KeyError:
			pass
		finally:
			if self.benchmarkTimerStart != 0:
				self.endBenchmark()
		
		#self.bpIDE.backgroundCompilerRan = True

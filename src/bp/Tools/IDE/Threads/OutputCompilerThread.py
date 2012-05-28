from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
import collections

class BPOutputCompilerThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.lastException = None
		self.finished.connect(self.bpIDE.backgroundCompilerFinished)
		
	def startWith(self, outputCompiler):
		if not self.bpIDE.backgroundCompileIsUpToDate and not self.bpIDE.backgroundCompilerRan:
			self.outputCompiler = outputCompiler
			self.start()
			#self.bpIDE.consoleDock.show()
			#print("Compiling")
		
	def run(self):
		try:
			self.ppFile = self.bpIDE.getCurrentPostProcessorFile()
			
			if self.bpIDE.codeEdit and not self.bpIDE.codeEdit.disableUpdatesFlag:
				self.outputCompiler.compile(self.ppFile, silent = True)
				
				if not self.bpIDE.running:
					self.bpIDE.outputCompiler = self.outputCompiler
				
				self.bpIDE.backgroundCompilerRan = True
				self.lastException = None
		except OutputCompilerException as e:
			self.lastException = e
		except KeyError:
			pass
		
		self.bpIDE.backgroundCompilerRan = True

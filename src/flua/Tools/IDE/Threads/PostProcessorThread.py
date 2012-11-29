from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
import collections

class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		Benchmarkable.__init__(self)
		
		self.bpIDE = codeEdit.bpIDE
		self.codeEdit = codeEdit
		self.processor = codeEdit.bpIDE.processor
		self.ppFile = None
		self.lastException = None
		self.numTasksHandled = 0
		self.version = 0
		#self.ceQueue = collections.deque()
		self.finished.connect(codeEdit.postProcessorFinished)
		
	def startWith(self):
		self.numTasksHandled = self.codeEdit.ppOutstandingTasks
		
		if not self.codeEdit is None:
			if self.bpIDE.threaded:
				self.start(QtCore.QThread.InheritPriority)
			else:
				self.run()
				self.finished.emit()
		
	#def queue(self, codeEdit):
	#	self.ceQueue.append(codeEdit)
		
	def run(self):
		self.version = self.codeEdit.version
		filePath = self.codeEdit.getFilePath()
		
		with self.processor.lock:
			try:
				if self.bpIDE.loadingFinished:
					self.processor.resetDTreesForFile(filePath)
					self.processor.cleanUpFile(filePath)
				
				self.startBenchmark("[%s : %d] PostProcessor" % (stripDir(filePath), self.version))
				self.ppFile = self.processor.process(self.codeEdit.root, filePath)
				self.endBenchmark()
				
				#self.bpIDE.processorOutFile = self.processor.processExistingInputFile(self.codeEdit.bpcFile)
				self.lastException = None
			except PostProcessorException as e:
				self.lastException = e
				
				# Try to get line information
				try:
					e.lineNumber = self.codeEdit.bpcFile.nodeToOriginalLineNumber[e.node]
				except:
					pass

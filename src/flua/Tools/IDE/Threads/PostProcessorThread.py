from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
import collections

class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		self.bpIDE = bpIDE
		self.processor = bpIDE.processor
		self.ppFile = None
		self.lastException = None
		self.numTasksHandled = 0
		self.ceQueue = collections.deque()
		self.finished.connect(self.bpIDE.postProcessorFinished)
		
	def startWith(self, codeEdit):
		self.codeEdit = codeEdit
		self.numTasksHandled = codeEdit.ppOutstandingTasks
		
		if not self.codeEdit is None:
			if self.bpIDE.threaded:
				self.start(QtCore.QThread.InheritPriority)
			else:
				self.run()
				self.finished.emit()
		
	def queue(self, codeEdit):
		self.ceQueue.append(codeEdit)
		
	def run(self):
		try:
			filePath = self.codeEdit.getFilePath()
			self.startBenchmark("[%s] PostProcessor" % stripDir(filePath))
			self.processor.resetDTreesForFile(filePath)
			self.processor.cleanUpFile(filePath)
			self.ppFile = self.processor.process(self.codeEdit.root, filePath)
			#self.bpIDE.processorOutFile = self.processor.processExistingInputFile(self.codeEdit.bpcFile)
			self.endBenchmark()
			self.lastException = None
		except PostProcessorException as e:
			self.lastException = e
			
			# Try to get line information
			try:
				e.lineNumber = self.codeEdit.bpcFile.nodeToOriginalLineNumber[e.node]
			except:
				pass

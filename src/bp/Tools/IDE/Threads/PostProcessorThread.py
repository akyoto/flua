from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
import collections

class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.processor = bpIDE.processor
		self.lastException = None
		self.ceQueue = collections.deque()
		self.finished.connect(self.bpIDE.postProcessorFinished)
		self.finished.connect(self.bpIDE.msgView.updateViewPostProcessor)
		
	def startWith(self, codeEdit):
		self.codeEdit = codeEdit
		if not self.codeEdit is None:
			self.start()
		
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

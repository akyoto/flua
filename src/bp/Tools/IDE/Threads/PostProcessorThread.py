from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *

class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.processor = bpIDE.processor
		self.finished.connect(self.bpIDE.postProcessorFinished)
		
	def run(self):
		try:
			self.startBenchmark("[%s] PostProcessor" % stripDir(self.bpIDE.getFilePath()))
			self.processor.resetDTreesForFile(self.bpIDE.getFilePath())
			self.bpIDE.processorOutFile = self.processor.process(self.bpIDE.codeEdit.root, self.bpIDE.getFilePath())
			self.endBenchmark()
		except PostProcessorException as e:
			errorMessage = e.getMsg()
			self.bpIDE.msgView.addMessage(errorMessage)

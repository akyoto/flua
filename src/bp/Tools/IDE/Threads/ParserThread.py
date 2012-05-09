from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *

class BPCodeUpdater(QtCore.QThread, Benchmarkable):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		self.bpIDE = codeEdit.bpIDE
		self.setDocument(codeEdit.qdoc)
		self.bpc = self.bpIDE.bpc#BPCCompiler(getModuleDir())
		self.bpcFile = None
		self.lastException = None
		self.finished.connect(self.codeEdit.compilerFinished)
		self.finished.connect(self.bpIDE.moduleView.updateView)
		self.finished.connect(self.bpIDE.msgView.updateViewParser)
		
	def setDocument(self, doc):
		self.qdoc = doc
		
	def run(self):
		#yappi.start()
		if self.codeEdit.futureText:
			codeText = self.codeEdit.futureText
		else:
			codeText = self.qdoc.toPlainText()
		#self.bpIDE.msgView.clear()
		#self.codeEdit.clearHighlights()
		
		self.lastException = None
		try:
			# TODO: Remove unsafe benchmark
			filePath = self.codeEdit.getFilePath()
			self.startBenchmark("[%s] Parser" % stripDir(filePath))
			self.bpcFile = self.bpc.spawnFileCompiler(filePath, True, codeText)
			if self.bpcFile.inFunction != 0:
				print("inFunction: " +  str(self.bpcFile.inFunction))
		except InputCompilerException as e:
			self.lastException = e
			
			# IMPORTANT: If an exception occured, editing should be able to run the updater again!
			self.codeEdit.disableUpdatesFlag = False
			
			#self.codeEdit.setLineError(lineNumber - 1, errorMessage)
			#self.codeEdit.highlightLine(lineNumber - 1, QtGui.QColor("#ff0000"))
		finally:
			#yappi.stop()
			#yappi.print_stats()
			self.endBenchmark()
			#yappi.clear_stats()
		
		return

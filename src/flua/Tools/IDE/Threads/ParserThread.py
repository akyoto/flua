from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *

class BPCodeUpdater(QtCore.QThread, Benchmarkable):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		self.bpIDE = codeEdit.bpIDE
		self.setDocument(codeEdit.qdoc)
		self.bpc = self.bpIDE.inputCompiler#BPCCompiler(getModuleDir())
		self.bpcFile = None
		self.lastException = None
		self.executionTime = 0
		self.finished.connect(self.codeEdit.compilerFinished)
		self.finished.connect(self.bpIDE.moduleView.updateView)
		
	def setDocument(self, doc):
		self.qdoc = doc
		
	def run(self):
		codeText = self.qdoc.toPlainText()
		#yappi.start()
		if self.codeEdit.openingFile:
			# No delay when opening files
			self.codeEdit.openingFile = False
		
		#self.codeEdit.clearHighlights()
		
		# Reduces memory usage
		if self.bpcFile:
			del self.bpcFile
			self.bpcFile = None
		
		try:
			# TODO: Remove unsafe benchmark
			filePath = self.codeEdit.getFilePath()
			self.startBenchmark("[%s] Parser" % stripDir(filePath))
			self.bpcFile = self.bpc.spawnFileCompiler(filePath, True, codeText)
			
			#if self.bpcFile.inFunction != 0:
			#	print("inFunction: " +  str(self.bpcFile.inFunction))
				
			del self.lastException
			self.lastException = None
		except InputCompilerException as e:
			self.lastException = e
			
			# IMPORTANT: If an exception occured, editing should be able to run the updater again!
			self.codeEdit.disableUpdatesFlag = False
			
			#self.codeEdit.setLineError(lineNumber - 1, errorMessage)
			#self.codeEdit.highlightLine(lineNumber - 1, QtGui.QColor("#ff0000"))
		finally:
			#yappi.stop()
			#yappi.print_stats()
			self.executionTime = self.endBenchmark()
			#yappi.clear_stats()
		
		# High amount of update requests means the user is typing a lot.
		# When he does that we want to delay the updates until he is finished.
		# queueCount = self.codeEdit.updateQueue.count(1)
		# if queueCount:
			# maxWaitTime = 3000
			
			# if myExecutionTime < 10:
				# myExecutionTime == 10
			
			# sleepTime = int((maxWaitTime * queueCount) / myExecutionTime)
			#print("Sleeping for %d milliseconds!" % sleepTime)
			
			# QtCore.QThread.msleep(sleepTime)
		
		return

from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
from bp.Tools.IDE.Utils import *

class BPGitThread(QtCore.QThread):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.finished.connect(self.bpIDE.gitPullFinished)
		self.cmd = None
		
	def startCmd(self, cmd):
		if self.isRunning():
			return
		
		self.cmd = cmd
		self.start()
		
	def run(self):
		try:
			startProcess(self.cmd, self.bpIDE.console.realStdout.write, self.bpIDE.console.realStderr.write)
		except Exception as e:
			errorMessage = str(e)
			print(errorMessage)

from PyQt4 import QtGui, QtCore, uic
from flua.Compiler import *
from flua.Tools.IDE.Utils import *

exitCodeMeaning = {
	0  : "successful termination",
	11 : "segmentation fault",
	64 : "command line usage error",
	65 : "data format error",
	66 : "cannot open input",
	67 : "addressee unknown",
	68 : "host name unknown",
	69 : "service unavailable",
	70 : "internal software error",
	71 : "system error (e.g., can't fork)",
	72 : "critical OS file missing",
	73 : "can't create (user) output file",
	74 : "input/output error",
	75 : "temp failure; user is invited to retry",
	76 : "remote error in protocol",
	77 : "permission denied",
	78 : "configuration error",
}
 
class BPRunThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		
		self.bpIDE = bpIDE
		self.process = None
		self.debugMode = False
		self.exitCode = -1
		self.finished.connect(self.programExited)
	
	def programStarted(self):
		print("Program „%s“ started." % (stripAll(self.exe)))
		
		if self.debugMode:
			#self.sendDebugger("break main\n")
			self.sendDebugger("run\n")
			#self.sendDebugger("q\n")
		
	def programExited(self):
		if self.exitCode != 0:
			if self.exitCode in exitCodeMeaning:
				print("Program „%s“ exited with exit code [%d] (%s)." % (stripAll(self.exe), self.exitCode, exitCodeMeaning[self.exitCode]))
			elif -self.exitCode in exitCodeMeaning:
				print("Program „%s“ exited with exit code [%d] (%s)." % (stripAll(self.exe), self.exitCode, exitCodeMeaning[-self.exitCode]))
			else:
				print("Program „%s“ exited with exit code [%d]." % (stripAll(self.exe), self.exitCode))
		else:
			print("Program „%s“ exited normally." % (stripAll(self.exe)))
		
		if self.bpIDE.running > 0:
			self.bpIDE.running -= 1
		
		if self.bpIDE.codeEdit:
			self.bpIDE.codeEdit.setFocus()
		
		os.chdir(getIDERoot())
		
	def startWith(self, exe, debugMode = False):
		#self.codeEdit = self.bpIDE.codeEdit
		self.outputCompiler = self.bpIDE.outputCompiler
		self.exe = exe
		self.debugMode = debugMode
		
		self.bpIDE.running += 1
		
		if self.bpIDE.threaded:
			self.start()
		else:
			self.run()
			self.finished.emit()
		
	def sendDebugger(self, data):
		self.sendData(data)
		
	def sendData(self, data):
		if self.bpIDE.running:
			someBytes = data.encode("utf-8")
			#print("Sending " + str(someBytes))
			
			# FLUSH IS NEEDED HERE!
			self.process.stdin.write(someBytes)
			self.process.stdin.flush()
		
	def run(self):
		if not self.debugMode:
			runFunc = self.outputCompiler.execute
		else:
			runFunc = self.outputCompiler.debug
		
		# Start the process
		self.exitCode = runFunc(
			exe = self.exe,
			fhOut = self.bpIDE.console.output.write,
			fhErr = self.bpIDE.console.output.writeError,
			thread = self
		)

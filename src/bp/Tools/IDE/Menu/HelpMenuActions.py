from bp.Tools.IDE.Startup import *
from bp.Compiler import *

class HelpMenuActions:
	
	def resetLocalChanges(self):
		if not self.ask("Are you sure you want to revert all local source code changes?"):
			return
		
		self.acquireGitThread()
		
		os.chdir(getModuleDir())
		
		gitResetCmd = [
			getGitPath() + "git",
			"reset",
			"--hard",
			"HEAD"
		]
		
		print("Reset local changes...")
		self.gitThread.startCmd(gitResetCmd, self.console.log)
		self.gitThread.wait()
		
		os.chdir(getIDERoot())
		
	def resetLocalFileChanges(self):
		if not self.codeEdit:
			return
		
		if not self.ask("Are you sure you want to revert all local source code changes to the currently opened file?"):
			return
		
		self.acquireGitThread()
		
		#os.chdir(getModuleDir())
		
		gitResetCmd = [
			getGitPath() + "git",
			"checkout",
			self.codeEdit.getFilePath()
		]
		
		print("Reset local changes...")
		self.gitThread.startCmd(gitResetCmd, self.console.log)
		self.gitThread.wait()
		
		#os.chdir(getIDERoot())
	
	def acquireGitThread(self):
		if self.gitThread and self.gitThread.isRunning():
			return False
		
		if self.gitThread is None:
			self.gitThread = BPGitThread(self)
		
		return True
			
	def showChangeLog(self):
		self.acquireGitThread()
		
		gitLogCmd = [
			getGitPath() + "git",
			"log",
			"--no-color",
			"--date=relative",
			"--format=%ar, %an: %s"
			#"--oneline",
			#"-n 20",
			#"--shortstat"
		]
		
		self.changeLogDialog, existed = self.getUIFromCache("changelog")
		
		if not existed:
			# To prevent an error
			self.changeLogDialog.bpIDE = self
			
			self.changeLog = BPLogWidget(self.changeLogDialog)
			self.changeLog.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
			self.changeLog.setReadOnly(True)
			self.changeLog.setStyleSheet(self.config.dialogStyleSheet)
			self.changeLogDialog.changeLogContainer.layout().addWidget(self.changeLog)
		
		self.changeLog.clear()
		
		print("Retrieving changelog...")
		self.gitThread.startCmd(gitLogCmd, self.changeLog, True)
		#self.gitThread.wait()
		
		#cursor = self.changeLog.textCursor()
		#cursor.movePosition(QtGui.QTextCursor.Start)
		#self.changeLog.setTextCursor(cursor)
		#self.changeLog.ensureCursorVisible()
		
		self.changeLogDialog.exec()
	
	def downloadUpdates(self):
		self.acquireGitThread()
		
		#gitResetCmd = [
		#	getGitPath() + "git",
		#	"reset",
		#	"--hard",
		#	"HEAD"
		#]
		
		#gitCleanCmd = [
		#	getGitPath() + "git",
		#	"clean",
		#	"-f",
		#	"-d"
		#]
		
		gitPullCmd = [
			getGitPath() + "git",
			"pull"
		]
		
		print("Checking for updates...")
		self.gitThread.startCmd(gitPullCmd)
	
	def cleanAllTargets(self):
		self.acquireGitThread()
		
		# C++
		print("Cleaning all C++ builds...")
		cleanCmd = [
			getFindPath() + "find",
			getModuleDir(),
			"-name",
			"C++",
			
			"-exec",
			getRmPath() + "rm",
			"-rf",
			"{}",
			";",
		]
		
		self.gitThread.startCmd(cleanCmd, self.console.log)
		
		# Wait for thread to finish so we can clean the next
		self.gitThread.wait()
		
		# Python 3
		print("Cleaning all Python 3 builds...")
		cleanCmd = [
			getFindPath() + "find",
			getModuleDir(),
			"-name",
			"Python3",
			
			"-exec",
			getRmPath() + "rm",
			"-rf",
			"{}",
			";",
		]
		
		self.gitThread.startCmd(cleanCmd, self.console.log)
	
	def reportBug(self):
		QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/blitzprog/bp/issues/new", QtCore.QUrl.TolerantMode))
	
	def showIntroduction(self):
		self.moduleView.highlightModule("bp.Examples.")
		
	def thanksTo(self):
		msgBox = QtGui.QMessageBox.about(self, "Thanks to...",
							"""
							<p>
								<h2>Thanks to the developers of:</h2>
								<ul style='font-size: 12pt;'>
									<li style='margin-bottom: 4px'>Qt</li>
									<li style='margin-bottom: 4px'>Python</li>
									<li style='margin-bottom: 4px'>PyQt</li>
									<li style='margin-bottom: 4px'>Git</li>
									<li style='margin-bottom: 4px'>Linux</li>
									<li style='margin-bottom: 4px'>MinGW</li>
									<li style='margin-bottom: 4px'>GMP</li>
									<li style='margin-bottom: 4px'>Boehm GC</li>
									<li style='margin-bottom: 4px'>github.com</li>
								</ul>
								<br/><br/>
								Without these projects the development of bp would not have been possible.
							</p>
							""")
		
	def about(self):
		QtGui.QMessageBox.about(self, "About bp Studio",
							"""
							<p>
								<h2>bp Studio</h2>
								A development environment for bp.<br/>
								<br/>
								Official website:<br/>
								<a href="http://blitzprog.org/">http://blitzprog.org/</a><br/>
								<br/>
								GitHub project:<br/>
								<a href="https://github.com/blitzprog/bp">https://github.com/blitzprog/bp</a><br/>
								<br/>
								by Eduard Urbach
							</p>
							""")

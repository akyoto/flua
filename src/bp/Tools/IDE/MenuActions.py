from bp.Tools.IDE.Startup import *

class MenuActions:
	
	def newFile(self, fileName = "", isOpeningFile = False):
		self.tmpCount += 1
		
		# TODO:
		if not fileName:
			fileName = "./tmp/New file %d.bp" % (self.tmpCount)
		newCodeEdit = BPCodeEdit(self)
		newCodeEdit.openingFile = True
		
		newCodeEdit.clear()
		newCodeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		self.currentWorkspace.addAndSelectTab(newCodeEdit, stripAll(fileName))
		
		self.setFilePath(fileName)
		
		newCodeEdit.setFocus()
		
		if not isOpeningFile:
			newCodeEdit.openingFile = False
			newCodeEdit.runUpdater()
		
	def reopenLastFile(self):
		if not self.currentWorkspace.filesClosed:
			return
		
		self.openFile(self.currentWorkspace.filesClosed.pop())
	
	def openFile(self, path):
		fileName = path
		if not fileName:
			if self.isTmpFile():
				openInDirectory = getModuleDir()
			else:
				openInDirectory = extractDir(self.getFilePath())
			
			fileName = QtGui.QFileDialog.getOpenFileName(
				parent=self,
				caption="Open File",
				directory=openInDirectory,
				filter="bp and related Files (*.bp *.hpp);;bpc Files (*.bpc);;Any text file (*.*)")
		
		if fileName:
			# File already opened in workspace?
			index = 0
			ce = None
			workspaceID = -1
			
			#ceInWorkspaces = None
			
			for workspace in self.workspaces:
				workspaceID += 1
				index, ce = workspace.getCodeEditByPath(fileName)
				if index != -1:
					break
			
			# Completely new file
			if index == -1:
				self.newFile(fileName, isOpeningFile = True)
				
				if fileName.endswith(".bp"):
					self.loadFileToEditor(fileName)
				elif fileName.endswith(".bpc"):
					self.loadBPCFileToEditor(fileName)
				else:
					self.loadTextFileToEditor(fileName)
				
				self.currentWorkspace.updateCurrentCodeEditName()
			# File was opened in another workspace
			elif self.workspaces[workspaceID] != self.currentWorkspace:
				if ce.isTextFile:
					tabName = stripDir(fileName)
				else:
					tabName = stripAll(fileName)
				self.currentWorkspace.addAndSelectTab(ce, tabName)
				
				# For some reason Qt shows the others workspace even though we have hidden it
				# => So we need to hide it again
				self.workspaces[workspaceID].hide()
				
			# File is already opened in this workspace
			elif self.workspaces[workspaceID] == self.currentWorkspace:
				self.currentWorkspace.changeCodeEdit(index)
			
		# Add to recent files list
		#self.recentFiles
		
	def saveFile(self):
		if self.codeEdit is None or self.currentWorkspace.count() == 0:
			return
		
		# Make sure the XML is up 2 date
		if (not self.codeEdit.isTextFile) and self.codeEdit.updateQueue:
			# We first need to end parsing!
			# Disable the stupid threads!
			self.codeEdit.threaded = False
			self.codeEdit.onUpdateTimeout()
			self.codeEdit.threaded = True
		
		filePath = self.getFilePath()
		if self.isTmpPath(filePath) or filePath.endswith(".bpc"):
			self.saveAsFile()
		elif self.codeEdit:
			self.codeEdit.save(filePath)
	
	def saveAsFile(self):
		if self.codeEdit is None:
			return False
		
		if self.isTmpFile():
			saveInDirectory = getModuleDir()
		else:
			saveInDirectory = extractDir(self.getFilePath())
		
		filePath = QtGui.QFileDialog.getSaveFileName(
				parent=self,
				caption="Save File",
				directory=saveInDirectory,
				filter="bp Files (*.bp)")
		
		if filePath:
			self.codeEdit.save(filePath)
			self.currentWorkspace.updateCurrentCodeEditName()
			
			# If it was saved in the module directory, reload the view
			if getModuleDir() in fixPath(filePath):
				self.moduleView.reloadModuleDirectory()
			
			return True
		
		return False
	
	def showSearch(self):
		self.searchForm, existed = self.getUIFromCache("search")
		
		if not existed:
			self.searchForm.setStyleSheet(self.config.dialogStyleSheet)
			
			flags = self.searchForm.windowFlags()
			flags |= QtCore.Qt.WindowStaysOnTopHint
			#flags |= QtCore.Qt.Popup
			#flags |= QtCore.Qt.FramelessWindowHint
			
			self.searchForm.setWindowFlags(flags)
			#self.searchForm.searchEdit.
		
		self.searchForm.searchEdit.setFocus()
		self.searchForm.show()
	
	def runProfiler(self):
		self.notImplemented()
	
	def onRunModule(self):
		self.runModule([])
	
	def runModuleOptimized(self):
		self.runModule([
			"-O3",
			"-march=native",
			"-mtune=native",
		])
	
	def runModule(self, compilerFlags = []):
		if self.codeEdit is None or self.currentWorkspace.count() == 0 or self.codeEdit.isTextFile:
			return
		
		# Make sure the XML is up 2 date
		if self.codeEdit.updateQueue:
			# We first need to end parsing!
			# Disable the stupid threads!
			self.codeEdit.threaded = False
			self.codeEdit.onUpdateTimeout()
			self.codeEdit.threaded = True
		
		outputTarget = "C++"
		
		if outputTarget == "C++":
			#print(self.processor.getCompiledFilesList())
			self.codeEdit.save()
			
			self.console.clearLog()
			self.msgView.clear()
			try:
				self.startBenchmark("C++ Build")
				
				cpp = CPPOutputCompiler(self.processor)
				
				#exePath = cpp.getExePath().replace("/", "\\")
				#if exePath and os.path.isfile(exePath):
				#	print("Removing %s" % exePath)
				#	os.remove(exePath)
				
				bpPostPFile = self.processor.getCompiledFiles()[self.getFilePath()]
				#try:
				cpp.compile(bpPostPFile)
				#except OutputCompilerException as e:
				#	self.msgView.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), e.getMsg())
				#	return
				
				cpp.writeToFS()
				
				exitCode = cpp.build(compilerFlags)
				
				print("-" * 80)
				self.endBenchmark()
				
				if exitCode != 0:
					print("C++ compiler error (see other console window, exit code %d)" % exitCode)
					return
				
				exe = cpp.getExePath()
				
				if not compilerFlags:
					print("No optimizations active (-O0)")
				else:
					print("Using optimizations (-O3)")
				print("Executing: %s" % exe)
				print("-" * 80)
				
				exeDir = extractDir(exe)
				os.chdir(exeDir)
				
				cpp.execute(exe, self.console.log.write, self.console.log.writeError)
			except OutputCompilerException as e:
				#lineNumber = e.getLineNumber()
				node = e.getLastParsedNode()
				
				if self.developerFlag:
					printTraceback()
					
					if node:
						print("Last parsed node:\n" + node.toxml())
				else:
					errorMessage = e.getMsg()
					self.msgView.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), errorMessage)
			except:
				printTraceback()
			finally:
				os.chdir(getIDERoot())
			
			#cpp.compile(self.file, self.codeEdit.root)
			
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
		
		self.changeLogDialog.show()
	
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
		
		#os.chdir(getModuleDir())
		
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
		
		print("Cleaning all targets...")
		self.gitThread.startCmd(cleanCmd, self.console.log)
		
		#os.chdir(getIDERoot())
	
	def resetLocalChanges(self):
		reply = QtGui.QMessageBox.question(self,
				"Message",
				"Are you sure you want to revert all local source code changes?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
				QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.No:
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
	
	def runModuleTest(self):
		self.notImplemented()
	
	def showModuleProperties(self):
		if self.codeEdit is None or not self.currentWorkspace.count():
			return
		
		self.moduleProperties, existed = self.getUIFromCache("module-properties")
		if not existed:
			self.moduleProperties.optimizeFor.currentIndexChanged.connect(self.setOptimizationOptions)
			self.moduleProperties.setStyleSheet(self.config.dialogStyleSheet)
		
		filePath = self.getFilePath()
		modulePath = self.localToGlobalImport(stripAll(filePath))
		if modulePath:
			parts = self.splitModulePath(modulePath)
			self.moduleProperties.modName.setText(".".join(parts))
			self.moduleProperties.companyName.setText(parts[0])
			if len(parts) > 1:
				self.moduleProperties.projectName.setText(parts[1])
			else:
				self.moduleProperties.projectName.setText("")
		else:
			self.moduleProperties.modName.setText("Your module is stored outside of the global repository. Please change this.")
			self.moduleProperties.companyName.setText("No company associated. Please create a directory in the global repository.")
			self.moduleProperties.projectName.setText("")
		
		if os.path.isfile(filePath):
			created = os.path.getctime(filePath)
			modified = os.path.getmtime(filePath)
			
			self.moduleProperties.dateCreated.setText(time.ctime(created))
			self.moduleProperties.dateModified.setText(time.ctime(modified))
		else:
			self.moduleProperties.dateCreated.setText("-")
			self.moduleProperties.dateModified.setText("-")
		
		self.setOptimizationOptions(self.moduleProperties.optimizeFor.currentIndex())
		self.moduleProperties.show()
	
	def setOptimizationOptions(self, index):
		# 0: Speed
		if index == 0:
			self.moduleProperties.useBigInt.setChecked(False)
			self.moduleProperties.useRequirements.setChecked(False)
			self.moduleProperties.useArrayRequirements.setChecked(False)
			self.moduleProperties.useDivisionByZeroCheck.setChecked(False)
		# 1: Correctness
		elif index == 1:
			self.moduleProperties.useBigInt.setChecked(True)
			self.moduleProperties.useRequirements.setChecked(True)
			self.moduleProperties.useArrayRequirements.setChecked(True)
			self.moduleProperties.useDivisionByZeroCheck.setChecked(True)
		# 2: Custom
		else:
			pass
	
	def showPreferences(self):
		self.preferences.setStyleSheet(self.config.dialogStyleSheet)
		self.preferences.show()
	
	def undoLastAction(self):
		if self.codeEdit:
			self.codeEdit.undo()
		
	def redoLastAction(self):
		if self.codeEdit:
			self.codeEdit.redo()
		
	def toggleFullScreen(self):
		self.geometryState = self.saveState()
		if self.isFullScreen():
			self.showNormal()
		else:
			self.showFullScreen()
		
	def showIntroduction(self):
		# For beginners
		self.newFile()
		
		if not self.codeEdit:
			return
		
		#self.codeEdit.disableUpdatesFlag = True
		self.codeEdit.setPlainText('''# Press F5 to run this
print "Hello bp!"

# You are using BPC syntax at the moment.
# It's pretty similar to Python:
if 1 + 1 == 2
	print "I'm a genius!"
else
	print "Something's wrong here..."

# A function starts with a lowercase letter (this will be changeable in the settings later):
myFunction x, y
	return x + y

# Call the function:
a = myFunction(5, 5)

# By using type inference the compiler knows 'a' is an integer.

# Classes start with an uppercase letter (will be changeable)
# and must contain an init function as a constructor:
MyClass
	init my.message
		print my.message
		
	doSomething
		print "By the way I heard Unicode works: おはようございます。"

# Creating objects:
b = MyClass("Hey it's b here! Long time no see.")

# Calling methods (whether brackets are optional or not depends on the syntax module):
b.doSomething()

# The current version is not stable.
# If you find a bug you can either post it here: https://github.com/blitzprog/bp/issues
# or tell me about it on IRC (#blitzprog on irc.freenode.net). Settings and preferences currently aren't saved and
# in some cases aren't even used.
# There are still lots of features missing but they'll be implemented sooner or later.

# Happy alpha testing :)''')
		#self.codeEdit.disableUpdatesFlag = False
		#self.codeEdit.onUpdateTimeout()
		
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
								Without these projects the development of blitzprog would not have been possible.
							</p>
							""")
		
	def about(self):
		QtGui.QMessageBox.about(self, "About blitzprog IDE",
							"""
							<p>
								<h2>Blitzprog IDE</h2>
								A development environment for the blitzprog programming language.<br/>
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
	
	def closeEvent(self, event):
		self.scribble.saveScribble()
		event.accept()
		return
		
		# TODO: Check files opened
		reply = QtGui.QMessageBox.question(self,
				"Message",
				"Are you sure you want to quit?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
				QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
			
	def notImplemented(self):
		self.notify("Not implemented yet.")

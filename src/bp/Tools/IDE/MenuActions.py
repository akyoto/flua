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
				filter="bp Files (*.bp);;bpc Files (*.bpc)")
		
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
			# File was opened in another workspace
			elif self.workspaces[workspaceID] != self.currentWorkspace:
				self.currentWorkspace.addAndSelectTab(ce, stripAll(fileName))
				
				# For some reason Qt shows the others workspace even though we have hidden it
				# => So we need to hide it again
				self.workspaces[workspaceID].hide()
				
			# File is already opened in this workspace
			elif self.workspaces[workspaceID] == self.currentWorkspace:
				self.currentWorkspace.changeCodeEdit(index)
			
		# Add to recent files list
		#self.recentFiles
		
	def saveFile(self):
		if self.codeEdit is None:
			return
		
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
		if self.codeEdit is None:
			return
		
		outputTarget = "C++"
		
		if outputTarget == "C++":
			#print(self.processor.getCompiledFilesList())
			self.codeEdit.save()
			
			self.console.clearLog()
			self.msgView.clear()
			try:
				self.startBenchmark("C++ Build")
				
				cpp = CPPOutputCompiler(self.processor)
				bpPostPFile = self.processor.getCompiledFiles()[self.getFilePath()]
				cpp.compile(bpPostPFile)
				cpp.writeToFS()
				exe = cpp.build(compilerFlags)
				
				print("-" * 80)
				self.endBenchmark()
				
				print("No optimizations active (-O0)")
				print("Executing: %s" % exe)
				print("-" * 80)
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
			
			#cpp.compile(self.file, self.codeEdit.root)
	
	def downloadUpdates(self):
		if self.gitThread and self.gitThread.isRunning():
			return
		
		if self.gitThread is None:
			self.gitThread = BPGitThread(self)
		
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
	
	def showModuleProperties(self):
		self.moduleProperties, existed = self.getUIFromCache("module-properties")
		if not existed:
			self.moduleProperties.optimizeFor.currentIndexChanged.connect(self.getOptimizeExplanation)
			self.moduleProperties.setStyleSheet(self.config.dialogStyleSheet)
		
		if self.codeEdit is None:
			return
		
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
		
		self.getOptimizeExplanation(self.moduleProperties.optimizeFor.currentIndex())
		self.moduleProperties.show()
	
	def getOptimizeExplanation(self, index):
		# 0: Numerics in this module use Int and Float as their data type by default.
		# 1: Numerics in this module use BigInt and BigFloat as their data type by default.
		# 2: Custom
		if index == 0:
			self.moduleProperties.optimizeForExplanation.setPlainText("""
Numerics in this module use Int and Float as their data type by default.
				
Array boundaries will not be checked and will not throw an exception.
""".strip())
		elif index == 1:
			self.moduleProperties.optimizeForExplanation.setPlainText("""
Numerics in this module use BigInt and BigFloat as their data type by default (arbitrary precision).
				
Array boundaries will be checked and throw an exception when needed.
""".strip())
		else:
			self.moduleProperties.optimizeForExplanation.setPlainText("""
This feature is currently in development.
""".strip())
	
	def showPreferences(self):
		self.preferences.setStyleSheet(self.config.dialogStyleSheet)
		self.preferences.show()
	
	def undoLastAction(self):
		if self.codeEdit:
			self.codeEdit.undo()
		
	def redoLastAction(self):
		if self.codeEdit:
			self.codeEdit.redo()
		
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
		msg = QtGui.QMessageBox(self)
		msg.setText("Not implemented yet")
		msg.show()

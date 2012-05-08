from bp.Tools.IDE.Startup import *

class MenuActions:
	
	def newFile(self, fileName = ""):
		self.tmpCount += 1
		
		# TODO:
		if not fileName:
			fileName = "./tmp/New file %d.bp" % (self.tmpCount)
		newCodeEdit = BPCodeEdit(self)
		newCodeEdit.clear()
		newCodeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		self.currentWorkspace.addAndSelectTab(newCodeEdit, stripAll(fileName))
		
		self.setFilePath(fileName)
		newCodeEdit.runUpdater()
		newCodeEdit.setFocus()
		
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
			
			ceInWorkspaces = None
			for workspace in self.workspaces:
				index, ce = workspace.getCodeEditByPath(fileName)
				if index != -1:
					break
			
			if index == -1:
				self.newFile(fileName)
				
				if fileName.endswith(".bp"):
					self.loadFileToEditor(fileName)
				elif fileName.endswith(".bpc"):
					self.loadBPCFileToEditor(fileName)
			elif ce != self.currentWorkspace:
				self.currentWorkspace.addAndSelectTab(ce, stripAll(fileName))
			elif ce == self.currentWorkspace:
				self.currentWorkspace.changeCodeEdit(index)
			
		# Add to recent files list
		#self.recentFiles
		
	def saveFile(self):
		if self.codeEdit is None:
			return
		
		filePath = self.getFilePath()
		if self.isTmpPath(filePath) or filePath.endswith(".bpc"):
			self.saveAsFile()
		else:
			self.codeEdit.save(filePath)
	
	def saveAsFile(self):
		if self.codeEdit is None:
			return
		
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
	
	def runModule(self):
		if self.codeEdit is None:
			return
		
		outputTarget = "C++"
		
		if outputTarget == "C++":
			#print(self.processor.getCompiledFilesList())
			self.codeEdit.save()
			
			self.msgView.clear()
			try:
				self.startBenchmark("C++ Compiler")
				
				cpp = CPPOutputCompiler(self.processor)
				bpPostPFile = self.processor.getCompiledFiles()[self.getFilePath()]
				cpp.compile(bpPostPFile)
				cpp.writeToFS()
				exe = cpp.build()
				
				self.endBenchmark()
				
				cpp.execute(exe)
			except OutputCompilerException as e:
				#lineNumber = e.getLineNumber()
				node = e.getLastParsedNode()
				errorMessage = e.getMsg()
				self.msgView.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), errorMessage)
			except:
				printTraceback()
			
			#cpp.compile(self.file, self.codeEdit.root)
	
	def showModuleProperties(self):
		widget, existed = self.getUIFromCache("module-properties")
		
		if self.codeEdit is None:
			return
		
		modulePath = self.localToGlobalImport(stripAll(self.getFilePath()))
		if modulePath:
			parts = self.splitModulePath(modulePath)
			widget.modName.setText(".".join(parts))
			widget.companyName.setText(parts[0])
			widget.projectName.setText(parts[1])
		else:
			widget.modName.setText("Your module is stored outside of the global repository. Please change this.")
			widget.companyName.setText("No company associated. Please create a directory in the global repository.")
		widget.show()
	
	def undoLastAction(self):
		self.codeEdit.undo()
		
	def redoLastAction(self):
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

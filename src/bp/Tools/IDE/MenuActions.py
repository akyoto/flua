from bp.Tools.IDE.Startup import *

class MenuActions:
	
	def newFile(self):
		self.tmpCount += 1
		
		# TODO:
		tmpFileName = "./tmp/New file %d.bp" % (self.tmpCount)
		newCodeEdit = BPCodeEdit(self)
		newCodeEdit.clear()
		newCodeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		self.currentWorkspace.addTab(newCodeEdit, stripAll(tmpFileName))
		self.codeEdit = newCodeEdit
		
		self.dependencyView.clear()
		self.msgView.clear()
		self.xmlView.clear()
		
		self.setFilePath(tmpFileName)
		self.codeEdit.runUpdater()
		self.codeEdit.setFocus()
		
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
		
		if fileName.endswith(".bp"):
			self.loadFileToEditor(fileName)
		elif fileName.endswith(".bpc"):
			self.loadBPCFileToEditor(fileName)
		else:
			return
			
		# Add to recent files list
		#self.recentFiles
		
	def saveFile(self):
		filePath = self.getFilePath()
		if self.isTmpPath(filePath) or filePath.endswith(".bpc"):
			self.saveAsFile()
		else:
			self.codeEdit.save(filePath)
	
	def saveAsFile(self):
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
			
			# If it was saved in the module directory, reload the view
			if getModuleDir() in fixPath(filePath):
				self.moduleView.reloadModuleDirectory()
				
	def undoLastAction(self):
		self.codeEdit.undo()
		
	def redoLastAction(self):
		self.codeEdit.redo()
		
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

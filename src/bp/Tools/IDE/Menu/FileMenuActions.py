from bp.Tools.IDE.Startup import *
from bp.Compiler import *

class FileMenuActions:
	
	def newFile(self, fileName = "", isOpeningFile = False):
		self.tmpCount += 1
		
		# TODO:
		if not fileName:
			fileName = "./tmp/New file %d.bp" % (self.tmpCount)
		newCodeEdit = BPCodeEdit(self)
		newCodeEdit.openingFile = True
		
		newCodeEdit.clear()
		newCodeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		# Is text file?
		if not fileName.endswith(".bp"):
			newCodeEdit.isTextFile = True
		
		self.currentWorkspace.addAndSelectTab(newCodeEdit, stripAll(fileName))
		self.currentWorkspace.updateModifiedState(False)
		
		self.setFilePath(fileName)
		
		newCodeEdit.setFocus()
		
		if not isOpeningFile:
			newCodeEdit.openingFile = False
			newCodeEdit.runUpdater()
			
		return newCodeEdit
		
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
				filter="All Files (*.*);;GLSL Files (*.glsl);;bpc Files (*.bpc);;Any text file (*.*)")
		
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
				ce = self.newFile(fileName, isOpeningFile = True)
				
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
				filter=["bp Files (*.bp)", "All Files (*.*)"][self.codeEdit.isTextFile])
		
		if filePath:
			self.codeEdit.save(filePath)
			self.currentWorkspace.updateCurrentCodeEditName()
			
			# If it was saved in the module directory, reload the view
			if getModuleDir() in fixPath(filePath):
				self.moduleView.reloadModuleDirectory()
			
			return True
		
		return False

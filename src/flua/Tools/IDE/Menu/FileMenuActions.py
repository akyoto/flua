from flua.Tools.IDE.Startup import *
from flua.Compiler import *

class FileMenuActions:
	
	def newFile(self, fileName = "", isOpeningFile = False):
		newCodeEdit = BPCodeEdit(self)
		newCodeEdit.openingFile = True # ???
		
		newCodeEdit.clear()
		newCodeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		# TODO: ...
		if not fileName:
			self.tmpCount += 1
			fileName = "./tmp/New file %d%s" % (self.tmpCount, self.environment.standardFileExtension)
		
		if not fileName.endswith(".flua"):
			newCodeEdit.isTextFile = True
		
		# Set file path
		self.codeEdit = newCodeEdit
		self.setFilePath(fileName)
		
		# Update workspace AFTER SETTING THE FILE PATH
		self.currentWorkspace.addAndSelectTab(newCodeEdit, stripAll(fileName))
		self.currentWorkspace.updateModifiedState(False)
		
		newCodeEdit.setFocus()
		
		if not isOpeningFile:
			newCodeEdit.openingFile = False
			newCodeEdit.runUpdater()
			
		return newCodeEdit
		
	def reopenLastFile(self):
		if not self.currentWorkspace.filesClosed:
			return
		
		self.openFile(self.currentWorkspace.filesClosed.pop())
	
	def openFile(self, path, ignoreLoadingFinished = False):
		if (not self.loadingFinished) and (not ignoreLoadingFinished):
			return None
		
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
				filter="All Files (*.*);;GLSL Files (*.glsl);;Flua Files (*.flua);;Any text file (*.*)")
		
		if not fileName:
			return None
		
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
			
			if fileName.endswith(".flua"):
				self.loadFileToEditor(fileName)
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
		
		return ce
		
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
				filter=["Flua Files (*.flua)", "All Files (*.*)"][self.codeEdit.isTextFile])
		
		if filePath:
			self.codeEdit.save(filePath)
			self.currentWorkspace.updateCurrentCodeEditName()
			
			# If it was saved in the module directory, reload the view
			if getModuleDir() in fixPath(filePath):
				self.moduleView.reloadModuleDirectory()
			
			return True
		
		return False

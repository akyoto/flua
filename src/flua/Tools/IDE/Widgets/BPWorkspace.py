from PyQt4 import QtGui, QtCore
from flua.Tools.IDE.Editor import *
from flua.Compiler.Utils import *

class BPWorkspace(QtGui.QTabWidget):
	
	def __init__(self, bpIDE, wsID):
		parent = bpIDE.workspacesContainer
		super().__init__(parent)
		
		self.bpIDE = bpIDE
		self.wsID = wsID
		self.filesClosed = []
		
		if bpIDE.config.documentModeEnabled:
			self.setDocumentMode(True)
		else:
			self.setDocumentMode(False)
		
		self.setTabsClosable(True)
		self.setMovable(True)
		#self.setTabShape(QtGui.QTabWidget.Triangular)
		self.hide()
		
		self.currentChanged.connect(self.changeCodeEdit)
		self.tabCloseRequested.connect(self.closeCodeEdit)
		parent.layout().addWidget(self)
		
	def addAndSelectTab(self, widget, name):
		index = self.addTab(widget, name)
		self.changeCodeEdit(index)
		widget.qdoc.modificationChanged.connect(self.updateModifiedState)
		
		# Buttons widget in the status bar
		self.bpIDE.workspacesView.updateCurrentWorkspace()
		
	def updateModifiedState(self, state):
		self.updateColors()
		#if state:#and self.bpIDE.codeEdit and self.bpIDE.codeEdit.qdoc.isModified():
		#	self.tabBar().setTabTextColor(self.currentIndex(), self.bpIDE.config.theme["doc-modified"])
		#else:
		#	self.tabBar().setTabTextColor(self.currentIndex(), self.bpIDE.config.theme["doc-unmodified"])
		
	def getWorkspaceID(self):
		return self.wsID
		
	def getTabNameList(self):
		tabNames = []	
		for i in range(self.count()):
			tabNames.append(self.tabText(i))
		return tabNames
		
	def getCodeEditList(self):
		ceList = []
		tabCount = self.count()
		for i in range(tabCount):
			ceList.append(self.widget(i))
		return ceList
		
	def updateColors(self):
		self.tabBar().setFont(self.bpIDE.config.standardFont)
		self.tabBar().setTabTextColor(self.currentIndex(), self.bpIDE.config.theme["doc-selected"])
		
		for i in range(self.count()):
			if self.widget(i).qdoc.isModified():
				self.tabBar().setTabTextColor(i, self.bpIDE.config.theme["doc-modified"])
			elif i != self.currentIndex():
				self.tabBar().setTabTextColor(i, self.bpIDE.config.theme["doc-unmodified"])
		
	def changeCodeEdit(self, index):
		#print("CODE EDIT CHANGED TO INDEX %d" % index)
		
		if index != -1:
			#del self.bpIDE.codeEdit
			self.bpIDE.codeEdit = self.widget(index)
			
			# Set environment
			env = self.bpIDE.codeEdit.environment
			if env:
				self.bpIDE.setEnvironment(env)
			
			self.bpIDE.codeEdit.setFocus()
			self.bpIDE.codeEdit.setCompleter(self.bpIDE.completer)
			
			if ((not self.bpIDE.codeEdit.openingFile) and (not self.bpIDE.codeEdit.isTextFile)):
				self.bpIDE.codeEdit.runUpdater()
				self.bpIDE.backgroundCompileIsUpToDate = False
				self.bpIDE.codeEdit.backgroundCompilerOutstandingTasks = 1
				#self.bpIDE.codeEdit
			
			if self.bpIDE.codeEdit.reloading:
				self.bpIDE.codeEdit.highlighter.rehighlight()
				self.bpIDE.codeEdit.reloading = False
			
			if self.currentIndex() != index:
				self.setCurrentIndex(index)
				
			# Text file or not?
			self.updateIsTextFile()
		
		if self.bpIDE.viewsInitialized:
			self.bpIDE.dependencyView.clear()
			#if self.bpIDE.codeEdit:
			#	self.bpIDE.codeEdit.msgView.clear()
			self.bpIDE.xmlView.clear()
		
		self.bpIDE.updateLineInfo()
		
		# Colors
		self.updateColors()
		
		if self.count():
			self.show()
		else:
			self.hide()
		
	def updateIsTextFile(self):
		# Text file or not?
		isText = self.bpIDE.codeEdit.isTextFile
		self.bpIDE.syntaxSwitcher.setEnabled(not isText)
		self.bpIDE.targetSwitcher.setEnabled(not isText)
			
	def getCodeEditByPath(self, path):
		for i in range(self.count()):
			ce = self.widget(i)
			if ce.getFilePath() == path:
				return i, ce
		
		return -1, None
		
	#def getFilePaths(self):
	#	for i in range(self.count()):
	#		yield self.widget(i).getFilePath()
			
	def getSessionInfo(self):
		for i in range(self.count()):
			ce = self.widget(i)
			yield ce.getFilePath(), ce.getCursorPosition()
		
	def closeCodeEdit(self, index):
		ce = self.widget(index)
		
		if ce:
			path = ce.getFilePath()
			if path and not self.bpIDE.isTmpPath(path):
				self.filesClosed.append(path)
		
		self.removeTab(index)
		
		# Update codeEdit
		#self.changeCodeEdit(self.currentIndex())
		#self.bpIDE.codeEdit = self.widget(self.currentWidget())
		#self.bpIDE.codeEdit.setFocus()
		
		# Update is not needed
		# self.removeTab automatically fires the signal
		# that the index has changed.
		
		# Buttons widget in the status bar
		self.bpIDE.workspacesView.updateCurrentWorkspace()
		
	def closeCurrentCodeEdit(self):
		self.closeCodeEdit(self.currentIndex())
		
	def updateCurrentCodeEditName(self):
		if self.count():
			if self.bpIDE.codeEdit.isTextFile:
				filePath = self.currentWidget().getFilePath()
				tabName = stripDir(filePath)
			else:
				filePath = self.currentWidget().getFilePath()
				moduleName = stripAll(filePath)
				if moduleName == "Mutable" or moduleName == "Immutable":
					tabName = "%s %s" % (moduleName, filePath.split("/")[-2])
				else:
					tabName = moduleName
					
				#self.bpIDE.codeEdit.highlighter.rehighlight()
			
			self.setTabText(self.currentIndex(), tabName)
			self.setTabToolTip(self.currentIndex(), filePath)
			
			# Set environment
			#self.bpIDE.setEnvironment(self.bpIDE.codeEdit.environment)
		
	def activateWorkspace(self):
		#self.tabWidget.show()
		self.changeCodeEdit(self.currentIndex())#bpIDE.codeEdit = self.currentWidget()
		
	def deactivateWorkspace(self):
		#self.tabWidget.show()
		self.bpIDE.codeEdit = None
		self.hide()
		#for workspace in self.bpIDE.workspaces:
		#	workspace.hide()

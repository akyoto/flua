####################################################################
# Header
####################################################################
# blitzprog IDE
# 
# Website: blitzprog.org
# Started: 26.04.2012 (Thu, Apr 26 2012)

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
# 
# This file is part of blitzprog.
# 
# blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import sys
import os
from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
from bp.Tools.IDE.Startup import *

####################################################################
# Code
####################################################################
class BPWorkspace(QtGui.QTabWidget):
	
	def __init__(self, bpIDE, wsID):
		parent = bpIDE.workspacesContainer
		super().__init__(parent)
		
		self.bpIDE = bpIDE
		self.wsID = wsID
		
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
		self.setCurrentIndex(index)
		self.bpIDE.workspacesView.updateCurrentWorkspace()
		
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
		
	def changeCodeEdit(self, index):
		#print("CODE EDIT TO %d" % index)
		if index != -1:
			self.bpIDE.codeEdit = self.widget(index)
			self.bpIDE.codeEdit.setCompleter(self.bpIDE.completer)
			self.bpIDE.codeEdit.runUpdater()
			
			if self.currentIndex() != index:
				self.setCurrentIndex(index)
		
		if self.bpIDE.viewsInitialized:
			self.bpIDE.dependencyView.clear()
			self.bpIDE.msgView.clear()
			self.bpIDE.xmlView.clear()
		
		self.bpIDE.updateLineInfo()
		
		if self.count():
			self.show()
		else:
			self.hide()
			
	def getCodeEditByPath(self, path):
		for i in range(self.count()):
			ce = self.widget(i)
			if ce.getFilePath() == path:
				return i, ce
		
		return -1, None
		
	def closeCodeEdit(self, index):
		if self.widget(index) == self.bpIDE.codeEdit:
			self.bpIDE.codeEdit = None
		
		self.removeTab(index)
		self.bpIDE.workspacesView.updateCurrentWorkspace()
		
	def closeCurrentCodeEdit(self):
		self.closeCodeEdit(self.currentIndex())
		
	def updateCurrentCodeEditName(self):
		pass
		
	def activateWorkspace(self):
		#self.tabWidget.show()
		self.changeCodeEdit(self.currentIndex())#bpIDE.codeEdit = self.currentWidget()
		
	def deactivateWorkspace(self):
		#self.tabWidget.show()
		self.bpIDE.codeEdit = None
		self.hide()

class BPMainWindow(QtGui.QMainWindow, MenuActions, Startup, Benchmarkable):
	
	def __init__(self):
		super().__init__()
		
		print("Module directory: " + getModuleDir())
		print("---")
		
		self.tmpCount = 0
		self.lastBlockPos = -1
		self.lastFunctionCount = -1
		self.intelliEnabled = False
		self.viewsInitialized = False
		self.tmpPath = fixPath(os.path.abspath("./tmp/"))
		self.docks = []
		self.uiCache = dict()
		self.config = None
		self.gitThread = None
		
		# Load config
		self.startBenchmark("Load Configuration")
		self.loadConfig()
		self.endBenchmark()
		
		# Workspaces
		self.currentWorkspace = None
		self.workspacesContainer = QtGui.QWidget(self)
		self.workspacesContainer.setContentsMargins(0, 0, 0, 0)
		hBox = QtGui.QHBoxLayout()
		hBox.setContentsMargins(0, 0, 0, 0)
		self.workspacesContainer.setLayout(hBox)
		
		self.workspaces = [
			BPWorkspace(self, 0),
			BPWorkspace(self, 1),
			BPWorkspace(self, 2),
			BPWorkspace(self, 3),
		]
		
		# Completer
		self.completer = BPCAutoCompleter(self)
		self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
		self.completer.bpcModel.setKeywordList(list(BPCHighlighter.keywords))
		
		self.threaded = True
		
		self.initAll()
		
		# For some weird reason you need to SHOW FIRST, THEN APPLY THE THEME
		self.setCentralWidget(self.workspacesContainer)
		self.showMaximized()
		self.config.applySettings()
		
		#self.openFile("/home/eduard/Projects/bp/src/bp/Core/String/UTF8String.bp")
		
	def setCurrentWorkspace(self, index):
		if self.currentWorkspace is not None:
			self.currentWorkspace.deactivateWorkspace()
		
		self.currentWorkspace = self.workspaces[index]
		self.currentWorkspace.activateWorkspace()
		
	def closeCurrentTab(self):
		self.currentWorkspace.closeCurrentCodeEdit()
		
	def gitPullFinished(self):
		print("Done.")
		
	def loadConfig(self):
		if os.path.isfile("settings.ini"):
			self.config = BPConfiguration(self, "settings.ini")
		else:
			self.config = BPConfiguration(self, "default-settings.ini")
		#self.config.applySettings()
		
	def getUIFromCache(self, uiFileName):
		if not uiFileName in self.uiCache:
			self.uiCache[uiFileName] = uic.loadUi("ui/%s.ui" % uiFileName)
			return self.uiCache[uiFileName], False
		return self.uiCache[uiFileName], True
		
	def onSettingsItemChange(self, current, previous):
		name = current.toolTip(0)
		uiFileName = "preferences/" + name.replace(" - ", ".").lower()
		
		widget, existed = self.getUIFromCache(uiFileName)
		if not existed:
			self.config.initPreferencesWidget(uiFileName, widget)
		
		if previous:
			previousFileName = "preferences/" + previous.toolTip(0).replace(" - ", ".").lower()
			self.uiCache[previousFileName].hide()
			self.preferences.currentBox.layout().removeWidget(self.uiCache[previousFileName])
		
		self.preferences.currentBox.setTitle(name)
		
		self.preferences.currentBox.layout()
		self.preferences.currentBox.layout().addWidget(widget)
		
		widget.show()
	
	def updateLineInfo(self, force = False, updateDependencyView = True):
		if self.codeEdit is None:
			self.lineNumberLabel.setText("")
			self.moduleInfoLabel.setText("")
			return
		
		newBlockPos = self.codeEdit.getLineNumber()
		if force or newBlockPos != self.lastBlockPos:
			self.lastBlockPos = newBlockPos
			selectedNode = None
			
			lineIndex = self.codeEdit.getLineIndex()
			
			funcCount = 0
			if self.processorOutFile:
				funcCount = self.processorOutFile.funcCount
			
			self.lineNumberLabel.setText(" Line %d / %d" % (lineIndex + 1, self.codeEdit.blockCount()))
			self.moduleInfoLabel.setText("%d functions in this file out of %d loaded. " % (funcCount, self.processor.funcCount))
			#self.codeEdit.highlightLine(lineIndex)
			
			#expr = self.codeEdit.getCurrentLine()
			#if expr:
			#	try:
			#		evalExpr = eval(expr)
			#		if evalExpr:
			#			self.evalInfoLabel.setText("%s => %s" % (expr, evalExpr))
			#	except:
			#		self.evalInfoLabel.setText("")
			
			selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
			
			# Check that line
			self.showDependencies(selectedNode, updateDependencyView)
			
			# Clear all highlights
			self.codeEdit.clearHighlights()
		
	def getModulePath(self, importedModule):
		return getModulePath(importedModule, extractDir(self.getFilePath()), self.getProjectPath())
	
	def localToGlobalImport(self, importedModule):
		return fixPath(stripExt(self.getModulePath(importedModule)[len(getModuleDir()):])).replace("/", ".").replace(" ", "_")
	
	def splitModulePath(self, importedModule):
		parts = importedModule.split(".")
		if len(parts) >= 2 and parts[-1] == parts[-2]:
			parts = parts[:-1]
		return parts
	
	def getModuleImportType(self, importedModule):
		return getModuleImportType(importedModule, extractDir(self.getFilePath()), self.getProjectPath())
		
	def postProcessorFinished(self):
		# Update line info
		self.updateLineInfo(force=True, updateDependencyView=False)
		
		# After we parsed the functions, set the text and highlight the file
		if self.codeEdit.disableUpdatesFlag:
			self.codeEdit.disableUpdatesFlag = False
			self.codeEdit.rehighlightFunctionUsage()
		
		self.dependencyView.updateView()
		
		# If the number of functions changed, rehighlight
		if self.processor.getFunctionCount() != self.lastFunctionCount and (self.lastFunctionCount != -1 or self.isTmpFile()):
			self.codeEdit.rehighlightFunctionUsage()
		
		self.lastFunctionCount = self.processor.getFunctionCount()
		
		# If the function name changed, rehighlight
		lineIndex = self.codeEdit.getLineIndex()
		selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
		if tagName(selectedNode) == "function":
			selectedOldNode = self.codeEdit.getOldNodeByLineIndex(lineIndex)
			if tagName(selectedOldNode) == "function":
				nameNew = getElementByTagName(selectedNode, "name")
				nameOld = getElementByTagName(selectedOldNode, "name")
				
				if nameNew.childNodes[0].nodeValue != nameOld.childNodes[0].nodeValue:
					self.codeEdit.rehighlightFunctionUsage()
		#lineIndex = self.codeEdit.getLineIndex()
		#selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
		#previousLineNode = self.codeEdit.getNodeByLineIndex(lineIndex - 1)
		#previousLineOldNode = self.codeEdit.getOldNodeByLineIndex(lineIndex - 1)
		
		#currentLine = self.codeEdit.getCurrentLine()
		#currentTag = tagName(selectedNode)
		#previousLineTag = tagName(previousLineNode)
		#previousLineOldTag = tagName(previousLineOldNode)
		
		#if currentTag == "function" or (previousLineTag == "function" and currentLine == '\t') or (previousLineOldTag == "function" and currentLine == ""):#(tagName(selectedNode) == "function") or ((tagName(previousLine) == "function") and self.getCurrentLine() == "\t"):
		#	self.codeEdit.rehighlightFunctionUsage(selectedNode)
		
	def showDependencies(self, node, updateDependencyView = True):
		self.dependencyView.setNode(node)
		if updateDependencyView:
			self.dependencyView.updateView()
		
		if node:
			self.xmlView.setPlainText(node.toprettyxml())
		else:
			self.xmlView.clear()
		
	def setFilePath(self, path):
		filePath = os.path.abspath(path)
		if self.processor:
			self.processor.setMainFile(filePath)
		self.codeEdit.setFilePath(filePath)
		
	def getProjectPath(self):
		# TODO: Project path
		return self.codeEdit.getFilePath()
		
	def getFilePath(self):
		return self.codeEdit.getFilePath()
		
	def getErrorCount(self):
		return self.msgView.count()
		
	def loadFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		self.setFilePath(fileName)
		
		# Read
		print("-" * 80)
		print("File: %s " % (fileName.rjust(80 - 7)))
		#self.startBenchmark("LoadXMLFile (physically read file)")
		xmlCode = loadXMLFile(self.getFilePath())
		#self.endBenchmark()
		
		# TODO: Clear all views
		self.dependencyView.clear()
		
		# Let's rock!
		self.startBenchmark("[%s] NodeToBPC" % stripDir(fileName))
		self.codeEdit.setXML(xmlCode)
		self.endBenchmark()
		
		self.afterSwitchingFile()
		
	# If you need to do something BEFORE a new file gets loaded, this is the right place
	def beforeSwitchingFile(self):
		# Reset function count
		self.lastFunctionCount = -1
		
		# Clear all module highlights
		self.moduleView.resetAllHighlights()
		
		# Enable dependency view from the very beginning
		self.lastBlockPos = -1
		
	# If you need to do something AFTER a new file gets loaded, this is the right place
	def afterSwitchingFile(self):
		pass
		
	def loadBPCFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		self.setFilePath(fileName)
		
		# Read
		self.startBenchmark("LoadBPCFile (physically read file)")
		with codecs.open(fileName, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		# TODO: Remove all BOMs
		if len(codeText) and codeText[0] == '\ufeff': #codecs.BOM_UTF8:
			codeText = codeText[1:]
		self.endBenchmark()
		
		# Let's rock!
		self.codeEdit.disableUpdatesFlag = True
		self.codeEdit.setPlainText(codeText)
		self.codeEdit.disableUpdatesFlag = False
		self.codeEdit.runUpdater()
		
		#self.startBenchmark("CodeEdit (interpret file)")
		#self.dependencyView.clear()
		#self.codeEdit.setXML(xmlCode)
		#self.endBenchmark()
		
		# Enable dependency view for first line
		self.afterSwitchingFile()
		
	def runPostProcessor(self):
		# TODO: Less cpu usage
		if self.threaded:
			if not self.postProcessorThread.isRunning():
				self.postProcessorThread.startWith(self.codeEdit)
		else:
			self.postProcessorThread.run()
			self.postProcessorFinished()
		
	def isTmpFile(self):
		return self.isTmpPath(self.getFilePath())
		
	def isTmpPath(self, path):
		if not path:
			return True
		
		return extractDir(path) == self.tmpPath
		
	def goToLineEnd(self, lineNum):
		self.codeEdit.setFocus(QtCore.Qt.MouseFocusReason)
		self.codeEdit.goToLineEnd(max(lineNum, 0))
		self.codeEdit.highlightLine(max(lineNum - 1, 0), QtGui.QColor("#ffddcc"))
		
	def getCurrentTheme(self):
		return self.config.theme
		
	def onCursorPosChange(self):
		self.updateLineInfo()
		
	def createDockWidget(self, name, widget, area):
		newDock = QtGui.QDockWidget(name, self)
		#newDock.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
		newDock.setWidget(widget)
		self.addDockWidget(area, newDock)
		
		self.connectVisibilityToViewMenu(name, newDock)
		self.docks.append(newDock)
		
		return newDock
		
	def connectVisibilityToViewMenu(self, name, widget):
		newAction = QtGui.QAction(name, self)
		newAction.setCheckable(True)
		newAction.toggled.connect(widget.setVisible)
		widget.visibilityChanged.connect(newAction.setChecked)
		self.menuView.addAction(newAction)
		
	def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

def main():
	# Create the application
	app = QtGui.QApplication(sys.argv)
	editor = BPMainWindow()
	exitCode = app.exec_()
	
	# In order to not have a segfault
	editor.console.detach()
	
	print("--- EOP: %d ---" % exitCode)
	sys.exit(exitCode)

if __name__ == '__main__':
	try:
		#import cProfile
		#cProfile.run("main()", "bp.prof")
		main()
		#bpMain("/home/eduard/Projects/bp/src/bp/Compiler/Test/Input/main.bpc", "/home/eduard/Projects/bp/src/bp/Compiler/Test/Output/")
	except SystemExit:
		pass
	except OSError:
		print("An instance of Blitzprog IDE is already running")
	except:
		printTraceback()

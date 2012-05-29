﻿####################################################################
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
from bp.Tools.IDE.Syntax import *

####################################################################
# Code
####################################################################
class BPMainWindow(QtGui.QMainWindow, MenuActions, Startup, Benchmarkable):
	
	def __init__(self):
		super().__init__()
		
		print("Module directory: " + getModuleDir())
		print("---")
		
		self.developerFlag = False
		self.tmpCount = 0
		self.lastBlockPos = -1
		self.lastFunctionCount = -1
		self.intelliEnabled = False
		self.viewsInitialized = False
		self.docks = []
		self.dockMenuActions = []
		self.uiCache = dict()
		self.config = None
		self.gitThread = None
		self.geometryState = None
		self.authorName = ""
		self.lastCodeEdit = None
		self.outputCompiler = None
		self.lastShownNode = None
		self.lastShownOutputCompiler = None
		self.currentNode = None
		self.running = 0
		self.backgroundCompileIsUpToDate = False
		
		# Timed
		self.bindFunctionToTimer(self.showDependencies, 200)
		self.bindFunctionToTimer(self.onCompileTimeout, 1000)
		
		# AC
		self.shortCuts = dict()
		self.funcsDict = dict()
		self.classesDict = dict()
		
		# Tmp path
		self.tmpPath = fixPath(os.path.abspath("./tmp/"))
		if self.tmpPath[-1] != "/":
			self.tmpPath += "/"
		
		# TODO: Keymap
		self.ctrlPressed = False
		
		# Load config
		self.startBenchmark("Load Configuration")
		self.loadConfig()
		self.endBenchmark()
		
		# Completer
		self.completer = BPCAutoCompleter(self)
		self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
		self.completer.bpcModel.setKeywordList(list(BPCHighlighter.keywordList))
		
		self.threaded = True
		
		self.initAll()
		
		# For some weird reason you need to SHOW FIRST, THEN APPLY THE THEME
		self.setCentralWidget(self.workspacesContainer)
		self.showMaximized()
		
		self.config.applySettings()
		
		# We love hard coding! ... or maybe not.
		#self.openFile(getModuleDir() + "playground/My playground.bp")
		#self.moduleView.highlightModule("playground.My playground")
		self.newFile()
		self.codeEdit.setPlainText("import playground.Everything\n\n# Check bp.Examples for some beginner topics.\n")
		cursor = self.codeEdit.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		self.codeEdit.setTextCursor(cursor)
		
		# Intercept sys.stdout and sys.stderr
		self.console.watch(self.console.log)
		
		#self.openFile("/home/eduard/Projects/bp/src/bp/Core/String/UTF8String.bp")
		
	#def eventFilter(self, obj, event):
	#	
	#	for i in range(len(self.docks)):
	#		if obj == self.docks[i:
	#			return False
	#			if event.type == QtCore.QEvent.Close:
	#				action = self.dockMenuActions[i]
	#				action.blockSignals(True)
	#				action.setChecked(False)
	#				action.blockSignals(False)
	#				return True
	#			return False
	#	
	#	return super().eventFilter(obj, event)
		
	def bindFunctionToTimer(self, func, interval):
		timer = QtCore.QTimer(self)
		timer.timeout.connect(func)
		timer.start(interval)
		
	def showDependencies(self):#, node, updateDependencyView = True):
		node = self.currentNode
		if node == self.lastShownNode:
			if self.lastShownOutputCompiler != self.outputCompiler:
				self.updateCodeBubble(node)
			return
		self.lastShownNode = self.currentNode
		
		self.dependencyView.setNode(node)
		if (not self.dependenciesViewDock.isHidden()):
			self.dependencyView.updateView()
		
		self.xmlView.setNode(node)
		if not self.xmlViewDock.isHidden():
			self.xmlView.updateView()
			
		self.metaData.setNode(node, self.getXMLDocument())
		if not self.metaData.isHidden():
			self.metaData.updateView()
		
		self.updateCodeBubble(node)
	
	def onCompileTimeout(self):
		# Don't do this if we're actually compiling
		if self.running:
			return
		
		# Create output compiler
		tmpOutputCompiler = self.createOutputCompiler("C++", temporary = True)
		self.outputCompilerThread.startWith(tmpOutputCompiler)
	
	def backgroundCompilerFinished(self):
		if self.outputCompilerThread.lastException:
			#pass
			
			# TODO: What should we do with background compiler error messages?
			
			#self.evalInfoLabel.setText(self.outputCompilerThread.lastException.getMsg())
			if self.codeEdit and self.codeEdit.msgView.count() == 0:
				self.displayOutputCompilerException(self.outputCompilerThread.lastException)
	
	def createOutputCompiler(self, outputTarget, temporary = False):
		if outputTarget.startswith("C++"):
			tmp = CPPOutputCompiler(self.processor, background = temporary)
		elif outputTarget.startswith("Python 3"):
			tmp = PythonOutputCompiler(self.processor, background = temporary)
		
		if temporary:
			return tmp
		else:
			self.outputCompiler = tmp
	
	def updateCodeBubble(self, node):
		if self.codeEdit and self.codeEdit.bubble and not self.running and self.consoleDock.isHidden():
			if node:
				calls = findCalls(node)
				
				# TODO: Optimize as a dict lookup
				# If we have output compiler information
				currentOutFile = None
				if self.outputCompiler:
					self.lastShownOutputCompiler = self.outputCompiler
					cePath = self.getFilePath()
					for outFile in self.outputCompiler.outFiles.values():
						if outFile.file == cePath:
							currentOutFile = outFile
							break
				
				# Let's see if we can get some information about those calls
				code = []
				shownFuncs = dict()
				for call in calls:
					
					if currentOutFile:
						try:
							# Params
							caller, callerType, funcName = currentOutFile.getFunctionCallInfo(call)
							params = getElementByTagName(call, "parameters")
							paramsString, paramTypes = currentOutFile.handleParameters(params)
							
							classImpl = currentOutFile.getClassImplementationByTypeName(callerType)
							
							realFuncDefNode = classImpl.getMatchingFunction(funcName, paramTypes).node
						except:
							realFuncDefNode = None
					else:
						realFuncDefNode = None
					
					funcName = getCalledFuncName(call)
					
					if funcName in self.funcsDict:
						for func in self.funcsDict[funcName].values():
							funcDefinitionNode = func.instruction
							
							# Don't show the same function twice
							if funcDefinitionNode in shownFuncs:
								continue
							
							if realFuncDefNode and realFuncDefNode != funcDefinitionNode:
								continue
							
							shownFuncs[funcDefinitionNode] = True
							
							# Documentation
							doc = getNodeComments(funcDefinitionNode)
							
							# Code
							bpcCode = nodeToBPC(funcDefinitionNode)
							
							# Do we have more information about that call?
							if currentOutFile:
								dataType = None
								try:
									# Return value
									dataType = currentOutFile.getCallDataType(call)
									if dataType and dataType != "void":
										pos = bpcCode.find("\n")
										bpcCode = (bpcCode[:pos] + "  → " + dataType + "") + bpcCode[pos:]
										#bpcCode += "\n" + ("→ " + dataType + "\n").rjust(46)
										#bpcCode = (bpcCode[:pos].ljust(80 - 3 - len(dataType)) + dataType) + bpcCode[pos:] 
								except:
									pass
							
							code.append(bpcCode)
							# Add the documentation afterwards
							if doc:
								code.append(doc)
				
				if code:
					codeText = "\n".join(code)
					lines = codeText.count("\n") + 1
					if lines > 1:
						# Because of Master-of-Weirdness a.k.a. Qt we need to SHOW FIRST, THEN CALCULATE DOCUMENT SIZE
						self.codeEdit.bubble.show()
						
						self.codeEdit.bubble.setPlainText(codeText)
						
						# DO THIS 2 TIMES ELSE YOUR HEIGHT WILL BE INVALID
						self.codeEdit.adjustBubbleSize()
						self.codeEdit.adjustBubbleSize()
						
						self.codeEdit.bubble.show()
				else:
					self.codeEdit.bubble.hide()#setPlainText("Unknown function '%s'" % funcName)
			else:
				self.codeEdit.bubble.hide()
		else:
			self.codeEdit.bubble.hide()
		
	def printL(self, msg):
		print(msg)
		self.consoleDock.show()
		
	def getPostProcessorFile(self, path):
		return self.processor.getCompiledFiles()[path]
		
	def getCurrentPostProcessorFile(self):
		return self.processor.getCompiledFiles()[self.getFilePath()]
		
	def hideEvent(self, event):
		self.geometryState = self.saveState()
		super().hideEvent(event)
		
	def showEvent(self, event):
		super().showEvent(event)
		
		if self.geometryState:
			self.restoreState(self.geometryState)
		
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
		if os.path.isfile(getIDERoot() + "settings.ini"):
			try:
				self.config = BPConfiguration(self, getIDERoot() + "settings.ini")
			except:
				self.config = BPConfiguration(self, getIDERoot() + "default-settings.ini")
		else:
			self.config = BPConfiguration(self, getIDERoot() + "default-settings.ini")
		#self.config.applySettings()
		
	def getUIFromCache(self, uiFileName):
		if not uiFileName in self.uiCache:
			self.uiCache[uiFileName] = uic.loadUi(getIDERoot() + "ui/%s.ui" % uiFileName)
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
	
	def updateLineInfo(self, force = False):#, updateDependencyView = True):
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
				del self.processorOutFile
				self.processorOutFile = None
			
			self.lineNumberLabel.setText(" Line %d / %d" % (lineIndex + 1, self.codeEdit.blockCount()))
			self.moduleInfoLabel.setText("%d / %d functions. " % (funcCount, self.processor.funcCount))
			
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
			self.currentNode = selectedNode
			#self.showDependencies(selectedNode, updateDependencyView)
			
			# Clear all highlights
			self.codeEdit.clearHighlights()
			self.codeEdit.highlightLine(lineIndex, self.config.theme["current-line"])
		
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
		
	def runPostProcessor(self, codeEdit):
		# TODO: Less cpu usage
		if self.threaded:
			if not self.postProcessorThread.isRunning():
				self.postProcessorThread.startWith(codeEdit)
			else:
				codeEdit.disableUpdatesFlag = False
		else:
			#raise "Not implemented in single-threaded mode"
			ppThread = BPPostProcessorThread(self)
			ppThread.codeEdit = codeEdit
			ppThread.run()
			self.postProcessorFinished(ppThread)
		
	def postProcessorFinished(self, ppThread = None):
		if ppThread is None:
			ppThread = self.postProcessorThread
		
		ppCodeEdit = ppThread.codeEdit
		self.processorOutFile = ppThread.ppFile
		
		if self.codeEdit and self.codeEdit.reloading:
			index = self.currentWorkspace.currentIndex()
			self.currentWorkspace.changeCodeEdit(index)
		
		# Update line info
		self.updateLineInfo(force=True)#, updateDependencyView=False)
		
		# Exists?
		if ppCodeEdit is None or ppCodeEdit.isTextFile:
			return
		
		# Msg view
		ppCodeEdit.msgView.updateViewPostProcessor()
		
		# Update auto completer data
		self.classesDict = self.processor.getClassesDict()
		self.funcsDict = self.processor.getFunctionsDict()
		
		if (
				ppCodeEdit.completer
				and
				(
					len(self.funcsDict) != ppCodeEdit.completer.bpcModel.funcListLen
					or len(self.classesDict) != ppCodeEdit.completer.bpcModel.classesListLen
				)
			):
			funcsList = list(self.funcsDict)
			classesList = list(self.classesDict)
			
			self.shortCuts = buildShortcutDict(funcsList)
			ppCodeEdit.completer.bpcModel.setAutoCompleteLists(funcsList, self.shortCuts, classesList)
		
		# After we parsed the functions, set the text and highlight the file
		if ppCodeEdit.disableUpdatesFlag:
			ppCodeEdit.disableUpdatesFlag = False
			ppCodeEdit.rehighlightFunctionUsage()
		
		if (not self.dependenciesViewDock.isHidden()):
			self.dependencyView.updateView()
		
		# If the number of functions changed, rehighlight
		if self.lastCodeEdit == self.codeEdit and self.processor.getFunctionCount() != self.lastFunctionCount and (self.lastFunctionCount != -1 or self.isTmpFile()):
			ppCodeEdit.rehighlightFunctionUsage()
		
		self.lastFunctionCount = self.processor.getFunctionCount()
		self.lastCodeEdit = self.codeEdit
		
		# If the function name changed, rehighlight
		lineIndex = ppCodeEdit.getLineIndex()
		selectedNode = ppCodeEdit.getNodeByLineIndex(lineIndex)
		if tagName(selectedNode) == "function":
			selectedOldNode = ppCodeEdit.getOldNodeByLineIndex(lineIndex)
			if tagName(selectedOldNode) == "function":
				nameNew = getElementByTagName(selectedNode, "name")
				nameOld = getElementByTagName(selectedOldNode, "name")
				
				if nameNew.childNodes[0].nodeValue != nameOld.childNodes[0].nodeValue:
					ppCodeEdit.rehighlightFunctionUsage()
		
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
		
		#del gc.garbage[:]
		
		# Leak detection
		# if 0:
			# import bp.Compiler.Utils.GC as gcInfo
			# print("[--------")
			# gcInfo.showMostCommonTypes()
			# print("BPC Files: %d" % gcInfo.countByTypename("BPCFile"))
			# print("PP Files: %d" % gcInfo.countByTypename("BPPostProcessorFile"))
			# for x in gcInfo.byType("BPPostProcessorFile"):
				# print(x.getFilePath())
			# print("--------]")
		
	def getXMLDocument(self):
		if self.codeEdit is None:
			return None
		
		return self.codeEdit.doc
		
	def forEachCodeEditDo(self, func):
		for workspace in self.workspaces:
			for codeEdit in workspace.getCodeEditList():
				func(codeEdit)
			
	def setFilePath(self, path):
		filePath = os.path.abspath(path)
		if self.processor:
			self.processor.setMainFile(filePath)
		self.codeEdit.setFilePath(filePath)
		
	def getProjectPath(self):
		if self.codeEdit is None:
			return ""
		
		# TODO: Project path
		return self.codeEdit.getFilePath()
		
	def getFilePath(self):
		if self.codeEdit is None:
			return ""
		
		return self.codeEdit.getFilePath()
		
	def getErrorCount(self):
		if not self.codeEdit:
			return 0
		return self.codeEdit.msgView.count()
		
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
		if self.codeEdit is not None:
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
		
	def loadTextFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		with codecs.open(fileName, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		# Let's rock!
		if self.codeEdit:
			self.codeEdit.disableUpdatesFlag = True
			self.codeEdit.isTextFile = True
			#del self.codeEdit.highlighter
			self.codeEdit.highlighter = CPPHighlighter(self.codeEdit.qdoc, self)
			self.codeEdit.setPlainText(codeText)
		
		# Enable dependency view for first line
		self.afterSwitchingFile()
		
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
		if self.codeEdit:
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
		
	def isTmpFile(self):
		return self.isTmpPath(self.getFilePath())
		
	def isTmpPath(self, path):
		if not path:
			return True
		
		return extractDir(path) == self.tmpPath
		
	def goToLineEnd(self, lineNum):
		if not self.codeEdit:
			return
		
		self.codeEdit.setFocus(QtCore.Qt.MouseFocusReason)
		self.codeEdit.goToLineEnd(max(lineNum, 0))
		self.codeEdit.highlightLine(max(lineNum - 1, 0), self.config.theme["error-line"])
		
	def getCurrentTheme(self):
		return self.config.theme
		
	def onCursorPosChange(self):
		self.updateLineInfo()
		
	def createDockWidget(self, name, widget, area):
		newDock = QtGui.QDockWidget(name, self)
		#newDock.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
		newDock.setWidget(widget)
		newDock.setObjectName(name)
		#newDock.installEventFilter(self)
		self.addDockWidget(area, newDock)
		
		self.dockMenuActions.append(self.connectVisibilityToViewMenu(name, newDock))
		self.docks.append(newDock)
		
		return newDock
		
	def connectVisibilityToViewMenu(self, name, widget):
		newAction = QtGui.QAction(name, self)
		newAction.setCheckable(True)
		newAction.toggled.connect(widget.setVisible)
		widget.visibilityChanged.connect(newAction.setChecked)
		self.menuView.addAction(newAction)
		return newAction
		
	def notify(self, msg, title = "Notification"):
		msgBox = QtGui.QMessageBox(self)
		msgBox.setWindowTitle(title)
		msgBox.setText(msg)
		msgBox.setIcon(QtGui.QMessageBox.Information)
		msgBox.setStyleSheet(self.config.dialogStyleSheet)
		msgBox.exec()
		
	def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

def main():
	# Create the application
	#gc.set_debug(gc.DEBUG_LEAK)
	#gc.enable()
	app = QtGui.QApplication(sys.argv)
	editor = BPMainWindow()
	exitCode = app.exec_()
	
	# In order to not have a segfault
	editor.console.detach()
	
	# Save config
	editor.config.saveSettings()
	
	print("--- EOP: %d ---" % exitCode)
	sys.exit(exitCode)

if __name__ == '__main__':
	try:
		#import cProfile
		#cProfile.run("main()")#, "bp.prof")
		main()
	except SystemExit:
		pass
	except:
		printTraceback()

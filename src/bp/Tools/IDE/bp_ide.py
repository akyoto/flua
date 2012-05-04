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
from bp.Tools.IDE.Utils import *
from bp.Tools.IDE.Editor import *
from bp.Tools.IDE.Widgets import *

####################################################################
# Code
####################################################################
class BPPostProcessorThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.processor = bpIDE.processor
		self.finished.connect(self.bpIDE.postProcessorFinished)
		
	def run(self):
		try:
			self.startBenchmark("[%s] PostProcessor" % stripDir(self.bpIDE.getFilePath()))
			self.processor.resetDTreesForFile(self.bpIDE.getFilePath())
			self.bpIDE.processorOutFile = self.processor.process(self.bpIDE.codeEdit.root, self.bpIDE.getFilePath())
			self.endBenchmark()
		except PostProcessorException as e:
			errorMessage = e.getMsg()
			self.bpIDE.msgView.addMessage(errorMessage)

class BPMainWindow(QtGui.QMainWindow, Benchmarkable):
	
	# INIT START
	
	def __init__(self):
		super().__init__()
		
		print("Module directory: " + getModuleDir())
		print("---")
		
		self.tmpCount = 0
		self.lastBlockPos = -1
		self.lastFunctionCount = -1
		self.intelliEnabled = False
		self.tmpPath = fixPath(os.path.abspath("./tmp/"))
		self.docks = []
		self.monospaceFont = QtGui.QFont("monospace", 9)
		self.standardFont = QtGui.QFont("SansSerif", 9)
		
		self.threaded = True
		
		self.initTheme()
		self.initUI()
		self.initCompiler()
		
		self.applyMonospaceFont(self.monospaceFont)
		self.applyStandardFont(self.standardFont)
		#self.openFile("/home/eduard/Projects/bp/src/bp/Core/String/UTF8String.bp")
		
	def initUI(self):
		uic.loadUi("blitzprog-ide.ui", self)
		self.initToolBar()
		
		# StatusBar
		self.statusBar.setFont(QtGui.QFont("SansSerif", 7))
		
		# Window
		#self.setWindowTitle("Blitzprog IDE")
		#self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.setGeometry(0, 0, 1000, 650)
		self.center()
		
		# Status bar
		self.lineNumberLabel = QtGui.QLabel()
		self.moduleInfoLabel = QtGui.QLabel()
		self.evalInfoLabel = QtGui.QLabel()
		self.lineNumberLabel.setMinimumWidth(100)
		self.progressBar = QtGui.QProgressBar(self.statusBar)
		self.progressBar.setTextVisible(False)
		self.progressBar.hide()
		#spacer1 = QtGui.QWidget(self.statusBar)
		#spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#spacer2 = QtGui.QWidget(self.statusBar)
		#spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#self.statusBar.addPermanentWidget(spacer1)
		self.statusBar.addWidget(self.lineNumberLabel)
		self.statusBar.addWidget(self.moduleInfoLabel)
		self.statusBar.addWidget(self.evalInfoLabel)
		self.statusBar.addPermanentWidget(self.progressBar, 0)
		#self.statusBar.setLayout(hBoxLayout)
		
		self.initDocks()
		
		self.codeEdit = BPCodeEdit(self)
		self.codeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		self.initActions()
		self.setCentralWidget(self.codeEdit)
		
		#self.statusBar.hide()
		self.toolBar.hide()
		self.syntaxSwitcherBar.hide()
		self.show()
		
	def initDocks(self):
		# Message view
		self.msgView = BPMessageView(self)
		
		# XML view
		self.xmlView = XMLCodeEdit(self)
		self.xmlView.setReadOnly(1)
		
		# Dependency view
		self.dependencyView = BPDependencyView(self)
		self.dependencyView.setReadOnly(1)
		
		# File view
		self.fileView = BPFileBrowser(self, getModuleDir())
		
		# Module view
		self.moduleView = BPModuleBrowser(self, getModuleDir())
		
		# Scribble - I absolutely love this feature in Geany!
		# It's always the little things that are awesome :)
		self.scribble = BPScribbleWidget(self, "miscellaneous/scribble.txt")
		
		# IntelliView enabled?
		if self.intelliEnabled:
			# IntelliView
			self.intelliView = BPIntelliView(self)
			
			# IntelliView Dock
			self.intelliView.addIntelligentWidget(self.msgView)
			self.intelliView.addIntelligentWidget(self.dependencyView)
			#self.intelliView.addIntelligentWidget(self.xmlView)
			self.intelliView.vBox.addStretch(1)
			self.intelliViewDock = self.createDockWidget("IntelliView", self.intelliView, QtCore.Qt.RightDockWidgetArea)
		else:
			self.moduleViewDock = self.createDockWidget("Modules", self.moduleView, QtCore.Qt.LeftDockWidgetArea)
			self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.RightDockWidgetArea)
			self.dependenciesViewDock = self.createDockWidget("Dependencies", self.dependencyView, QtCore.Qt.RightDockWidgetArea)
			self.xmlViewDock = self.createDockWidget("XML", self.xmlView, QtCore.Qt.RightDockWidgetArea)
			self.fileViewDock = self.createDockWidget("Files", self.fileView, QtCore.Qt.RightDockWidgetArea)
			self.scribbleDock = self.createDockWidget("Scribble", self.scribble, QtCore.Qt.RightDockWidgetArea)
			
		self.dependenciesViewDock.hide()
		#self.xmlViewDock.hide()
		self.scribbleDock.hide()
		self.fileViewDock.hide()
		
	def initActions(self):
		# File
		self.actionNew.triggered.connect(self.newFile)
		self.actionOpen.triggered.connect(self.openFile)
		self.actionSave.triggered.connect(self.saveFile)
		self.actionSaveAs.triggered.connect(self.saveAsFile)
		self.actionExit.triggered.connect(self.close)
		
		# Edit
		self.actionUndo.triggered.connect(self.undoLastAction)
		self.actionRedo.triggered.connect(self.redoLastAction)
		self.actionCopy.triggered.connect(self.codeEdit.copy)
		self.actionCut.triggered.connect(self.codeEdit.cut)
		self.actionPaste.triggered.connect(self.codeEdit.paste)
		
		# Module
		self.actionRun.triggered.connect(self.runModule)
		
		# Help
		self.actionAbout.triggered.connect(self.about)
		
	def initTheme(self):
		lightTheme = {
			'default': format("#272727"),
			'default-background': "#ffffff",
			'keyword': format('blue'),
			'operator': format('red'),
			'brace': format('darkGray'),
			'comma': format('#555555'),
			'output-target': format('#666666'),
			'include-file': format('#666666'),
			'string': format('#009000'),
			'string2': format('darkMagenta'),
			'comment': format('darkGray', 'italic'),
			'self': format('black', 'italic'),
			'number': format('brown'),
			'hex-number': format('brown'),
			'own-function': format('#373737', 'bold'),
			'local-module-import': format('#661166', 'bold'),
			'project-module-import': format('#378737', 'bold'),
			'global-module-import': format('#373737', 'bold'),
			'current-line' : None#QtGui.QColor("#fefefe")
		}
		
		darkTheme = {
			'default': format("#eeeeee"),
			'default-background': "#272727",
			'keyword': format('orange'),
			'operator': format('#ff2010'),
			'brace': format('darkGray'),
			'comma': format('#777777'),
			'output-target': format('#888888'),
			'include-file': format('#888888'),
			'string': format('#00c000'),
			'string2': format('darkMagenta'),
			'comment': format('darkGray', 'italic'),
			'self': format('black', 'italic'),
			'number': format('#00cccc'),
			'hex-number': format('brown'),
			'own-function': format('#ff8000', 'bold'),
			'local-module-import': format('#77ee77', 'bold'),
			'project-module-import': format('#dddddd', 'bold'),
			'global-module-import': format('#22dd22', 'bold'),
			'current-line' : None#QtGui.QColor("#fefefe")
		}
		
		self.currentTheme = lightTheme
		
	def initCompiler(self):
		self.postProcessorThread = None
		self.bpc = BPCCompiler(getModuleDir(), ".bp")
		self.processor = BPPostProcessor()
		self.processorOutFile = None
		self.postProcessorThread = BPPostProcessorThread(self)
		self.newFile()
		
	def initToolBar(self):
		# Syntax switcher
		syntaxSwitcher = QtGui.QComboBox()
		syntaxSwitcher.addItem("BPC Syntax")
		syntaxSwitcher.addItem("C++/Java Syntax")
		syntaxSwitcher.addItem("Python Syntax")
		syntaxSwitcher.addItem("Ruby Syntax")
		
		spacerWidget = QtGui.QWidget()
		spacerWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		
		# Tool bar
		self.syntaxSwitcherBar.addSeparator()
		self.syntaxSwitcherBar.addWidget(spacerWidget)
		self.syntaxSwitcherBar.addWidget(syntaxSwitcher)
		self.syntaxSwitcherBar.addSeparator()
		
	# INIT END
	
	def updateLineInfo(self, force = False, updateDependencyView = True):
		newBlockPos = self.codeEdit.getLineNumber()
		if force or newBlockPos != self.lastBlockPos:
			self.lastBlockPos = newBlockPos
			selectedNode = None
			
			lineIndex = self.codeEdit.getLineIndex()
			
			funcCount = 0
			if self.processorOutFile:
				funcCount = self.processorOutFile.funcCount
			
			self.lineNumberLabel.setText(" Line %d / %d" % (lineIndex + 1, self.codeEdit.blockCount()))
			self.moduleInfoLabel.setText("%d functions in this file out of %d loaded" % (funcCount, self.processor.funcCount))
			
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
		
	def runModule(self):
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
		
	def showDependencies(self, node, updateDependencyView = True):
		self.dependencyView.setNode(node)
		if updateDependencyView:
			self.dependencyView.updateView()
		
		if node:
			self.xmlView.setPlainText(node.toprettyxml())
		else:
			self.xmlView.clear()
		
	def setFilePath(self, path):
		self.filePath = os.path.abspath(path)
		if self.processor:
			self.processor.setMainFile(self.filePath)
		self.codeEdit.setFilePath(self.filePath)
		
	def getProjectPath(self):
		# TODO: Project path
		return self.codeEdit.getFilePath()
		
	def getFilePath(self):
		return self.codeEdit.getFilePath()
		
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
				self.postProcessorThread.start()
		else:
			self.postProcessorThread.run()
			self.postProcessorFinished()
		
	def applyMonospaceFont(self, font):
		# Widgets with monospace font
		self.codeEdit.setFont(font)
		self.xmlView.setFont(font)
		self.dependencyView.setFont(font)
		
	def applyStandardFont(self, font):
		QtGui.QToolTip.setFont(font)
		
		# Widgets with normal font
		self.moduleView.setFont(font)
		self.msgView.setFont(font)
		
		# All docks
		for dock in self.docks:
			dock.setFont(font)
		
	def applyMenuFont(self, font):
		self.menuBar.setFont(font)
		for menuItem in self.menuBar.children():
			menuItem.setFont(font)
	
	def newFile(self):
		self.codeEdit.clear()
		self.dependencyView.clear()
		self.msgView.clear()
		self.xmlView.clear()
		
		self.tmpCount += 1
		self.setFilePath("./tmp/tmp%d.bp" % (self.tmpCount))
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
		return self.currentTheme
		
	def onCursorPosChange(self):
		self.updateLineInfo()
		
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
		
	def closeEvent(self, event):
		self.scribble.saveScribble()
		event.accept()
		return
		
		reply = QtGui.QMessageBox.question(self,
				"Message",
				"Are you sure you want to quit?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
				QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

def main():
	# Create the application
	app = QtGui.QApplication(sys.argv)
	editor = BPMainWindow()
	sys.exit(app.exec_())

if __name__ == '__main__':
	try:
		#import cProfile
		#cProfile.run("main()", "bp.prof")
		main()
		#bpMain("/home/eduard/Projects/bp/src/bp/Compiler/Test/Input/main.bpc", "/home/eduard/Projects/bp/src/bp/Compiler/Test/Output/")
	except SystemExit:
		pass
	#except OSError:
	#	print("An instance of Blitzprog IDE is already running")
	except:
		printTraceback()

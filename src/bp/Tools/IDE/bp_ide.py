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
			self.startBenchmark("BP  PostProcessor (%s)" % stripDir(self.bpIDE.getFilePath()))
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
		
		self.lastBlockPos = -1
		self.lastFunctionCount = -1
		self.intelliEnabled = False
		
		self.threaded = True
		
		self.initTheme()
		self.initUI()
		self.initCompiler()
		self.setFilePath("./tmp/tmp.bp")
		#self.openFile("/home/eduard/Projects/bp/src/bp/Compiler/Test/Input/main.bp")
		
	def initUI(self):
		uic.loadUi("blitzprog-ide.ui", self)
		self.initToolBar()
		
		# Font
		QtGui.QToolTip.setFont(QtGui.QFont("SansSerif", 10))
		self.statusBar().setFont(QtGui.QFont("SansSerif", 7))
		
		# Window
		#self.setWindowTitle("Blitzprog IDE")
		#self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.setGeometry(0, 0, 1000, 650)
		self.center()
		
		self.statusBar().showMessage("Ready")
		
		self.initDocks()
		
		self.codeEdit = BPCodeEdit(self)
		self.codeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		self.initActions()
		self.setCentralWidget(self.codeEdit)
		
		#self.statusBar().hide()
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
			self.moduleViewDock = self.createDockWidget("Modules", self.moduleView, QtCore.Qt.RightDockWidgetArea)
			self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.RightDockWidgetArea)
			self.dependenciesViewDock = self.createDockWidget("Dependencies", self.dependencyView, QtCore.Qt.RightDockWidgetArea)
			self.xmlViewDock = self.createDockWidget("XML", self.xmlView, QtCore.Qt.RightDockWidgetArea)
			self.fileViewDock = self.createDockWidget("Files", self.fileView, QtCore.Qt.RightDockWidgetArea)
			
		self.dependenciesViewDock.hide()
		self.xmlViewDock.hide()
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
		
		# Module
		self.actionRun.triggered.connect(self.runModule)
		
		# Help
		self.actionAbout.triggered.connect(self.about)
		
	def initTheme(self):
		defaultTheme = {
			'default': format("#272727"),
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
			'local-module-import': format('#770077', 'bold'),
			'project-module-import': format('#378737', 'bold'),
			'global-module-import': format('#373737', 'bold'),
			'current-line' : None#QtGui.QColor("#fefefe")
		}
		
		self.currentTheme = defaultTheme
		
	def initCompiler(self):
		self.postProcessorThread = None
		self.bpc = BPCCompiler(getModuleDir(), ".bp")
		self.processor = BPPostProcessor()
		self.processorOutFile = None
		self.postProcessorThread = BPPostProcessorThread(self)
		self.codeEdit.clear()
		
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
			self.statusBar().showMessage("Line %d / %d" % (lineIndex + 1, self.codeEdit.blockCount()))
			selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
			
			# Check that line
			self.showDependencies(selectedNode, updateDependencyView)
			
			# Clear all highlights
			self.codeEdit.clearHighlights()
		
	def postProcessorFinished(self):
		# After we parsed the functions, set the text and highlight the file
		if self.codeEdit.futureText:
			self.codeEdit.setPlainText(self.codeEdit.futureText)
			self.codeEdit.disableUpdateFlag = False
		
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
				self.msgView.addLineBasedMessage(1, errorMessage)
			
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
		self.lastFunctionCount = -1
		self.setFilePath(fileName)
		
		# Read
		self.startBenchmark("LoadXMLFile (physically read file)")
		xmlCode = loadXMLFile(self.getFilePath())
		self.endBenchmark()
		
		# TODO: Clear all views
		self.dependencyView.clear()
		
		# Let's rock!
		self.startBenchmark("CodeEdit (interpret file)")
		self.codeEdit.setXML(xmlCode)
		self.endBenchmark()
		
		# Enable dependency view for first line
		self.lastBlockPos = -1
		
	def loadBPCFileToEditor(self, fileName):
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
		self.lastBlockPos = -1
		
	def runPostProcessor(self):
		# TODO: Less cpu usage
		if self.threaded:
			if not self.postProcessorThread.isRunning():
				self.postProcessorThread.start()
		else:
			self.postProcessorThread.run()
			self.postProcessorFinished()
		
	def newFile(self):
		self.codeEdit.clear()
		self.dependencyView.clear()
		self.msgView.clear()
		self.xmlView.clear()
		#print(self.codeEdit.)
		
	def openFile(self, path):
		fileName = path
		if not fileName:
			fileName = QtGui.QFileDialog.getOpenFileName(
				parent=self,
				caption="Open File",
				directory=getModuleDir(),
				filter="bp Files (*.bp);;bpc Files (*.bpc)")
		
		if fileName.endswith(".bp"):
			self.loadFileToEditor(fileName)
		elif fileName.endswith(".bpc"):
			self.loadBPCFileToEditor(fileName)
		
	def saveFile(self):
		filePath = self.getFilePath()
		if self.isTmpPath(filePath) or filePath.endswith(".bpc"):
			self.saveAsFile()
		else:
			self.codeEdit.save(filePath)
	
	def saveAsFile(self):
		filePath = QtGui.QFileDialog.getSaveFileName(
				parent=self,
				caption="Save File",
				directory=getModuleDir(),
				filter="bp Files (*.bp)")
		
		if filePath:
			self.codeEdit.save(filePath)
		
	def isTmpFile(self):
		return self.isTmpPath(self.getFilePath())
		
	def isTmpPath(self, path):
		if not path:
			return True
		
		return extractDir(path) == fixPath(os.path.abspath("./tmp/") + "/")
		
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

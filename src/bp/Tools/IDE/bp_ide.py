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
from bp.Tools.IDE.Editor import *

####################################################################
# Functions
####################################################################
def format(color, style=''):
	"""Return a QTextCharFormat with the given attributes.
	"""
	_color = QtGui.QColor()
	_color.setNamedColor(color)
	
	_format = QtGui.QTextCharFormat()
	_format.setForeground(_color)
	if 'bold' in style:
		_format.setFontWeight(QtGui.QFont.Bold)
	if 'italic' in style:
		_format.setFontItalic(True)
	
	return _format

####################################################################
# Code
####################################################################
class BPMessageView(QtGui.QListWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpMainWidget = parent
		self.setWordWrap(True)
		self.icon = QtGui.QIcon("images/tango/status/dialog-warning.svg")
		self.itemClicked.connect(self.goToLineOfItem)
		
	def goToLineOfItem(self, item):
		lineNum = int(item.statusTip())
		self.bpMainWidget.goToLineEnd(lineNum)
		
	def addLineBasedMessage(self, lineNumber, msg):
		newItem = QtGui.QListWidgetItem(self.icon, msg)
		newItem.setStatusTip(str(lineNumber))
		self.addItem(newItem)

class BPMainWindow(QtGui.QMainWindow, Benchmarkable):
	
	def __init__(self):
		super().__init__()
		
		print("Module directory: " + getModuleDir())
		print("---")
		
		self.lastBlockPos = -1
		
		self.initTheme()
		self.initUI()
		self.initCompiler()
		#self.openFile("/home/eduard/Projects/bp/src/bp/Compiler/Test/Input/main.bp")
		
	def initTheme(self):
		defaultTheme = {
			'default': format("#272727"),
			'keyword': format('blue'),
			'operator': format('red'),
			'brace': format('darkGray'),
			'output-target': format('#666666'),
			'include-file': format('#666666'),
			'string': format('#009000'),
			'string2': format('darkMagenta'),
			'comment': format('darkGray', 'italic'),
			'self': format('black', 'italic'),
			'numbers': format('brown'),
			'own-function': format('#272727', 'bold'),
			'current-line' : None#QtGui.QColor("#fefefe")
		}
		
		self.currentTheme = defaultTheme
		
	def initCompiler(self):
		self.bpc = BPCCompiler(getModuleDir())
		self.processor = None
		
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
		self.toolBar.addSeparator()
		self.toolBar.addWidget(spacerWidget)
		self.toolBar.addWidget(syntaxSwitcher)
		self.toolBar.addSeparator()
		
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
		
		self.contextView = XMLCodeEdit(self)
		self.contextView.setReadOnly(1)
		
		self.xmlView = XMLCodeEdit(self)
		self.xmlView.setReadOnly(1)
		
		self.msgView = BPMessageView(self)
		
		self.dependenciesViewDock = self.createDockWidget("Dependencies", self.contextView, QtCore.Qt.RightDockWidgetArea)
		self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.RightDockWidgetArea)
		self.xmlViewDock = self.createDockWidget("XML View", self.xmlView, QtCore.Qt.RightDockWidgetArea)
		
		self.dependenciesViewDock.hide()
		#self.xmlViewDock.hide()
		
		self.codeEdit = BPCodeEdit(self)
		self.codeEdit.cursorPositionChanged.connect(self.onCursorPosChange)
		
		self.initActions()
		self.setCentralWidget(self.codeEdit)
		self.show()
		
	def getCurrentTheme(self):
		return self.currentTheme
		
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
		
	def goToLineEnd(self, lineNum):
		self.codeEdit.setFocus(QtCore.Qt.MouseFocusReason)
		self.codeEdit.goToLineEnd(lineNum)
		self.codeEdit.highlightLine(lineNum - 1, QtGui.QColor("#ffddcc"))
		
	def onCursorPosChange(self):
		self.updateLineInfo()
		
	def updateLineInfo(self, force = False):
		newBlockPos = self.codeEdit.getLineNumber()
		if force or newBlockPos != self.lastBlockPos:
			self.lastBlockPos = newBlockPos
			selectedNode = None
			
			lineIndex = self.codeEdit.getLineIndex()
			self.statusBar().showMessage("Line %d" % (lineIndex + 1))
			selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
			
			# Check that line
			self.showDependencies(selectedNode)
			
			# Clear all highlights
			self.codeEdit.clearHighlights()
		
	def showDependencies(self, node):
		dTree = None
		if node in dTreeByNode:
			dTree = dTreeByNode[node]
		#elif node:
		#	print("Node not registered")
		
		if dTree:
			self.contextView.setPlainText(dTree.getDependencyPreview())
		else:
			self.contextView.clear()
			
		if node:
			self.xmlView.setPlainText(node.toprettyxml())
		else:
			self.xmlView.clear()
		
	def getFilePath(self):
		return self.codeEdit.getFilePath()
		
	def loadFileToEditor(self, fileName):
		self.codeEdit.setFilePath(fileName)
		
		# Read
		self.startBenchmark("LoadXMLFile (physically read file)")
		xmlCode = loadXMLFile(self.getFilePath())
		self.endBenchmark()
		
		# Let's rock!
		self.startBenchmark("CodeEdit (interpret file)")
		self.contextView.clear()
		self.codeEdit.setXML(xmlCode)
		self.endBenchmark()
		
		self.startBenchmark("BPPostProcessor (generate DTrees)")
		self.processor = BPPostProcessor()
		self.processor.process(self.codeEdit.root, self.getFilePath())
		self.endBenchmark()
		
		# Enable dependency view for first line
		self.lastBlockPos = -1
		
	def newFile(self):
		self.codeEdit.clear()
		self.contextView.clear()
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
				filter="bp Files (*.bp)")
		
		if fileName:
			self.loadFileToEditor(fileName)
		
	def saveFile(self):
		filePath = self.codeEdit.getFilePath()
		if not filePath:
			filePath = QtGui.QFileDialog.getSaveFileName(
				parent=self,
				caption="Save File",
				directory=getModuleDir(),
				filter="bp Files (*.bp)")
		
		if filePath:
			self.codeEdit.save(filePath)
	
	def saveAsFile(self):
		filePath = QtGui.QFileDialog.getSaveFileName(
				parent=self,
				caption="Save File",
				directory=getModuleDir(),
				filter="bp Files (*.bp)")
		
		if filePath:
			self.codeEdit.save(filePath)
		
	def runModule(self):
		outputTarget = "C++"
		
		if outputTarget == "C++":
			#print(self.processor.getCompiledFilesList())
			cpp = CPPOutputCompiler(self.processor)
			cpp.compile(self.processor.getCompiledFilesList()[0])
			cpp.writeToFS()
			exe = cpp.build()
			cpp.execute(exe)
			#cpp.compile(self.file, self.codeEdit.root)
		
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
		newDock.setWidget(widget)
		self.addDockWidget(area, newDock)
		
		newAction = QtGui.QAction(name, self)
		newAction.setCheckable(True)
		newAction.toggled.connect(newDock.setVisible)
		newDock.visibilityChanged.connect(newAction.setChecked)
		self.menuView.addAction(newAction)
		
		return newDock
		
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
		main()
	except SystemExit:
		pass
	#except OSError:
	#	print("An instance of Blitzprog IDE is already running")
	except:
		printTraceback()

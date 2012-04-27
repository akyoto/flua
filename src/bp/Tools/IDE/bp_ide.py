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
from PyQt4 import QtGui, QtCore
from bp.Compiler import *

####################################################################
# Globals
####################################################################

####################################################################
# Syntax modules
####################################################################
from bp.Tools.IDE.Syntax import *

####################################################################
# Code
####################################################################
class BPCodeEdit(QtGui.QTextEdit):
	
	def __init__(self):
		super(BPCodeEdit, self).__init__()
		self.highlighter = BPCHighlighter(self.document())
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
		self.converter = None
		self.lines = []
		
	def setXML(self, xmlCode):
		self.doc = parseString(xmlCode.encode( "utf-8" ))
		self.root = self.doc.documentElement
		codeNode = getElementByTagName(self.root, "code")
		
		self.converter = LineToNodeConverter()
		bpcCode = nodeToBPC(codeNode, 0, self.converter)
		self.lines = bpcCode.split("\n")
		
		# Remove two empty lines
		if 0:
			offset = 0
			lastLineEmpty = False
			for index in range(0, len(self.lines)):
				i = index + offset
				if i < len(self.lines):
					line = self.lines[i]
					if line.strip() == "":
						if lastLineEmpty:
							self.removeLineNumber(i)
							offset -= 1
						lastLineEmpty = True
					else:
						lastLineEmpty = False
				else:
					break
		
		self.setText("\n".join(self.lines))
		
	def removeLineNumber(self, index):
		# TODO: Fix index by +1 -1
		self.lines = self.lines[:index-1] + self.lines[index:]
		self.converter.lineToNode = self.converter.lineToNode[:index-1] + self.converter.lineToNode[index:]
		
class BPEditor(QtGui.QMainWindow):
	
	def __init__(self):
		super(BPEditor, self).__init__()
		self.initUI()
		self.initCompiler()
		
	def initCompiler(self):
		self.bpc = BPCCompiler(modDir)
		
	def initMenu(self):
		# File menu actions
		newAction = action = QtGui.QAction(QtGui.QIcon("images/new.svg"), "&New", self)
		action.setShortcut("Ctrl+N")
		action.setStatusTip("Create new file")
		action.triggered.connect(self.newFile)
		
		openAction = action = QtGui.QAction(QtGui.QIcon("images/open.svg"), "&Open", self)
		action.setShortcut("Ctrl+O")
		action.setStatusTip("Open new file")
		action.triggered.connect(self.openFile)
		
		saveAction = action = QtGui.QAction(QtGui.QIcon("images/save.svg"), "&Save", self)
		action.setShortcut("Ctrl+S")
		action.setStatusTip("Save file")
		action.triggered.connect(self.saveFile)
		
		saveAsAction = action = QtGui.QAction(QtGui.QIcon("images/save-as.svg"), "Save &As", self)
		action.setShortcut("Ctrl+Shift+S")
		action.setStatusTip("Save as another file")
		action.triggered.connect(self.saveAsFile)
		
		exitAction = action = QtGui.QAction(QtGui.QIcon("images/exit.svg"), "&Exit", self)		
		action.setShortcut("Ctrl+Q")
		action.setStatusTip("Exit application")
		action.triggered.connect(self.close)
		
		# Edit
		undoAction = action = QtGui.QAction(QtGui.QIcon("images/undo.svg"), "&Undo", self)
		action.setShortcut("Ctrl+Z")
		action.setStatusTip("Undo last action")
		action.triggered.connect(self.undoLastAction)
		
		redoAction = action = QtGui.QAction(QtGui.QIcon("images/redo.svg"), "&Redo", self)
		action.setShortcut("Ctrl+Y")
		action.setStatusTip("Redo last action")
		action.triggered.connect(self.redoLastAction)
		
		# Module menu actions
		runModuleAction = action = QtGui.QAction(QtGui.QIcon("images/run.svg"), "&Run", self)
		action.setShortcut("Ctrl+R")
		action.setStatusTip("Run")
		action.triggered.connect(self.runModule)
		
		# Help menu actions
		aboutAction = action = QtGui.QAction(QtGui.QIcon("images/about.svg"), "&About", self)
		action.triggered.connect(self.about)
		
		# Menu bar
		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu("&File")
		fileMenu.addAction(newAction)
		fileMenu.addAction(openAction)
		fileMenu.addSeparator()
		fileMenu.addAction(saveAction)
		fileMenu.addAction(saveAsAction)
		fileMenu.addSeparator()
		fileMenu.addAction(exitAction)
		
		editMenu = menuBar.addMenu("&Edit")
		editMenu.addAction(undoAction)
		editMenu.addAction(redoAction)
		
		moduleMenu = menuBar.addMenu("&Module")
		moduleMenu.addAction(runModuleAction)
		
		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(aboutAction)
		
		# Syntax switcher
		syntaxSwitcher = QtGui.QComboBox()
		syntaxSwitcher.addItem("BPC Syntax")
		syntaxSwitcher.addItem("C++/Java Syntax")
		syntaxSwitcher.addItem("Python Syntax")
		syntaxSwitcher.addItem("Ruby Syntax")
		
		spacerWidget = QtGui.QWidget()
		spacerWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		
		# Tool bar
		self.toolbar = self.addToolBar("Exit")
		self.toolbar.addAction(newAction)
		self.toolbar.addAction(openAction)
		self.toolbar.addSeparator()
		self.toolbar.addAction(saveAction)
		self.toolbar.addSeparator()
		self.toolbar.addAction(runModuleAction)
		self.toolbar.addSeparator()
		self.toolbar.addWidget(spacerWidget)
		self.toolbar.addWidget(syntaxSwitcher)
		self.toolbar.addSeparator()
		
	def initUI(self):
		self.initMenu()
		
		QtGui.QToolTip.setFont(QtGui.QFont("SansSerif", 10))
		
		self.setGeometry(0, 0, 1000, 650)
		self.setWindowTitle("Blitzprog IDE")
		self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.center()
		
		self.statusBar().showMessage("Ready")
		
		self.editPanel = QtGui.QWidget()
		self.codeEdit = BPCodeEdit()
		self.codeEdit.cursorPositionChanged.connect(self.loadContext)
		self.contextView = BPCodeEdit()
		self.contextView.setReadOnly(1)
		
		hBox = QtGui.QHBoxLayout()
		hBox.addWidget(self.codeEdit)
		hBox.addWidget(self.contextView)
		hBox.setStretchFactor(self.codeEdit, 1)
		self.editPanel.setLayout(hBox)
		
		self.setCentralWidget(self.editPanel)
		self.show()
		
	def loadContext(self):
		try:
			cursor = self.codeEdit.textCursor()
			lineNumber = cursor.blockNumber()
			self.statusBar().showMessage("Line %d" % (lineNumber + 1))
			
			# Check that line
			xmlCode = self.codeEdit.converter.getNode(lineNumber).toprettyxml()
			self.contextView.setText(xmlCode)
			#line = cursor.block().text()
		except:
			self.contextView.setText("")
		
	def loadFileToEditor(self, fileName):
		self.file = fileName
		
		# Read
		with codecs.open(self.file, "r", "utf-8") as inStream:
			xmlCode = inStream.read()
		
		# TODO: Remove all BOMs
		if len(xmlCode) and xmlCode[0] == '\ufeff': #codecs.BOM_UTF8:
			xmlCode = xmlCode[1:]
		
		# Remove whitespaces
		# TODO: Ignore bp_strings!
		headerEnd = xmlCode.find("</header>")
		pos = xmlCode.find("\t", headerEnd)
		while pos != -1:
			xmlCode = xmlCode.replace("\t", "")
			pos = xmlCode.find("\t", headerEnd)
			
		pos = xmlCode.find("\n", headerEnd)
		while pos != -1:
			xmlCode = xmlCode.replace("\n", "")
			pos = xmlCode.find("\n", headerEnd)
		
		self.codeEdit.setXML(xmlCode)
		
	def newFile(self):
		self.codeEdit.clear()
		
	def openFile(self, path):
		fileName = path
		if not fileName:
			fileName = QtGui.QFileDialog.getOpenFileName(
				parent=self,
				caption="Open File",
				directory=modDir,
				filter="bp Files (*.bp)")
		
		if fileName:
			self.loadFileToEditor(fileName)
		
	def saveFile(self):
		pass
	
	def saveAsFile(self):
		pass
		
	def runModule(self):
		compiler = BPPostProcessor(self.bpc)
		
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
	app = QtGui.QApplication(sys.argv)
	editor = BPEditor()
	sys.exit(app.exec_())

if __name__ == '__main__':
	try:
		main()
	except SystemExit:
		pass
	except:
		printTraceback()
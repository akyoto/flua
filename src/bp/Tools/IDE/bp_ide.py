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
		
		moduleMenu = menuBar.addMenu("&Module")
		moduleMenu.addAction(runModuleAction)
		
		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(aboutAction)
		
		# Tool bar
		self.toolbar = self.addToolBar("Exit")
		self.toolbar.addAction(newAction)
		self.toolbar.addAction(openAction)
		self.toolbar.addSeparator()
		self.toolbar.addAction(saveAction)
		self.toolbar.addSeparator()
		self.toolbar.addAction(runModuleAction)
		
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
		self.usedFuncsView = BPCodeEdit()
		
		hBox = QtGui.QHBoxLayout()
		hBox.addWidget(self.codeEdit)
		hBox.addWidget(self.usedFuncsView)
		hBox.setStretchFactor(self.codeEdit, 1)
		self.editPanel.setLayout(hBox)
		
		self.setCentralWidget(self.editPanel)
		self.show()
		
	def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
		
	def newFile(self):
		self.textEdit.clear()
		
	def openFile(self, path):
		fileName = path
		if not fileName:
			fileName = QtGui.QFileDialog.getOpenFileName(
				parent=self,
				caption="Open File",
				directory="",
				filter="bp Files (*.bp)")
		
		if fileName:
			self.loadFileToEditor(fileName)
		
	def loadFileToEditor(self, fileName):
		self.file = fileName
		
		# Read
		with codecs.open(self.file, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		# TODO: Remove all BOMs
		if len(codeText) and codeText[0] == '\ufeff': #codecs.BOM_UTF8:
			codeText = codeText[1:]
		
		# Remove whitespaces
		# TODO: Ignore bp_strings!
		headerEnd = codeText.find("</header>")
		pos = codeText.find("\t", headerEnd)
		while pos != -1:
			codeText = codeText.replace("\t", "")
			pos = codeText.find("\t", headerEnd)
			
		pos = codeText.find("\n", headerEnd)
		while pos != -1:
			codeText = codeText.replace("\n", "")
			pos = codeText.find("\n", headerEnd)
		
		self.doc = parseString(codeText.encode( "utf-8" ))
		self.codeEdit.setText(nodeToBPC(self.doc.documentElement).strip())
		
	def saveFile(self):
		pass
	
	def saveAsFile(self):
		pass
		
	def runModule(self):
		bpc = BPCCompiler(modDir)
		compiler = BPPostProcessor(bpc)
		
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
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
from inspect import __date__

####################################################################
# Main
####################################################################
class BPEditor(QtGui.QMainWindow):
	
	def __init__(self):
		super(BPEditor, self).__init__()
		self.initUI()
		
	def initUI(self):
		QtGui.QToolTip.setFont(QtGui.QFont("SansSerif", 10))
		
		self.setGeometry(0, 0, 1000, 650)
		self.setWindowTitle("Blitzprog IDE")
		self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.center()
		
		btn = QtGui.QPushButton("Press me!", self)
		btn.setToolTip("Hey! <br/><b style='color: #ff0000;'>Yo</b> Test")
		btn.move(50, 150)
		btn.clicked.connect(self.close)
		
		self.statusBar().showMessage("Ready")
		
		self.textEdit = QtGui.QTextEdit()
		self.textEdit.setFont(QtGui.QFont("monospace", 10))
		self.textEdit.setTabStopWidth(4 * 8)
		
		hBox = QtGui.QHBoxLayout()
		hBox.addStretch(1)
		hBox.addWidget(self.textEdit)
		
		self.setCentralWidget(self.textEdit)
		self.initMenu()
		self.show()
		
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
			self.textEdit.setText(fileName)
		
	def saveFile(self):
		pass
	
	def saveAsFile(self):
		pass
		
	def runModule(self):
		pass
		
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
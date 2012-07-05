from PyQt4 import QtGui, QtCore
from flua.Compiler.Utils import *
import os

class BPSearchResultsWidget(QtGui.QListWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.searchEdit = self.bpIDE.searchEdit
		self.setWordWrap(True)
		self.setObjectName("SearchResults")
		self.hide()
		
		#self.setContentsMargins(0, 0, 0, 0)
		#self.setMaximumHeight(0)
		#self.setScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		
		#self.keywordIcon = QtGui.QIcon("images/icons/autocomplete/keyword.png")
		self.functionIcon = QtGui.QIcon("images/icons/autocomplete/function.png")
		self.externFuncIcon = QtGui.QIcon("images/icons/autocomplete/extern-function.png")
		self.externVarIcon = QtGui.QIcon("images/icons/autocomplete/extern-variable.png")
		self.classIcon = QtGui.QIcon("images/icons/autocomplete/class.png")
		self.exceptionIcon = QtGui.QIcon("images/icons/autocomplete/exception.png")
		#self.shortcutFunctionIcon = QtGui.QIcon("images/icons/autocomplete/shortcut-function.png")
		
		self.itemClicked.connect(self.goToLineOfItem)
		self.horizontalScrollBar().hide()
		
		self.searchEdit.textChanged.connect(self.startSearch)
		
	def searchIn(self, coll, text, icon):
		for func in coll:
			func = func.replace("_", ".")
			
			if text in func.lower():
				newItem = QtGui.QListWidgetItem(icon, func)
				self.addItem(newItem)
		
	def startSearch(self):
		if self.searchEdit.regExSearch:
			self.clear()
			self.hide()
			return
		
		comp = self.bpIDE.outputCompiler
		text = self.searchEdit.text().lower()
		
		self.clear()
		if not text:
			self.hide()
			return
		
		# Search functions
		if comp:
			#self.searchIn(comp.mainClass.externFunctions, text, self.externFuncIcon)
			#self.searchIn(comp.mainClass.externVariables, text, self.externVarIcon)
			self.searchIn(comp.mainClass.classes, text, self.classIcon)
			self.searchIn(comp.mainClass.functions, text, self.functionIcon)
		
		items = self.count()
		
		# Nothing found
		if not items:
			self.hide()
			return
		
		resultsHeight = 0
		for i in range(items):
			resultsHeight += self.visualItemRect(self.item(i)).height()
		
		resultsWidth = 400
		if resultsHeight > 200:
			resultsHeight = 200
		
		self.setGeometry(self.bpIDE.width() - resultsWidth - 21, self.bpIDE.height() - self.bpIDE.statusBar.height() - resultsHeight - 21, resultsWidth, resultsHeight)
		
		# Show widget
		if items:
			self.show()
		
	def goToLineOfItem(self, item):
		self.bpIDE.jumpTo(item.text())
		self.hide()
		
	def updateView(self):
		pass
				

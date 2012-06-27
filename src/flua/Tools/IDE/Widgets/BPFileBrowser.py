from PyQt4 import QtGui, QtCore
import os

#class BPFileFilter(QtGui.QSortFilterProxyModel):
	
	#def __init__(self, fsModel, fsModelIndex):
		#super().__init__()
		#self.fsModelIndex = fsModelIndex
		#self.setSourceModel(fsModel)
		#self.fsModel = fsModel
		
	##def fetchMore(self, index):
	##	print("fetchMore")
	##	super().fetchMore(index)
	##def hasChildren(self, index):
		
	##def hasChildren(self, index):
	##	if self.canFetchMore(index):
	##		self.fetchMore(index)
	##		return self.rowCount(index) > 0
	##	return True
		##sIndex = self.mapToSource(index)
		##if self.fsModel.canFetchMore(sIndex):
		##	self.fsModel.fetchMore(sIndex)
		##return self.fsModel.hasChildren(sIndex)
		
	#def filterAcceptsRow(self, sourceRow, sourceParent):
		#sModelIndex = self.fsModel.index(sourceRow, 0, sourceParent)
		##print(self.fsModel.fileName(sModelIndex))
		#if self.fsModel.fileName(sModelIndex).endswith(".flua"):
			#return True
		#elif self.fsModel.isDir(sModelIndex):
			##if self.filterAcceptsRow(sourceRow + 1, sModelIndex.child(0, 0)):
			##	return True
			##return self.#self.hasChildren(self.mapFromSource(sModelIndex))#self.hasChildren(sourceParent)
			#return True
		
		#return False

class BPFileBrowser(QtGui.QTreeView):
	
	def __init__(self, parent, rootPath):
		super().__init__(parent)
		self.bpIDE = parent
		self.fsModel = QtGui.QFileSystemModel()
		#self.fsModel.setNameFilters(["*.flua"])
		fsModelIndex = self.fsModel.setRootPath(rootPath)
		
		#self.proxyModel = BPFileFilter(self.fsModel, fsModelIndex)
		#self.proxyModel.setFilterWildcard("b*")
		#self.proxyModel.setFilterRegExp(QtCore.QRegExp('^bp$', QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString))
		#self.proxyModel.setFilterKeyColumn(0)
		
		#
		#self.viewPath("/home/")#rootPath)
		#self.setModel(self.proxyModel)
		#self.setModel(self.proxyModel)
		self.setModel(self.fsModel)
		self.setRootIndex(fsModelIndex)#self.proxyModel.mapFromSource(fsModelIndex))
		
		self.setHeaderHidden(True)
		self.setColumnHidden(1, True)
		self.setColumnHidden(2, True)
		self.setColumnHidden(3, True)
		#self.icon = QtGui.QIcon("images/tango/status/dialog-warning.svg")
		#self.itemClicked.connect(self.goToLineOfItem)
		
		self.doubleClicked.connect(self.onItemClick)
		
	def onItemClick(self, item):
		filePath = self.fsModel.filePath(item)
		if os.path.isfile(filePath):
			self.bpIDE.openFile(filePath)
		
	#def viewPath(self, path):
	#	pass
		
	def updateView(self):
		pass

from PyQt4 import QtGui, QtCore
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
import os
import sys

class BPModuleViewModel(QtGui.QStandardItemModel):
	
	def __init__(self, parent = None):
		super().__init__()

class BPModuleItem(QtGui.QStandardItem):
	
	def __init__(self, name):
		super().__init__(name)
		self.path = ""
		self.realPath = ""
		self.name = name
		self.subModules = dict()
		self.setEditable(False)
		self.isModule = False
		self.setData(self, QtCore.Qt.UserRole + 1)
		#self.setData(self.icon, QtCore.Qt.DecorationRole)
		
	def setModPath(self, path):
		self.path = path
		self.realPath = getModulePath(self.path)

class BPModuleBrowser(QtGui.QTreeView, Benchmarkable):
	
	def __init__(self, parent, modDir):
		super().__init__(parent)
		self.bpIDE = parent
		self.bpcModel = None
		self.modDir = modDir
		self.modDirLen = len(self.modDir)
		self.setExpandsOnDoubleClick(False)
		self.setAnimated(True)
		
		self.brushSimpleFolder = QtGui.QBrush(QtGui.QColor("#adadad"))
		self.brushModule = QtGui.QBrush(QtGui.QColor("#272727"))
		
		self.doubleClicked.connect(self.onItemClick)
		self.setHeaderHidden(True)
		
		self.bpcModel = BPModuleViewModel()
		self.setModel(self.bpcModel)
		
		self.reloadModuleDirectory()
		#self.reloadModuleDirectory()
		#self.reloadModuleDirectory()
		
		self.expandToDepth(0)
		
	def reloadModuleDirectory(self):
		if self.bpcModel:
			self.bpcModel.removeRows(0, self.bpcModel.rowCount())
		
		self.modules = BPModuleItem("root")
		
		self.startBenchmark("Load module directory")
		for root, subFolders, files in os.walk(self.modDir):
			if fixPath(root) == self.bpIDE.tmpPath:
				continue
			
			for file in files:
				if file.endswith(".bp"):
					lastDir = fixPath(root).split("/")[-2]
					modName = file[:-3]
					if modName == lastDir:
						mod = extractDir(root[self.modDirLen:]).replace("/", ".")[:-1]
					else:
						mod = extractDir(root[self.modDirLen:]).replace("/", ".") + modName
					mod = fixPath(root[self.modDirLen:]).replace("/", ".") + "." + file[:-3]
					
					parts = mod.split(".")
					
					modulesRoot = self.modules
					for part in parts:
						if not part in modulesRoot.subModules:
							modulesRoot.subModules[part] = BPModuleItem(part)
						modulesRoot = modulesRoot.subModules[part]
		self.endBenchmark()
		#print(self.modules.subModules["bp"].subModules)
		#if self.bpcModel and self.bpcModel.hasChildren():
		#	self.bpcModel.removeRows(1, self.bpcModel.rowCount())
		#self.setModel(None)
		self.buildTree()
		
	def onItemClick(self, item):
		modItem = item.data(QtCore.Qt.UserRole + 1)
		realPath = modItem.realPath
		if realPath:
			self.bpIDE.openFile(realPath)
		else:
			# TODO: Go down until we meet a module
			if not self.isExpanded(item):
				self.expandUntilModuleFound(item, modItem)
			else:
				self.setExpanded(item, False)
		
	def expandUntilModuleFound(self, fromIndex, fromItem):
		if not fromItem.isModule:
			childrenCount = fromItem.rowCount()
			for i in range(childrenCount):
				childIndex = fromIndex.child(i, 0)
				childItem = childIndex.data(QtCore.Qt.UserRole + 1)
				if childItem.isModule:
					break
				else:
					self.expandUntilModuleFound(childIndex, childItem)
		self.setExpanded(fromIndex, True)
		
	def buildTree(self):
		for namespace, mod in sorted(self.modules.subModules.items()):
			self.buildTreeRec(mod, self.bpcModel.invisibleRootItem(), "")
		
	def buildTreeRec(self, mod, parent, parentPath):
		if parentPath:
			mod.setModPath(parentPath + "." + mod.name)
		else:
			mod.setModPath(mod.name)
		
		mod.setForeground(self.brushSimpleFolder)
		
		for namespace, subMod in sorted(mod.subModules.items()):
			self.buildTreeRec(subMod, mod, mod.path)
		
		parentItem = parent.data()
		if parentItem and parentItem.name == mod.name:
			#parent.setIcon(QtGui.QIcon("images/icons/mimetypes/package-x-generic.png"))
			parent.isModule = True
			parent.setForeground(self.brushModule)
			return
		
		if not mod.hasChildren():
			mod.isModule = True
			mod.setForeground(self.brushModule)
		
		parent.appendRow(mod)
		
	def updateView(self):
		pass

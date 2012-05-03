from PyQt4 import QtGui, QtCore
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
import os
import sys

class BPModuleViewModel(QtGui.QStandardItemModel):
	
	def __init__(self):
		super().__init__()

class BPModuleItem(QtGui.QStandardItem):
	
	def __init__(self, name):
		super().__init__(name)
		self.path = ""
		self.realPath = ""
		self.name = name
		self.subModules = dict()
		self.setEditable(False)
		self.setData(self, QtCore.Qt.UserRole + 1)
		
	def setModPath(self, path):
		self.path = path
		self.realPath = getModulePath(self.path)

class BPModuleBrowser(QtGui.QTreeView, Benchmarkable):
	
	def __init__(self, parent, modDir):
		super().__init__(parent)
		self.bpIDE = parent
		self.modules = BPModuleItem("root")	# The actual module "list"
		self.modDir = modDir
		self.modDirLen = len(self.modDir)
		self.model = BPModuleViewModel()
		self.setExpandsOnDoubleClick(False)
		self.setAnimated(True)
		
		self.doubleClicked.connect(self.onItemClick)
		self.setHeaderHidden(True)
		
		self.startBenchmark("Load module directory")
		for root, subFolders, files in os.walk(modDir):
			for file in files:
				if file.endswith(".bp"):
					lastDir = fixPath(root).split("/")[-2]
					modName = file[:-3]
					if modName == lastDir:
						mod = fixPath(root[self.modDirLen:]).replace("/", ".")[:-1]
					else:
						mod = fixPath(root[self.modDirLen:]).replace("/", ".") + modName
					mod = fixPath(root[self.modDirLen:]).replace("/", ".") + file[:-3]
					
					parts = mod.split(".")
					
					modulesRoot = self.modules
					for part in parts:
						if not part in modulesRoot.subModules:
							modulesRoot.subModules[part] = BPModuleItem(part)
						modulesRoot = modulesRoot.subModules[part]
		self.endBenchmark()
		
		self.buildTree()
		self.setModel(self.model)
		self.expandToDepth(0)
		
	def onItemClick(self, item):
		modItem = item.data(QtCore.Qt.UserRole + 1)
		realPath = modItem.realPath
		if realPath:
			self.bpIDE.openFile(realPath)
		else:
			self.setExpanded(item, 1 - self.isExpanded(item))
		
	def buildTree(self):
		for namespace, mod in sorted(self.modules.subModules.items()):
			self.buildTreeRec(mod, self.model.invisibleRootItem(), "")
		
	def buildTreeRec(self, mod, parent, parentPath):
		if parentPath:
			mod.setModPath(parentPath + "." + mod.name)
		else:
			mod.setModPath(mod.name)
		
		for namespace, subMod in sorted(mod.subModules.items()):
			self.buildTreeRec(subMod, mod, mod.path)
		
		parentItem = parent.data()
		if parentItem and parentItem.name == mod.name:
			return
		parent.appendRow(mod)
		
	def updateView(self):
		pass

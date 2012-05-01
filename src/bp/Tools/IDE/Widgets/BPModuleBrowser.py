from PyQt4 import QtGui, QtCore
from bp.Compiler.Utils import *
import os
import sys

class BPModuleViewModel(QtGui.QStandardItemModel):
	
	def __init__(self):
		super().__init__()

class BPModuleItem(QtGui.QStandardItem):
	
	def __init__(self, name):
		super().__init__(name)
		self.name = name
		self.subModules = dict()

class BPModuleBrowser(QtGui.QTreeView, Benchmarkable):
	
	def __init__(self, parent, modDir):
		super().__init__(parent)
		self.bpIDE = parent
		self.modules = BPModuleItem("root")	# The actual module "list"
		self.modDir = modDir
		self.modDirLen = len(self.modDir)
		self.model = BPModuleViewModel()
		self.setHeaderHidden(True)
		
		self.startBenchmark("Module directory")
		for root, subFolders, files in os.walk(modDir):
			for file in files:
				if file.endswith(".bp"):
					if 1:
						mod = fixPath(root[self.modDirLen:]).replace("/", ".") + file[:-3]
						parts = mod.split(".")
						
						modulesRoot = self.modules
						for part in parts:
							if not part in modulesRoot.subModules:
								modulesRoot.subModules[part] = BPModuleItem(part)
							modulesRoot = modulesRoot.subModules[part]
					else:
						# ListView implementation
						lastDir = fixPath(root).split("/")[-2]
						modName = file[:-3]
						if modName == lastDir:
							mod = fixPath(root[self.modDirLen:]).replace("/", ".")[:-1]
						else:
							mod = fixPath(root[self.modDirLen:]).replace("/", ".") + modName
						print(mod)
		self.endBenchmark()
		
		self.buildTree()	
		self.setModel(self.model)
		
	def buildTree(self):
		for namespace, mod in self.modules.subModules.items():
			self.buildTreeRec(mod, self.model.invisibleRootItem())
		
	def buildTreeRec(self, mod, parent):
		for namespace, subMod in mod.subModules.items():
			self.buildTreeRec(subMod, mod)
		parent.appendRow(mod)
		
	def updateView(self):
		pass

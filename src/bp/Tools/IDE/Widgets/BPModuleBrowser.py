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
		#self.setAnimated(True)
		self.oldImportedMods = []
		self.oldImportedModsLen = 0
		self.setHeaderHidden(True)
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		
		self.brushSimpleFolder = self.bpIDE.config.theme['module-browser-directory']
		self.brushModule = self.bpIDE.config.theme['module-browser-module']
		
		self.doubleClicked.connect(self.onItemClick)
		self.customContextMenuRequested.connect(self.showContextMenu)
		
		self.bpcModel = BPModuleViewModel()
		self.setModel(self.bpcModel)
		
		self.reloadModuleDirectory(True)
		
	def reloadModuleDirectory(self, expand = True):
		if self.bpcModel:
			self.bpcModel.removeRows(0, self.bpcModel.rowCount())
		
		self.modules = BPModuleItem("root")
		
		self.startBenchmark("Load module directory")
		for root, subFolders, files in os.walk(self.modDir):
			if fixPath(root) == self.bpIDE.tmpPath:
				continue
			
			for file in files:
				if file.endswith(".bp"):
					lastDir = fixPath(root).split(OS_SLASH)[-2]
					modName = file[:-3]
					if modName == lastDir:
						mod = extractDir(root[self.modDirLen:]).replace(OS_SLASH, ".")[:-1]
					else:
						mod = extractDir(root[self.modDirLen:]).replace(OS_SLASH, ".") + modName
					mod = fixPath(root[self.modDirLen:]).replace(OS_SLASH, ".") + "." + file[:-3]
					
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
		
		if expand:
			self.expandToDepth(0)
		
	def onItemClick(self, item):
		# Ugly on Windows 7
		if os.name == "nt":
			self.clearSelection()
		
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
		
	def forEachModItemDo(self, parent, func):
		for child in parent.subModules.values():
			self.forEachModItemDo(child, func)
		func(parent)
		
	def resetHighlight(self, modItem):
		modItem.setFont(self.bpIDE.config.standardFont)
		
		if modItem.isModule:
			modItem.setForeground(self.brushModule)
		else:
			modItem.setForeground(self.brushSimpleFolder)
		
	# Clear all highlights
	def resetAllHighlights(self):
		self.forEachModItemDo(self.modules, self.resetHighlight)
		
		# Reset to enable rehighlighting on a file reload
		self.oldImportedMods = []
		self.oldImportedModsLen = 0
		
	def showContextMenu(self, pos):
		print("Context menu not implemented!")
		
	def updateView(self):
		# Show imports
		if self.bpIDE.codeEdit is not None:
			importedMods = self.bpIDE.codeEdit.getImportedModulesByCode()
		else:
			importedMods = []
		
		# Compare it with the old import list and if it's different -> highlight
		#index = 0
		#for modName in importedMods:
		#	if index < self.oldImportedModsLen and modName != self.oldImportedMods[index]:
		#		modItem = self.getModuleItemByName(self.oldImportedMods[index])
		#		if modItem:
		#			self.resetHighlight(modItem)
		#	
		#	if index >= self.oldImportedModsLen or modName != self.oldImportedMods[index]:
		#		self.highlightModule(modName)
		#	index += 1
		
		# Old modules got deleted -> reset highlight
		#for rest in range(index, self.oldImportedModsLen):
		#	modItem = self.getModuleItemByName(self.oldImportedMods[rest])
		#	if modItem:
		#		print("RESET FOR %s" % modItem.name)
		#		self.resetHighlight(modItem)
		
		# TODO: Fix the old commented, but better implementation
		#print("OLD: " + str(self.oldImportedMods))
		for modName in self.oldImportedMods:
			modItem = self.getModuleItemByName(modName)
			if modItem:
				#print("RESET FOR " + modName + "/" + modItem.name)
				self.resetHighlight(modItem)
		
		# Modified by the coming for loop
		self.oldImportedMods = []
		self.oldImportedModsLen = 0
		
		for modName in importedMods:
			self.highlightModule(modName)
		
		#if not self.bpIDE.codeEdit.root:
		#	return
		#
		#header = getElementByTagName(self.bpIDE.codeEdit.root, "header")
		#if not header:
		#	return
		#
		#deps = getElementByTagName(header, "dependencies")
		#if not deps:
		#	return
		
		# Look at <dependencies> and highlight them
		#for child in deps.childNodes:
		#	modName = child.childNodes[0].nodeValue.strip()
		#	self.highlightModule(modName)
	
	def highlightModule(self, modName):
		importType = self.bpIDE.getModuleImportType(modName)
		
		# Local import
		if importType == 1 or importType == 2:
			style = self.bpIDE.getCurrentTheme()['local-module-import']
		elif importType == 3 or importType == 4:
			style = self.bpIDE.getCurrentTheme()['project-module-import']
		else:#if importType == 5 or importType == 6:
			style = self.bpIDE.getCurrentTheme()['global-module-import']
		
		# Local + project import
		if importType >=1 and importType <= 4:
			filePath = stripExt(self.bpIDE.getModulePath(modName))
			modPath = filePath[len(getModuleDir()):].replace(OS_SLASH, ".")
			parts = modPath.split(".")
			if len(parts) > 1 and parts[-1] == parts[-2]:
				modPath = ".".join(parts[:-1])
		# Global module import
		else:
			modPath = modName
		
		item = self.getModuleItemByName(modPath, expand = True)
		if item:
			#item.setFont(style.font())
			item.setForeground(style.foreground())
			
		self.oldImportedMods.append(modPath)
		self.oldImportedModsLen += 1
		
	def getModuleItemByName(self, modName, expand = False):
		importType = self.bpIDE.getModuleImportType(modName)
		if importType == 1 or importType == 2:
			localToGlobal = self.bpIDE.localToGlobalImport(modName)
			parts = localToGlobal.split(".")
		else:
			parts = modName.split(".")
		
		if len(parts) >= 2 and parts[-1] == parts[-2]:
			parts = parts[:-1]
		
		currentModule = self.modules
		lastPart = len(parts)
		currentPart = 0
		while currentPart < lastPart:
			subMod = parts[currentPart]
			
			if subMod in currentModule.subModules:
				currentModule = currentModule.subModules[subMod]
			else:
				break
			
			if expand and currentPart != lastPart - 1:
				if currentPart < 3 or 1:
					self.setExpanded(currentModule.index(), True)
			currentPart += 1
		
		if currentModule == self.modules:
			return None
		
		return currentModule

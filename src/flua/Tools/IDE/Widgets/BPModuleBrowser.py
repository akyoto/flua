from PyQt4 import QtGui, QtCore
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Tools.IDE.Utils import *
import os
import sys
import shutil

# New origin:
# git remote set-url --push origin <newurl>

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
		self.setEditable(True)
		self.isModule = False
		self.selectedModItem = None
		self.setData(self, QtCore.Qt.UserRole + 1)
		#self.setData(self.icon, QtCore.Qt.DecorationRole)
		
	def addSubModule(self, name):
		if not self.subModules:
			self.realPath = stripExt(self.realPath) + "/" + stripAll(self.realPath) + ".flua"
		
		mod = BPModuleItem(name)
		mod.setModPath(self.path + "." + name)
		mod.isModule = True
		self.subModules[name] = mod
		self.appendRow(mod)
		self.sortChildren(0)
		
	def setModPath(self, path):
		self.path = path
		self.realPath = getModulePath(self.path)
		
		# Top level modules
		#if not self.realPath:
		
class BPModuleBrowser(QtGui.QTreeView, Benchmarkable):
	
	def __init__(self, parent, environment):
		super().__init__(parent)
		Benchmarkable.__init__(self)
		
		self.bpIDE = parent
		self.environment = environment
		self.bpcModel = None
		self.modules = None
		self.modCount = 0
		self.setExpandsOnDoubleClick(False)
		#self.setAnimated(True)
		self.oldImportedMods = []
		self.oldImportedModsLen = 0
		self.setHeaderHidden(True)
		self.setEditTriggers(QtGui.QAbstractItemView.EditKeyPressed)
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		
		self.brushSimpleFolder = self.bpIDE.config.theme['module-browser-directory']
		self.brushModule = self.bpIDE.config.theme['module-browser-module']
		
		self.doubleClicked.connect(self.onItemClick)
		self.customContextMenuRequested.connect(self.showContextMenu)
		
		# Actions
		self.modNewAction = QtGui.QAction(
			QtGui.QIcon(getIDERoot() + "images/icons/modules/module_add.png"),
			"New module",
			self)
		self.modNewAction.triggered.connect(self.newModule)
		
		#self.modRenameAction = QtGui.QAction(
		#	QtGui.QIcon(getIDERoot() + "images/icons/modules/module_rename.png"),
		#	"Rename module",
		#	self)
		#self.modRenameAction.triggered.connect(self.renameModule)
		
		self.modDeleteAction = QtGui.QAction(
			QtGui.QIcon(getIDERoot() + "images/icons/modules/module_delete.png"),
			"Delete module",
			self)
		self.modDeleteAction.triggered.connect(self.deleteModule)
		
		self.repoNewAction = QtGui.QAction(
			QtGui.QIcon(getIDERoot() + "images/icons/mimetypes/package-x-generic.png"),
			"New repository",
			self)
		self.repoNewAction.triggered.connect(self.newRepository)
		
		# Model
		self.bpcModel = BPModuleViewModel()
		self.setModel(self.bpcModel)
		
		#self.reloadModuleDirectory(expand = True)
		
	# On renaming
	def commitData(self, editor):
		item = self.currentIndex().data(QtCore.Qt.UserRole + 1)
		newName = editor.text()
		
		# Name changed?
		if item.name == newName and len(newName) >= 1:
			return
		
		isDirOnly = False
		
		realPath = item.realPath
		if not realPath:
			realPath = fixPath(getModuleDir() + item.path.replace(".", "/"))
			if realPath.endswith("/"):
				realPath = realPath[:-1]
			isDirOnly = True
		
		parts = realPath.split("/")
		
		sharesName = False
		if item.isModule:
			if len(parts) >= 2 and parts[-2] == stripExt(parts[-1]):
				sharesName = True
				parts[-2] = newName
			
			parts[-1] = newName + self.environment.standardFileExtension
		else:
			if parts:
				parts[-1] = newName
		
		newPath = "/".join(parts)
		
		#if isDirOnly:
		#	realDir = extractDir(realPath + "/")
		#else:
		#	realDir = extractDir(realPath)
		
		if sharesName:
			#print(realPath)
			#print(newPath)
			shutil.copytree(os.path.dirname(realPath), os.path.dirname(newPath))
			shutil.move(os.path.dirname(newPath) + "/" + stripDir(realPath), newPath)
			shutil.rmtree(os.path.dirname(realPath))
		else:
			if isDirOnly:
				try:
					os.makedirs(os.path.dirname(newPath))
				except OSError:
					pass
			
			shutil.move(realPath, newPath)
		
		# Update data
		item.name = newName
		item.realPath = newPath
		
		pathParts = item.path.split(".")
		if pathParts:
			pathParts[-1] = newName
		item.path = ".".join(pathParts)
		
		# We need to update children's paths
		if sharesName or isDirOnly:
			self.reloadModuleDirectory()
		
		super().commitData(editor)
		
	def sizeHint(self):
		return QtCore.QSize(280, -1)
		
	# Context menu
	def showContextMenu(self, pos):
		self.selectedModItem = self.indexAt(pos).data(QtCore.Qt.UserRole + 1)
		
		if self.selectedModItem:
			menu = QtGui.QMenu(self)
			menu.addAction(self.modNewAction)
			#menu.addAction(self.modRenameAction)
			menu.addAction(self.modDeleteAction)
			menu.exec(QtGui.QCursor.pos())
		else:
			# TODO: Other menu
			menu = QtGui.QMenu(self)
			menu.addAction(self.repoNewAction)
			menu.exec(QtGui.QCursor.pos())
		
	# Create new repository
	def newRepository(self, ignored):
		name = self.bpIDE.askText(
			"Please enter the name of your repository:",
			"""The name can <b>only contain lowercase letters</b>, think of it as a <b>tag</b> and use a short name. <br/>
			This is the name which will appear in the global repository list if you decide to publish it.""",
			title = "New repository"
		)
		
		if name:
			name = normalizeTopLevelModName(name.strip())
			path = getModuleDir() + name + "/"
			
			if not os.path.exists(path):
				os.makedirs(path)
			
			shutil.copyfile(getIDERoot() + "Templates/Empty" + self.environment.standardFileExtension, path + "Empty" + self.environment.standardFileExtension)
			self.reloadModuleDirectory(expand = False)
		
	# New module
	def newModule(self, ignored):
		item = self.selectedModItem
		if not item:
			return
		
		name = self.bpIDE.askText(
			"New module name:",
			"This module will be created as a submodule of <b>%s</b>" % item.path,
			title = "New module"
		)
		
		if not name:
			return
		
		realPath = fixPath(item.realPath)
		if not realPath:
			realPath = fixPath(getModuleDir() + item.path.replace(".", "/"))
		
		if item.isModule:
			# Move it to the new directory
			if os.path.isfile(realPath) and extractDir(realPath).split("/")[-2] != stripAll(realPath):
				newPath = stripExt(realPath) + "/"
				os.makedirs(newPath)
				shutil.copy(realPath, newPath)
				os.unlink(item.realPath)
			else:
				newPath = extractDir(realPath)
		else:
			newPath = realPath
		
		#if not newPath:
		#	newPath = getModuleDir() + item.name
		
		if not newPath.endswith("/"):
			newPath += "/"
		
		#print("Start:")
		#print(item.realPath)
		#print(realPath)
		#print(newPath)
		#print(name)
		
		copyFrom = getIDERoot() + "Templates/Empty" + self.environment.standardFileExtension
		copyTo = newPath + name + self.environment.standardFileExtension
		
		#print(copyFrom)
		#print(copyTo)
		
		shutil.copyfile(copyFrom, copyTo)
		
		item.addSubModule(name)
		
	# Module renaming
	def renameModule(self, ignored):
		# TODO: ...
		item = self.selectedModItem
		item.setEditable(True)
		
	# Module deletion
	def deleteModule(self, ignored):
		item = self.selectedModItem
		deleted = False
		
		if item:
			# Just to be safe.
			if item.realPath == getModuleDir():
				return
			
			if item.isModule and item.subModules:
				if self.bpIDE.ask("Are you sure you want to delete <b>%s</b> and all of its submodules?" % item.path, title = "Delete module"):
					if os.path.dirname(item.realPath).split("/")[-1] == item.name:
						shutil.rmtree(extractDir(item.realPath))
					else:
						shutil.rmtree(item.realPath)
					if item.parent():
						item.parent().subModules.pop(item.name)
						item.parent().removeRow(item.row())
					deleted = True
			elif item.isModule:
				if self.bpIDE.ask("Are you sure you want to delete the module <b>%s</b>?" % item.path, title = "Delete module"):
					os.unlink(item.realPath)
					if item.parent():
						item.parent().subModules.pop(item.name)
						item.parent().removeRow(item.row())
					deleted = True
			else:
				if self.bpIDE.ask("Are you sure you want to delete all modules inside <b>%s</b>?" % item.path, title = "Delete module"):
					shutil.rmtree(getModuleDir() + item.path)
					if item.parent():
						item.parent().subModules.pop(item.name)
						item.parent().removeRow(item.row())
					deleted = True
		
		# Top level module
		if deleted and item and not "." in item.path:
			self.reloadModuleDirectory(expand = False)
		#self.reloadModuleDirectory()
		
		self.selectedModItem = None
		
	# Reload all directories
	def reloadModuleDirectory(self, rootItem = None, expand = True):
		expandedList = []
		
		# Delete all existing rows 
		if self.bpcModel:
			# Save expanded state
			indices = self.bpcModel.persistentIndexList()
			
			for index in indices:
				expandedList.append((index.data(QtCore.Qt.UserRole + 1).path, self.isExpanded(index)))
			
			# The actual deletion
			self.bpcModel.removeRows(0, self.bpcModel.rowCount())
		
		self.modules = BPModuleItem("root")
		
		if not self.environment.rootDir:
			return
		
		self.modules.realPath = self.bpIDE.environment.rootDir
		
		fileExtensions = self.environment.fileExtensions
		
		rootPath = extractDir(self.modules.realPath)
		rootLen = len(rootPath)
		self.modCount = 0
		
		ideRoot = getIDERoot()
		
		self.startBenchmark("Init module directory")
		for root, subFolders, files in os.walk(rootPath):
			# Fix path
			rootFixed = root.replace(OS_WRONG_SLASH, OS_SLASH)
			if not rootFixed.endswith("/"):
				rootFixed += "/"
			
			# Filter Python cache directories
			if rootFixed.endswith("__pycache__/"):
				continue
			
			# Filter hidden git directories
			if ".git" in rootFixed:
				continue
			
			# Filter IDE root directory
			if ideRoot in rootFixed:
				continue
				
			# Filter C++ output directories
			if rootFixed.endswith("C++/"):
				continue
			
			# Filter Python 3 output directories
			if rootFixed.endswith("Python3/"):
				continue
			
			# Find all modules
			for file in files:
				fileExt = extractExt(file)
				
				if not fileExt in fileExtensions:
					continue
				
				extLen = len(fileExt)
				
				# If there is a directory with the same name, delete the file
				if self.environment == self.bpIDE.fluaEnvironment:
					if os.path.isdir(fixPath(root) + "/" + stripExt(file)):
						try:
							os.unlink(fixPath(root) + "/" + file)
						except OSError:
							pass
						
						continue
				
				lastDir = fixPath(root).split(OS_SLASH)[-2]
				modName = file[:-extLen]
				if modName == lastDir:
					mod = extractDir(root[rootLen:]).replace(OS_SLASH, ".")[:-1]
				else:
					mod = extractDir(root[rootLen:]).replace(OS_SLASH, ".") + modName
				mod = fixPath(root[rootLen:]).replace(OS_SLASH, ".") + "." + file[:-extLen]
				
				parts = mod.split(".")
				
				modulesRoot = self.modules
				for part in parts:
					if not part in modulesRoot.subModules:
						modulesRoot.subModules[part] = BPModuleItem(part)
					modulesRoot = modulesRoot.subModules[part]
				
				self.modCount += 1
					
		self.endBenchmark()
		#print(self.modules.subModules["bp"].subModules)
		#if self.bpcModel and self.bpcModel.hasChildren():
		#	self.bpcModel.removeRows(1, self.bpcModel.rowCount())
		#self.setModel(None)
		
		# Build the module tree
		self.buildTree(rootItem)
		
		if expandedList:
			for modPath, state in expandedList:
				item = self.getModuleItemByName(modPath)
				if item:
					self.setExpanded(item.index(), state)
		elif expand:
			self.expandToDepth(0)
		
	def onItemClick(self, item):
		# Ugly
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
		
	def buildTree(self, rootItem = None):
		if rootItem:
			for namespace, mod in sorted(rootItem.subModules.items()):
				self.buildTreeRec(mod, rootItem, rootItem.path)
		else:
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
		
		#mod.setIcon(QtGui.QIcon("images/icons/autocomplete/function.png"))
		
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
		self.brushSimpleFolder = self.bpIDE.config.theme['module-browser-directory']
		self.brushModule = self.bpIDE.config.theme['module-browser-module']
		
		if self.modules:
			self.forEachModItemDo(self.modules, self.resetHighlight)
		
		# Reset to enable rehighlighting on a file reload
		self.oldImportedMods = []
		self.oldImportedModsLen = 0
		
	def updateView(self):
		# Ugly
		self.clearSelection()
		
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
	
	def highlightModPath(self, modPath, style, addToOldImportedMods = True):
		item = self.getModuleItemByName(modPath, expand = True)
		
		if item:
			#item.setFont(style.font())
			item.setForeground(style.foreground())
			
		if addToOldImportedMods:
			self.oldImportedMods.append(modPath)
			self.oldImportedModsLen += 1
	
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
			filePath = self.bpIDE.getModulePath(modName)
			modPath = self.translateFileToModPath(filePath)
		# Global module import
		else:
			modPath = modName
		
		self.highlightModPath(modPath, style)
		
	def highlightFile(self, filePath, style, addToOldImportedMods = False):
		self.highlightModPath(self.translateFileToModPath(filePath), style, addToOldImportedMods)
		
	def translateFileToModPath(self, filePath):
		filePath = stripExt(filePath)
		modPath = filePath[len(getModuleDir()):].replace(OS_SLASH, ".")
		parts = modPath.split(".")
		
		if len(parts) > 1 and parts[-1] == parts[-2]:
			modPath = ".".join(parts[:-1])
		
		return modPath
		
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

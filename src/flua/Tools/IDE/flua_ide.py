﻿####################################################################
# Header
####################################################################
# Flua IDE
# 
# Website: flua-lang.org
# Started: 26.04.2012 (Thu, Apr 26 2012)

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
# 
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import sys
import os
from PyQt4 import QtGui, QtCore, QtNetwork, uic
from flua.Compiler import *
from flua.Tools.IDE.Startup import *
from flua.Tools.IDE.Syntax import *

####################################################################
# Code
####################################################################
class BPMainWindow(QtGui.QMainWindow, MenuActions, Startup, Benchmarkable):
	
	def __init__(self, multiThreaded = True):
		super().__init__()
		Benchmarkable.__init__(self)
		
		# Before showing
		self.geometryState = None
		
		# Print this first to identify wrong paths
		print("Module directory: " + getModuleDir())
		print("---")
		
		# Useless stuff
		QtCore.QCoreApplication.setOrganizationName("Flua")
		QtCore.QCoreApplication.setOrganizationDomain("flua-lang.org")
		QtCore.QCoreApplication.setApplicationName("Flua Studio")
		
		# For some weird reason you need to SHOW FIRST, THEN APPLY THE THEME
		if os.name == "nt":
			self.show()
		
		# Init
		self.threaded = multiThreaded
		
		self.environment = None
		self.tmpCount = 0
		self.lastBlockPos = -1
		self.lastFunctionCount = -1
		self.intelliEnabled = False
		self.viewsInitialized = False
		self.docks = []
		self.dockMenuActions = []
		self.uiCache = dict()
		self.config = None
		self.gitThread = None
		self.authorName = ""
		self.previousScopes = None
		self.lastCodeEdit = None
		self.outputCompiler = None
		self.lastShownNode = None
		self.lastShownOutputCompiler = None
		self.currentNode = None
		self.runThread = None
		self.somethingModified = True
		self.codeEditLastRun = None
		self.loadingFinished = False
		self.running = 0
		self.compiling = 0
		self.backgroundCompileIsUpToDate = False
		self.lastRunOptions = []
		self.dockShortcuts = ["A", "S", "D", "F", "Y", "X", "C", "V", "G", "B"]	# TODO: Internationalization
		self.activeRepositoryIcon = QtGui.QIcon("images/icons/repo-browser/repository.png")
		self.inactiveRepositoryIcon = QtGui.QIcon("images/icons/repo-browser/repository-inactive.png")
		#self.networkMgr = QtNetwork.QNetworkAccessManager(self)
		
		# AC
		#self.shortCuts = dict()
		self.funcsDict = dict()
		self.classesDict = dict()
		
		# Tmp path
		self.tmpPath = fixPath(os.path.abspath("./tmp/"))
		if self.tmpPath[-1] != "/":
			self.tmpPath += "/"
		
		# TODO: Keymap
		self.ctrlPressed = False
		
		# Load config
		self.startBenchmark("Load Configuration")
		self.loadConfig()
		self.endBenchmark()
		
		# Completer
		self.completer = BPCAutoCompleter(self)
		self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
		
		if os.name != "nt":
			self.showMaximized()
		
		# The beginning of the end.
		self.initAll()
		
		# Timed
		self.startTime = time.time()
		
		self.bindFunctionToTimer(self.showDependencies, 150)
		self.bindFunctionToTimer(self.onCompileTimeout, self.config.compilerUpdateInterval)
		#self.bindFunctionToTimer(self.onProcessEvents, 5)
		
		# Apply settings
		self.setCentralWidget(self.workspacesContainer)
		
		self.initDocks()
		
		self.config.applySettings()
		
		# We love hard coding! ... or maybe not.
		#self.moduleView.highlightModule("playground.My playground")
		
		# Loading finished
		self.loadingFinished = True
		
		# Intercept sys.stdout and sys.stderr
		self.console.watch(self.console.log)
		
		# Set default environment
		environmentNames = {
			"Flua" : self.fluaEnvironment
		}
		
		if self.config.defaultEnvironmentName in environmentNames:
			self.setEnvironment(environmentNames[self.config.defaultEnvironmentName])
		
		# Load session
		self.loadSession()
		
		# Loading finished
		self.onLoadingFinished()
		
		#if 1:
			#self.newFile()
		#	
		#else:
		#	self.newFile()
#			self.codeEdit.setPlainText("""import playground.Everything
#
## Check flua.Documentation in the module browser on the left for some beginner topics.
#""")
			#cursor = self.codeEdit.textCursor()
			#cursor.movePosition(QtGui.QTextCursor.End)
			#self.codeEdit.setTextCursor(cursor)
			
			#self.firstStartUpdateTimer = self.bindFunctionToTimer(self.onProgressUpdate, 10)
		
		# Show maximized now
		if os.name == "nt":
			self.showMaximized()
		
	#def eventFilter(self, obj, event):
	#	
	#	for i in range(len(self.docks)):
	#		if obj == self.docks[i:
	#			return False
	#			if event.type == QtCore.QEvent.Close:
	#				action = self.dockMenuActions[i]
	#				action.blockSignals(True)
	#				action.setChecked(False)
	#				action.blockSignals(False)
	#				return True
	#			return False
	#	
	#	return super().eventFilter(obj, event)
		
	def sendToRunningProgram(self, data):
		self.runThread.sendData(data)
		
	def setEnvironment(self, env):
		if env == None:
			return
			#env = self.baseEnvironment
			
		if self.codeEdit:
			self.codeEdit.setEnvironment(env)
			self.currentWorkspace.updateIsTextFile()
			
		if env == self.environment:
			return
		
		if self.loadingFinished:
			print("Switching environment to %s" % env.name)
		
		# Unload the old environment
		if self.environment:
			self.environment.action.setChecked(False)
		
		# Set the new environment
		self.environment = env
		
		# Load the new environment
		self.environment.action.setChecked(True)
		
		if self.loadingFinished:
			self.moduleView.hide()
			self.moduleView = self.environment.moduleView
			
			self.moduleViewDock.setWidget(self.moduleView)
			self.moduleViewDock.setObjectName("Modules")
			
			if self.environment != self.baseEnvironment and self.moduleView.modCount == 0:
				if self.environment == self.fluaEnvironment:
					self.moduleView.reloadModuleDirectory(expand = True)
				else:
					self.moduleView.reloadModuleDirectory(expand = False)
			
			self.moduleInfoLabel.setText("%d modules. " % (self.moduleView.modCount))
			
			self.moduleView.resetAllHighlights()
			self.moduleView.show()
			
			#if self.codeEdit and self.isTmpFile():
			#	self.codeEdit.setFileExtension(self.environment.standardFileExtension)
		
	def bindFunctionToTimer(self, func, interval):
		timer = QtCore.QTimer(self)
		timer.timeout.connect(func)
		timer.start(interval)
		return timer
		
	def showDependencies(self):#, node, updateDependencyView = True):
		node = self.currentNode
		
		if node == self.lastShownNode:
			if self.lastShownOutputCompiler != self.outputCompiler:
				self.updateCodeBubble(node)
			return
		self.lastShownNode = self.currentNode
		
		self.dependencyView.setNode(node)
		if (not self.dependenciesViewDock.isHidden()):
			self.dependencyView.updateView()
		
		self.xmlView.setNode(node)	
		if not self.xmlViewDock.isHidden():
			self.xmlView.updateView()
			
		self.metaData.setNode(node, self.getXMLDocument())
		if not self.metaData.isHidden():
			self.metaData.updateView()
		
		self.updateCodeBubble(node)
		
	def getFileCount(self):
		fileCount = 0
		
		for ws in self.workspaces:
			fileCount += ws.count()
		
		return fileCount
		
	def onProgressUpdate(self):
		if self.lastFunctionCount == -1: #and self.codeEdit and self.codeEdit.postProcessorThread:
			val = time.time() - self.startTime
			self.progressBar.setValue(min(100, val * 40))
			#self.progressBar.setFormat("%p% " + stripAll(self.processor.lastFilePath))
			
			#self.progressBar.show()
			#self.searchEdit.hide()
		else:
			self.firstStartUpdateTimer.stop()
			self.onLoadingFinished()
		
	def onLoadingFinished(self):
		self.progressBar.hide()
		self.searchEdit.show()
		
	def onProcessEvents(self):
		QtGui.QApplication.instance().processEvents()
	
	def onCompileTimeout(self):
		# Don't do this if we're actually compiling or if we have nothing to compile
		if self.running or self.compiling or (not self.codeEdit) or self.codeEdit.backgroundCompilerOutstandingTasks == 0:
			return
		
		if self.codeEdit.ppOutstandingTasks > 0:
			if 0:#(
				#	(self.currentNode and self.currentNode.nodeType == Node.ELEMENT_NODE and self.currentNode.tagName == "assign")
				#	or
				#	(self.nodeAboveCurrent and self.nodeAboveCurrent.nodeType == Node.ELEMENT_NODE and self.nodeAboveCurrent.tagName == "assign")
				#):
				pass
			else:
				#if self.loadingFinished:
				return
		
		# Create output compiler
		tmpOutputCompiler = self.createOutputCompiler("C++", temporary = True)
		self.outputCompilerThread.startWith(tmpOutputCompiler)
	
	def getEnvironmentByFilePath(self, filePath):
		ext = extractExt(filePath)
		
		if ext in self.fileExtensionToEnvironment:
			return self.fileExtensionToEnvironment[ext]
		
		return self.baseEnvironment
	
	def backgroundCompilerFinished(self):
		#if self.outputCompilerThread.lastException:
			#pass
			
			# Hmm...what should we do with background compiler error messages?
			
			#self.evalInfoLabel.setText(self.outputCompilerThread.lastException.getMsg())
			#if self.codeEdit:
				#msgView = self.codeEdit.msgView
				#if 1:#msgView.count() == 0 or isinstance(msgView.lastException, OutputCompilerException):
					#if msgView.lastException:
					#	print(msgView.lastException.__class__)
					#msgView.clear()
		
		# The output compiler
		comp = self.outputCompilerThread.outputCompiler
		
		# Set environment namespace to the main namespace of the compiler
		self.environment.mainNamespace = comp.mainClass
		
		# If the number of functions changed, rehighlight
		if self.codeEdit:
			# This function also counts the class methods:
			newFuncCount = comp.getFunctionCount()
			
			# Contrary to this one:
			#newFuncCount = len(self.environment.mainNamespace.functions)
			
			#if not self.outputCompilerThread.lastException:
			if self.needsRehighlight(newFuncCount): #self.lastCodeEdit == self.codeEdit
				self.codeEdit.rehighlightFunctionUsage()
			
			self.lastFunctionCount = newFuncCount
			self.lastCodeEdit = self.codeEdit
		
		# We love long variable names, don't we?
		ce = self.outputCompilerThread.codeEdit
		if ce:
			ce.outFile = comp.getMainFile()
			
			# Restore the scopes if possible
			self.restoreScopesOfNode(self.currentNode)
			
			# Update auto complete
			if ce.completer:
				ce.completer.bpcModel.retrieveData(self.outputCompilerThread.outputCompiler)
			
			# Adjust number of outstanding tasks
			ce.backgroundCompilerOutstandingTasks -= self.outputCompilerThread.numTasksHandled
			
			if ce.backgroundCompilerOutstandingTasks < 0:
				ce.backgroundCompilerOutstandingTasks = 0
				
			# Messages
			ce.msgView.updateViewOutputCompiler()
	
	def needsRehighlight(self, newFuncCount):
		return newFuncCount != self.lastFunctionCount and (self.codeEdit != self.lastCodeEdit or self.lastFunctionCount != -1 or self.isTmpFile())
	
	def createOutputCompiler(self, outputTarget, temporary = False, takeCache = True):
		#if self.outputCompiler:
		#	return self.outputCompiler
		
		if outputTarget.startswith("C++"):
			tmp = CPPOutputCompiler(
				self.processor,
				background = temporary,
				guiCallBack = [None, QtGui.QApplication.instance().processEvents][temporary],
			)
		elif outputTarget.startswith("Python 3"):
			tmp = PythonOutputCompiler(
				self.processor,
				background = temporary,
				guiCallBack = [None, QtGui.QApplication.instance().processEvents][temporary],
			)
		
		# Take previous cache
		if self.outputCompiler and self.outputCompiler.mainFile == self.getFilePath():
			tmp.takeOverCache(self.outputCompiler)
		
		if temporary:
			return tmp
		else:
			self.outputCompiler = tmp
	
	# Old, old code...deprecated stuff, you know?
	# But we need this in case we lack type data.
	def bubbleAllFunctionVariants(self, code, call, shownFuncs, currentOutFile):
		realFuncDefNode = None
		
		funcName = getCalledFuncName(call)
		
		# TODO: Don't depend on self.funcsDict, replace with outputCompiler data
		if funcName in self.funcsDict:
			for func in self.funcsDict[funcName].values():
				funcDefinitionNode = func.instruction
				
				# Don't show the same function twice
				if funcDefinitionNode in shownFuncs:
					continue
				
				if realFuncDefNode and realFuncDefNode != funcDefinitionNode:
					continue
				
				shownFuncs[funcDefinitionNode] = True
				
				# Documentation
				doc = getNodeComments(funcDefinitionNode)
				
				# Code
				bpcCode = nodeToBPC(funcDefinitionNode)
				#bpcCode = self.truncateBubbleCode(bpcCode)
				bpcCode = self.bubbleAddReturnType(bpcCode, call, currentOutFile)
				code.append(bpcCode)
				
				# Add the documentation afterwards
				if doc:
					code.append(doc)
	
	def bubbleAddReturnType(self, bpcCode, call, currentOutFile):
		# Do we have more information about that call?
		if currentOutFile:
			dataType = None
			try:
				# Return value
				dataType = currentOutFile.getCallDataType(call)
				if dataType and dataType != "void":
					pos = bpcCode.find("\n")
					bpcCode = (bpcCode[:pos] + "  → " + dataType + "") + bpcCode[pos:]
					return bpcCode
			except:
				return bpcCode
			
		return bpcCode
	
	#def bubbleAddReturnTypeByDefinition(self, bpcCode, funcDefNode, classImpl):
		#try:
		#	classImpl.getFuncImplementation()
	
	def truncateBubbleCode(self, bpcCode):
		lines = bpcCode.split("\n")
		codeLen = len(lines)
		
		if codeLen >= self.maxBubbleCodeLength:
			return '\n'.join(lines[:self.maxBubbleCodeLength]) + "\n\n[...]\n"
		
		return bpcCode
	
	def bubbleFunction(self, code, realFuncDefNode, call, currentOutFile, shownFuncs):
		# Don't show the same function twice
		if realFuncDefNode in shownFuncs:
			return
		
		shownFuncs[realFuncDefNode] = True
		
		# Documentation
		doc = getNodeComments(realFuncDefNode)
		
		# Code
		bpcCode = nodeToBPC(realFuncDefNode)
		#bpcCode = self.truncateBubbleCode(bpcCode)
		bpcCode = self.bubbleAddReturnType(bpcCode, call, currentOutFile)
		
		# Add it
		code.append(bpcCode)
		
		# Add the documentation afterwards
		if doc:
			code.append(doc)
	
	def updateCodeBubble(self, node):
		if not self.config.enableDocBubbles:
			return
		
		if self.codeEdit and self.codeEdit.bubble and (not self.running) and self.consoleDock.isHidden() and (self.codeEdit.hasFocus()):
			if node:
				#self.startBenchmark("Find calls in reversed order")
				calls = findCallsReversed(node)
				#self.endBenchmark()
				
				# TODO: Optimize as a dict lookup
				# If we have output compiler information
				currentOutFile = None
				if self.outputCompiler:
					self.lastShownOutputCompiler = self.outputCompiler
					cePath = self.getFilePath()
					for outFile in self.outputCompiler.outFiles.values():
						if outFile.file == cePath:
							currentOutFile = outFile
							break
				
				# Let's see if we can get some information about those calls
				code = []
				shownFuncs = dict()
				for call in calls:
					callerType = ""
					funcName = ""
					
					if currentOutFile:
						# Exceptions are your friends! ... or not?
						try:
							# Params
							if call.tagName == "call":
								#print(call.toxml())
								caller, callerType, funcName = currentOutFile.getFunctionCallInfo(call)
							elif call.tagName == "new":
								#caller = ""
								callerType = currentOutFile.getExprDataType(call)
								funcName = "init"
								
							params = getElementByTagName(call, "parameters")
							paramsString, paramTypes = currentOutFile.handleParameters(params)
							
							classImpl = currentOutFile.getClassImplementationByTypeName(callerType)
							
							try:
								realFunc = classImpl.getMatchingFunction(funcName, paramTypes)
								realFuncDefNode = realFunc.node
								
								if callerType:
									code.append("# %s" % (callerType))
								
								self.bubbleFunction(code, realFuncDefNode, call, currentOutFile, shownFuncs)
							except:
								try:
									candidates = classImpl.getCandidates(funcName)
									
									if callerType:
										code.append("# %s" % (callerType))
									
									for func in candidates:
										self.bubbleFunction(code, func.node, call, currentOutFile, shownFuncs)
									
									continue
								except:
									continue
						
						except:
							# Only show all function variants if code bubble is empty
							if (not code) and call.tagName == "call":
								if callerType:
									code.append("# %s" % (callerType))
								
								self.bubbleAllFunctionVariants(code, call, shownFuncs, currentOutFile)
							continue
					else:
						# Only show all function variants if code bubble is empty
						if (not code) and call.tagName == "call":
							if callerType:
								code.append("# %s" % (callerType))
							
							self.bubbleAllFunctionVariants(code, call, shownFuncs, currentOutFile)
						continue
				
				if code:
					codeText = "\n".join(code)
					lines = codeText.count("\n") + 1
					
					if lines > 1:
						# Because of Master-of-Weirdness a.k.a. Qt we need to SHOW FIRST, THEN CALCULATE DOCUMENT SIZE
						self.codeEdit.bubble.show()
						self.codeEdit.bubble.setPlainText(codeText)
						
						# TODO: Can we optimize this a bit?
						# DO THIS 2 TIMES ELSE YOUR HEIGHT WILL BE INVALID - GREETINGS FROM TROLLTECH
						self.codeEdit.adjustBubbleSize()
						self.codeEdit.adjustBubbleSize()
						
						#self.codeEdit.bubble.show()
				elif self.codeEdit:
					self.codeEdit.bubble.hide()#setPlainText("Unknown function „%s“" % funcName)
			elif self.codeEdit:
				self.codeEdit.bubble.hide()
		elif self.codeEdit:
			self.codeEdit.bubble.hide()
		
	def printL(self, msg):
		print(msg)
		self.console.activate("Log")
		self.consoleDock.show()
		
	def getPostProcessorFile(self, path):
		return self.processor.getCompiledFiles()[path]
		
	def getCurrentPostProcessorFile(self):
		return self.processor.getCompiledFiles()[self.getFilePath()]
		
	def hideEvent(self, event):
		self.geometryState = self.saveState()
		super().hideEvent(event)
		
	def showEvent(self, event):
		super().showEvent(event)
		
		if self.geometryState:
			self.restoreState(self.geometryState)
		
	def setCurrentWorkspace(self, index, activateButton = True):
		if activateButton:
			button = self.workspacesView.group.button(index)
			button.setChecked(True)
			self.workspacesView.setCurrentWorkspaceByButton(button)
		else:
			if self.currentWorkspace is not None:
				self.currentWorkspace.deactivateWorkspace()
			
			self.currentWorkspace = self.workspaces[index]
			self.currentWorkspace.activateWorkspace()
		
	def closeCurrentTab(self):
		self.currentWorkspace.closeCurrentCodeEdit()
		
	def gitPullFinished(self):
		print("Done.")
		
	def loadConfig(self):
		if os.path.isfile(getConfigDir() + "studio/settings.ini"):
			try:
				self.config = BPConfiguration(self, getConfigDir() + "studio/settings.ini")
			except:
				self.config = BPConfiguration(self, getIDERoot() + "default-settings.ini")
		else:
			self.config = BPConfiguration(self, getIDERoot() + "default-settings.ini")
		#self.config.applySettings()
		
	def getUIFromCache(self, uiFileName):
		if not uiFileName in self.uiCache:
			self.uiCache[uiFileName] = uic.loadUi(getIDERoot() + "ui/%s.ui" % uiFileName)
			return self.uiCache[uiFileName], False
		return self.uiCache[uiFileName], True
		
	def onSettingsItemChange(self, current, previous):
		name = current.toolTip(0)
		uiFileName = "preferences/" + name.replace(" - ", ".").lower()
		
		widget, existed = self.getUIFromCache(uiFileName)
		
		# Update values
		self.config.updatePreferencesWidget(uiFileName, widget)
		
		if not existed:
			self.config.initPreferencesWidget(uiFileName, widget)
		
		if previous:
			previousFileName = "preferences/" + previous.toolTip(0).replace(" - ", ".").lower()
			self.uiCache[previousFileName].hide()
			self.preferences.currentBox.layout().removeWidget(self.uiCache[previousFileName])
		
		self.preferences.currentBox.setTitle(name)
		
		self.preferences.currentBox.layout()
		self.preferences.currentBox.layout().addWidget(widget)
		
		widget.show()
	
	def updateLineInfo(self, force = False):#, updateDependencyView = True):
		if self.codeEdit is None:
			self.lineNumberLabel.setText("")
			self.moduleInfoLabel.setText("")
			return
		
		newBlockPos = self.codeEdit.getLineNumber()
		if force or newBlockPos != self.lastBlockPos:
			self.lastBlockPos = newBlockPos
			selectedNode = None
			
			lineIndex = self.codeEdit.getLineIndex()
			
			funcCount = 0
			if self.processorOutFile:
				funcCount = self.processorOutFile.funcCount
				del self.processorOutFile
				self.processorOutFile = None
			
			self.lineNumberLabel.setText(" Line %d / %d" % (lineIndex + 1, self.codeEdit.blockCount()))
			
			#expr = self.codeEdit.getCurrentLine()
			#if expr:
			#	try:
			#		evalExpr = eval(expr)
			#		if evalExpr:
			#			self.evalInfoLabel.setText("%s => %s" % (expr, evalExpr))
			#	except:
			#		self.evalInfoLabel.setText("")
			
			selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
			
			# Check that line
			self.currentNode = selectedNode
			
			#self.showDependencies(selectedNode, updateDependencyView)
			
			# Clear all highlights
			self.codeEdit.clearHighlights()
			self.codeEdit.highlightLine(lineIndex, self.config.theme["current-line"])
		
	def restoreScopesOfNode(self, selectedNode):
		if not selectedNode:
			selectedNode = self.lastShownNode
		
		if not self.codeEdit:
			return
		
		if self.codeEdit.outFile and selectedNode:
			#print("Before")
			#self.codeEdit.outFile.debugScopes()
			
			savedNode = selectedNode
			
			if savedNode.nodeType != Node.TEXT_NODE and savedNode.hasAttribute("id"):
				savedNodeId = savedNode.getAttribute("id")
			else:
				savedNodeId = -1
			
			while (savedNode.nodeType == Node.TEXT_NODE or savedNode.tagName != "module") and ((not savedNodeId) or (not savedNodeId in self.codeEdit.outFile.nodeIdToScope)):
				#print("Trying: " + savedNode.getAttribute("id"))
				savedNode = savedNode.parentNode
				
				try:
					savedNodeId = savedNode.getAttribute("id")
				except:
					savedNodeId = None
			
			if savedNode and not savedNode.tagName == "module":
				try:
					self.codeEdit.outFile.restoreScopesForNodeId(savedNodeId)
					#print("YAY! ID: %s" % savedNodeId)
					return
				except:
					print("Could not find scope information for node %s" % tagName(savedNode))
				else:
					self.previousScopes = self.codeEdit.outFile.scopes
			else:
				pass#print("Scopes:")
				#self.codeEdit.outFile.debugNodeToScope()
				#self.codeEdit.outFile.debugScopes()
		
		# Okay we have a problem, but maybe we have old scope data?
		if self.previousScopes and self.codeEdit.outFile:
			print("USING OLD SCOPE DATA")
			self.codeEdit.outFile.restoreScopes(self.previousScopes)
		
	def getModulePath(self, importedModule):
		return getModulePath(importedModule, extractDir(self.getFilePath()), self.getProjectPath())
	
	def localToGlobalImport(self, importedModule):
		return fixPath(stripExt(self.getModulePath(importedModule)[len(getModuleDir()):])).replace("/", ".").replace(" ", "_")
	
	def splitModulePath(self, importedModule):
		parts = importedModule.split(".")
		if len(parts) >= 2 and parts[-1] == parts[-2]:
			parts = parts[:-1]
		return parts
	
	def getModuleImportType(self, importedModule):
		return getModuleImportType(importedModule, extractDir(self.getFilePath()), self.getProjectPath())
		
	def updateModuleBrowser(self):
		self.moduleView.updateView()
		
	def runPostProcessor(self, codeEdit):
		# TODO: Less cpu usage
		if self.threaded: #and not codeEdit.reloading:
			if not codeEdit.postProcessorThread.isRunning():
				codeEdit.postProcessorThread.startWith()
			#else:
			#	codeEdit.disableUpdatesFlag = False
		else:
			#raise "Not implemented in single-threaded mode"
			ppThread = BPPostProcessorThread(self)
			ppThread.codeEdit = codeEdit
			ppThread.numTasksHandled = codeEdit.ppOutstandingTasks
			ppThread.run()
			self.postProcessorFinished(ppThread)
		
	def postProcessorFinished(self, ppThread = None):
		if ppThread is None:
			if not self.codeEdit:
				return
			
			ppThread = self.codeEdit.postProcessorThread
		
		ppCodeEdit = ppThread.codeEdit
		self.processorOutFile = ppThread.ppFile
		
		if self.codeEdit and self.codeEdit.reloading:
			index = self.currentWorkspace.currentIndex()
			self.currentWorkspace.changeCodeEdit(index)
		
		# Update line info
		self.updateLineInfo(force=True)#, updateDependencyView=False)
		
		# Exists?
		if ppCodeEdit is None or ppCodeEdit.isTextFile:
			return
		
		# Subtract number of tasks handled
		ppCodeEdit.ppOutstandingTasks -= ppThread.numTasksHandled
		if ppCodeEdit.ppOutstandingTasks < 0:
			ppCodeEdit.ppOutstandingTasks = 0
		
		# Msg view
		ppCodeEdit.msgView.updateViewPostProcessor()
		
		# Update auto completer data
		self.funcsDict = self.processor.getFunctionsDict()
		
		# TODO: Replace this as we don't need it anymore
		if 0:
			self.classesDict = self.processor.getClassesDict()
			
			if (
					ppCodeEdit.completer
					and
					(
						len(self.funcsDict) != ppCodeEdit.completer.bpcModel.funcListLen
						or len(self.classesDict) != ppCodeEdit.completer.bpcModel.classesListLen
					)
				):
				funcsList = list(self.funcsDict)
				classesList = list(self.classesDict)
				
				classesList.sort()
				funcsList.sort()
				
				self.shortCuts = buildShortcutDict(funcsList)
				ppCodeEdit.completer.bpcModel.setAutoCompleteLists(funcsList, self.shortCuts, classesList)
		
		# After we parsed the functions, set the text and highlight the file
		if ppCodeEdit.disableUpdatesFlag:
			ppCodeEdit.disableUpdatesFlag = False
			ppCodeEdit.rehighlightFunctionUsage()
		
		if (not self.dependenciesViewDock.isHidden()):
			self.dependencyView.updateView()
		
		# If the function name changed, rehighlight
		lineIndex = ppCodeEdit.getLineIndex()
		selectedNode = ppCodeEdit.getNodeByLineIndex(lineIndex)
		if tagName(selectedNode) in functionNodeTagNames:
			selectedOldNode = ppCodeEdit.getOldNodeByLineIndex(lineIndex)
			if tagName(selectedOldNode) in functionNodeTagNames:
				nameNew = getElementByTagName(selectedNode, "name")
				nameOld = getElementByTagName(selectedOldNode, "name")
				
				if nameOld and nameNew and nameNew.childNodes[0].nodeValue != nameOld.childNodes[0].nodeValue:
					ppCodeEdit.rehighlightFunctionUsage()
		
		#lineIndex = self.codeEdit.getLineIndex()
		#selectedNode = self.codeEdit.getNodeByLineIndex(lineIndex)
		#previousLineNode = self.codeEdit.getNodeByLineIndex(lineIndex - 1)
		#previousLineOldNode = self.codeEdit.getOldNodeByLineIndex(lineIndex - 1)
		
		#currentLine = self.codeEdit.getCurrentLine()
		#currentTag = tagName(selectedNode)
		#previousLineTag = tagName(previousLineNode)
		#previousLineOldTag = tagName(previousLineOldNode)
		
		#if currentTag == "function" or (previousLineTag == "function" and currentLine == '\t') or (previousLineOldTag == "function" and currentLine == ""):#(tagName(selectedNode) == "function") or ((tagName(previousLine) == "function") and self.getCurrentLine() == "\t"):
		#	self.codeEdit.rehighlightFunctionUsage(selectedNode)
		
		#del gc.garbage[:]
		
		# Leak detection
		# if 0:
			# import flua.Compiler.Utils.GC as gcInfo
			# print("[--------")
			# gcInfo.showMostCommonTypes()
			# print("BPC Files: %d" % gcInfo.countByTypename("BPCFile"))
			# print("PP Files: %d" % gcInfo.countByTypename("BPPostProcessorFile"))
			# for x in gcInfo.byType("BPPostProcessorFile"):
				# print(x.getFilePath())
			# print("--------]")
		
	def getXMLDocument(self):
		if self.codeEdit is None:
			return None
		
		return self.codeEdit.doc
		
	def forEachCodeEditDo(self, func):
		for workspace in self.workspaces:
			for codeEdit in workspace.getCodeEditList():
				func(codeEdit)
			
	def setFilePath(self, path):
		filePath = os.path.abspath(path)
		
		if self.processor:
			self.processor.setMainFile(filePath)
			
		if self.codeEdit:
			self.codeEdit.setFilePath(filePath)
		
	def getProjectPath(self):
		if self.codeEdit is None:
			return ""
		
		# TODO: Project path
		return self.codeEdit.getFilePath()
		
	def getFilePath(self):
		if self.codeEdit is None:
			return ""
		
		return self.codeEdit.getFilePath()
		
	def getErrorCount(self):
		if not self.codeEdit:
			return 0
		return self.codeEdit.msgView.count()
		
	def loadFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		self.setFilePath(fileName)
		
		# Read
		print("-" * 80)
		print("File: %s " % (fileName.rjust(80 - 7)))
		#self.startBenchmark("LoadXMLFile (physically read file)")
		xmlCode = loadXMLFile(self.getFilePath())
		#self.endBenchmark()
		
		# TODO: Clear all views
		self.dependencyView.clear()
		
		# Let's rock!
		self.startBenchmark("[%s] NodeToBPC" % stripDir(fileName))
		if self.codeEdit is not None:
			self.codeEdit.setXML(xmlCode)
		self.endBenchmark()
		
		self.afterSwitchingFile()
		
	# If you need to do something BEFORE a new file gets loaded, this is the right place
	def beforeSwitchingFile(self):
		# Reset function count
		self.lastFunctionCount = -1
		
		# Clear all module highlights
		self.moduleView.resetAllHighlights()
		
		# Enable dependency view from the very beginning
		self.lastBlockPos = -1
		
	# If you need to do something AFTER a new file gets loaded, this is the right place
	def afterSwitchingFile(self):
		pass
		
	def loadTextFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		with codecs.open(fileName, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		# Let's rock!
		if self.codeEdit:
			self.codeEdit.disableUpdatesFlag = True
			#del self.codeEdit.highlighter
			#self.codeEdit.highlighter = CPPHighlighter(self.codeEdit.qdoc, self)
			self.codeEdit.setPlainText(codeText)
		
		# Enable dependency view for first line
		self.afterSwitchingFile()
		
	def loadBPCFileToEditor(self, fileName):
		self.beforeSwitchingFile()
		
		self.setFilePath(fileName)
		
		# Read
		self.startBenchmark("LoadBPCFile (physically read file)")
		with codecs.open(fileName, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		# TODO: Remove all BOMs
		if len(codeText) and codeText[0] == '\ufeff': #codecs.BOM_UTF8:
			codeText = codeText[1:]
		self.endBenchmark()
		
		# Let's rock!
		if self.codeEdit:
			self.codeEdit.disableUpdatesFlag = True
			self.codeEdit.setPlainText(codeText)
			self.codeEdit.disableUpdatesFlag = False
			self.codeEdit.runUpdater()
		
		#self.startBenchmark("CodeEdit (interpret file)")
		#self.dependencyView.clear()
		#self.codeEdit.setXML(xmlCode)
		#self.endBenchmark()
		
		# Enable dependency view for first line
		self.afterSwitchingFile()
		
	def isTmpFile(self):
		return self.isTmpPath(self.getFilePath())
		
	def isTmpPath(self, path):
		if not path:
			return True
		
		return extractDir(path) == self.tmpPath
		
	def highlightError(self, lineNum):
		if not self.codeEdit:
			return
		
		self.codeEdit.setFocus(QtCore.Qt.MouseFocusReason)
		self.codeEdit.goToLineEnd(max(lineNum, 0))
		self.codeEdit.highlightLine(max(lineNum - 1, 0), self.config.theme["error-line"])
		
	def getCurrentTheme(self):
		return self.config.theme
		
	def onCursorPosChange(self):
		self.updateLineInfo()
		
	def createDockWidget(self, name, widget, area):
		shortcut = self.dockShortcuts[len(self.docks)]
		
		if name == "Chat":
			# Temporarily hardcoded
			dockName = "Instant Feedback"
		else:
			dockName = name
		
		newDock = QtGui.QDockWidget("%s (Alt + %s)" % (dockName, shortcut), self)
		
		#newDock.setFeatures(QtGui.QDockWidget.DockWidgetMovable | QtGui.QDockWidget.DockWidgetFloatable)
		newDock.setWidget(widget)
		newDock.setObjectName(name)
		#newDock.installEventFilter(self)
		self.addDockWidget(area, newDock)
		
		self.dockMenuActions.append(self.connectVisibilityToViewMenu(name, newDock, shortcut))
		self.docks.append(newDock)
		
		return newDock
		
	def connectVisibilityToViewMenu(self, name, widget, shortcut):
		newAction = QtGui.QAction(shortcut, self)
		newAction.setCheckable(True)
		newAction.setToolTip(name)
		newAction.setWhatsThis(name)
		newAction.setShortcut("Alt+" + shortcut)
		newAction.toggled.connect(widget.setVisible)
		widget.visibilityChanged.connect(newAction.setChecked)
		
		#self.menuView.addAction(newAction)
		
		# Main menu icons
		#self.mainMenuBar.addSeparator()
		newAction.setIcon(self.dockIcons[name])
		self.mainMenuBar.addAction(newAction)
		
		return newAction
		
	def notify(self, msg, title = "Notification"):
		msgBox = QtGui.QMessageBox(self)
		msgBox.setWindowTitle(title)
		msgBox.setText(msg)
		msgBox.setIcon(QtGui.QMessageBox.Information)
		msgBox.setStyleSheet(self.config.dialogStyleSheet)
		msgBox.exec()
		
	def center(self):
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
		
	def sizeHint(self):
		return QtCore.QSize(1024, 600)

def main(multiThreading = True):
	# Create the application
	#gc.set_#debug(gc.DEBUG_LEAK)
	#gc.enable()
	app = QtGui.QApplication(sys.argv)
	editor = BPMainWindow(multiThreading)
	exitCode = app.exec_()
	
	# In order to not have a segfault
	editor.console.detach()
	
	# Save config
	editor.config.saveSettings()
	editor.saveSession()
	
	print("--- EOP: %d ---" % exitCode)
	#sys.exit(exitCode)

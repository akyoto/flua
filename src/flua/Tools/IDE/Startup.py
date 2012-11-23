####################################################################
# Header
####################################################################
# Module:   IDE startup
# Author:   Eduard Urbach

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
from flua.Tools.IDE.Threads import *
from flua.Tools.IDE.Utils import *
from flua.Tools.IDE.Editor import *
from flua.Tools.IDE.Widgets import *
from flua.Tools.IDE.MenuActions import *
from flua.Tools.IDE.Environment import *
import configparser

####################################################################
# Classes
####################################################################

class Startup:
	
	def initAll(self):
		self.startBenchmark("Init Theme")
		self.initTheme()
		self.endBenchmark()
		
		self.startBenchmark("Init Workspaces")
		self.initWorkspaces()
		self.endBenchmark()
		
		self.startBenchmark("Init UI")
		self.initUI()
		self.endBenchmark()
		
		self.setCurrentWorkspace(0)
		
		self.startBenchmark("Init Toolbar")
		self.initToolBar()
		self.endBenchmark()
		
		self.startBenchmark("Init Dock Icons")
		self.initDockIcons()
		self.endBenchmark()
		
		#self.startBenchmark("Init Docks")
		#self.initDocks()
		#self.endBenchmark()
		
		self.startBenchmark("Init Compiler")
		self.initCompiler()
		self.endBenchmark()
		
		# New file
		#self.newFile()
		
		self.startBenchmark("Init Preferences")
		self.initPreferences()
		self.endBenchmark()
		
		self.startBenchmark("Init Actions")
		self.initActions()
		self.endBenchmark()
		
		# Repository list
		self.repos = [x for x in readFile(getIDERoot() + "repositories.txt").split("\n") if x]
	
	def initPreferences(self):
		self.preferences = uic.loadUi("ui/preferences.ui")
		self.preferences.settings.expandToDepth(0)
		self.preferences.settings.currentItemChanged.connect(self.onSettingsItemChange)
		
	def initUI(self):
		uic.loadUi(getIDERoot() + "ui/flua-ide.ui", self)
		
		# StatusBar
		self.statusBar.setFont(QtGui.QFont("Ubuntu", 9))
		
		# Window
		#self.setWindowTitle("Flua IDE")
		#self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.setGeometry(0, 0, 1000, 650)
		self.center()
		
		# Status bar
		self.lineNumberLabel = QtGui.QLabel()
		self.moduleInfoLabel = QtGui.QLabel()
		self.evalInfoLabel = QtGui.QLabel("")
		self.lineNumberLabel.setMinimumWidth(100)
		self.progressBar = QtGui.QProgressBar(self.statusBar)
		self.progressBar.setTextVisible(True)
		#self.progressBar.setMinimumWidth(100)
		#self.progressBar.hide()
		
		#spacer1 = QtGui.QWidget(self.statusBar)
		#spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#spacer2 = QtGui.QWidget(self.statusBar)
		#spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#self.statusBar.addPermanentWidget(spacer1)
		self.statusBar.addWidget(self.lineNumberLabel)
		self.statusBar.addWidget(self.moduleInfoLabel)
		self.statusBar.addWidget(self.evalInfoLabel)
		
		# Syntax switcher
		self.syntaxSwitcher = QtGui.QComboBox(self)
		self.syntaxSwitcher.setToolTip("Syntax switcher")
		self.syntaxSwitcher.addItem("Flua Syntax              ")
		self.syntaxSwitcher.addItem("Flua goes C++            ")
		self.syntaxSwitcher.addItem("Flua goes Ruby           ")
		self.syntaxSwitcher.addItem("Flua goes Python         ")
		self.syntaxSwitcher.currentIndexChanged.connect(self.switchSyntax)
		self.statusBar.addPermanentWidget(self.syntaxSwitcher, 0)
		
		# Progress bar
		self.statusBar.addPermanentWidget(self.progressBar, 1)
		
		# Search
		self.searchEdit = BPSearchEdit(self)
		self.replaceEdit = BPReplaceEdit(self)
		
		self.searchEdit.hide()
		
		self.statusBar.addPermanentWidget(self.searchEdit, 1)
		self.statusBar.addPermanentWidget(self.replaceEdit, 1)
		
		# Search results
		self.searchResults = BPSearchResultsWidget(self)
		
		# Command edit
		self.cmdEdit = BPCommandEdit(self)
		self.cmdEdit.hide()
		
		self.statusBar.addPermanentWidget(self.cmdEdit, 1)
		
		# Target switching
		self.targetSwitcher = QtGui.QComboBox(self)
		self.targetSwitcher.setToolTip("Target language")
		self.targetSwitcher.addItem("C++")
		self.targetSwitcher.addItem("Python 3 (in development)")
		self.targetSwitcher.addItem("HTML5 (not implemented)")
		
		self.statusBar.addPermanentWidget(self.targetSwitcher, 0)
		
		# Workspaces view
		self.workspacesView = BPWorkspacesView(self)
		self.statusBar.addPermanentWidget(self.workspacesView, 0)
		
		#self.statusBar.setLayout(hBoxLayout)
		
		self.codeEdit = None
		
		#self.statusBar.hide()
		#self.toolBar.hide()
		#self.syntaxSwitcherBar.hide()
		
	def initDockIcons(self):
		defaultIcon = QtGui.QIcon("images/icons/categories/applications-other.png")
		self.dockIcons = {
			"Modules"      : None,
			"Outline"      : None,
			"XML"          : None,
			"Files"        : None,
			"Meta data"    : None,
			"Dependencies" : None,
			"Scribble"     : None,
			"Console"      : None,
			"Files"        : None,
			"Chat"         : None,
		}
		
		for iconName in self.dockIcons.keys():
			self.dockIcons[iconName] = QtGui.QIcon("images/icons/docks/%s.png" % normalizeName(iconName).lower())
		
	def initDocks(self):
		self.setDockOptions(QtGui.QMainWindow.AnimatedDocks)# | QtGui.QMainWindow.AllowNestedDocks)
		
		# Module view
		#self.startBenchmark("Init module browser")
		for env in self.environments:
			env.moduleView = BPModuleBrowser(self, env)
		
		self.moduleView = self.environment.moduleView
		#self.endBenchmark()
		
		# Console
		#self.startBenchmark(" * Console")
		self.console = BPConsoleWidget(self)
		#self.endBenchmark()
		
		# XML view
		#self.startBenchmark(" * XML view")
		self.xmlView = XMLCodeEdit(self)
		self.xmlView.setReadOnly(1)
		#self.endBenchmark()
		
		# Dependency view
		#self.startBenchmark(" * Dependency view")
		self.dependencyView = BPDependencyView(self)
		self.dependencyView.setReadOnly(1)
		#self.endBenchmark()
		
		# File view
		#self.startBenchmark(" * File browser")
		self.fileView = BPFileBrowser(self, getModuleDir())
		#self.endBenchmark()
		
		# Scribble - I absolutely love this feature in Geany!
		# It's always the little things that are awesome :)
		
		#self.startBenchmark(" * Scribble")
		self.scribble = BPScribbleWidget(self, getIDERoot() + "miscellaneous/scribble.txt")
		#self.endBenchmark()
		
		# Chat
		#self.chatWidget = BPChatWidget(self)
		
		# Outline
		#self.startBenchmark(" * Outline")
		self.outlineView = BPOutlineView(self)
		#self.endBenchmark()
		
		# Meta data
		#self.startBenchmark(" * Meta data")
		self.metaData = BPMetaDataWidget(self)
		#self.endBenchmark()
		
		#self.workspacesViewDock = self.createDockWidget("Workspaces", self.workspacesView, QtCore.Qt.LeftDockWidgetArea)
		#self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.LeftDockWidgetArea)
		
		self.moduleViewDock = self.createDockWidget("Modules", self.moduleView, QtCore.Qt.LeftDockWidgetArea)
		self.consoleDock = self.createDockWidget("Console", self.console, QtCore.Qt.BottomDockWidgetArea)
		self.outlineViewDock = self.createDockWidget("Outline", self.outlineView, QtCore.Qt.RightDockWidgetArea)
		self.metaDataViewDock = self.createDockWidget("Meta data", self.metaData, QtCore.Qt.RightDockWidgetArea)
		self.dependenciesViewDock = self.createDockWidget("Dependencies", self.dependencyView, QtCore.Qt.RightDockWidgetArea)
		self.scribbleDock = self.createDockWidget("Scribble", self.scribble, QtCore.Qt.BottomDockWidgetArea)
		self.xmlViewDock = self.createDockWidget("XML", self.xmlView, QtCore.Qt.RightDockWidgetArea)
		self.fileViewDock = self.createDockWidget("Files", self.fileView, QtCore.Qt.RightDockWidgetArea)
		#self.chatViewDock = self.createDockWidget("Chat", self.chatWidget, QtCore.Qt.BottomDockWidgetArea)
		
		self.outlineViewDock.hide()
		self.metaDataViewDock.hide()
		self.scribbleDock.hide()
		self.fileViewDock.hide()
		self.dependenciesViewDock.hide()
		#self.chatViewDock.hide()
		
		#self.msgViewDock.hide()
		
		#self.xmlViewDock.show()
		
		if not self.config.developerMode:
			self.xmlViewDock.hide()
			self.consoleDock.hide()
		
		# Needed for workspaces
		self.viewsInitialized = True
		
	def initActions(self):
		actions = {
			# File
			self.actionNew : self.newFile,
			self.actionOpen : self.openFile,
			self.actionSave : self.saveFile,
			self.actionSaveAs : self.saveAsFile,
			self.actionClose : self.closeCurrentTab,
			self.actionReopenLastFile : self.reopenLastFile,
			self.actionExit : self.close,
			
			# Edit
			self.actionUndo : self.undoLastAction,
			self.actionRedo : self.redoLastAction,
			self.actionSearch : self.showSearch,
			self.actionRegExSearch : self.showRegexSearch,
			self.actionFindNext : self.findNext,
			self.actionCopy : self.copy,
			self.actionCut : self.cut,
			self.actionPaste : self.paste,
			self.actionPreferences : self.showPreferences,
			
			# Module
			self.actionRun : self.onRunModule,
			self.actionRunOptimized : self.runModuleOptimized,
			self.actionRunDebug : self.runDebug,
			self.actionRunModuleTests : self.runModuleTests,
			self.actionCleanAllTargets : self.cleanAllTargets,
			self.actionViewSource : self.viewSource,
			self.actionProperties : self.showModuleProperties,
			
			# Utilities
			self.actionCommand : self.enterCommand,
			self.actionJumpToDefinition : self.jumpToDefinition,
			self.actionDuplicateLine : self.duplicateLine,
			self.actionToggleComment : self.toggleComment,
			self.actionCreateDefaultImplementation : self.createDefaultImplementation,
			self.actionFindPossibleParallelizationPoints : self.findPossibleParallelizationPoints,
			
			# Repositories
			self.actionRepositoryList : self.showRepositoryList,
			self.actionConnectWithGitHub : self.connectWithGitHub,
			
			# Workspaces
			self.actionWorkspace_1 : lambda: self.setCurrentWorkspace(0),
			self.actionWorkspace_2 : lambda: self.setCurrentWorkspace(1),
			self.actionWorkspace_3 : lambda: self.setCurrentWorkspace(2),
			self.actionWorkspace_4 : lambda: self.setCurrentWorkspace(3),
			self.actionWorkspace_Q : lambda: self.setCurrentWorkspace(4),
			self.actionWorkspace_W : lambda: self.setCurrentWorkspace(5),
			self.actionWorkspace_E : lambda: self.setCurrentWorkspace(6),
			self.actionWorkspace_R : lambda: self.setCurrentWorkspace(7),
			
			# Environments
			self.actionEnvFlua : lambda: self.setEnvironment(self.fluaEnvironment),
			self.actionEnvPython : lambda: self.setEnvironment(self.pythonEnvironment),
			self.actionEnvCPP : lambda: self.setEnvironment(self.cppEnvironment),
			self.actionEnvGLSL : lambda: self.setEnvironment(self.glslEnvironment),
			self.actionEnvNone : lambda: self.setEnvironment(self.baseEnvironment),
			
			# Window
			self.actionToggleFullscreen : self.toggleFullScreen,
			
			# Help
			self.actionIntroduction : self.showIntroduction,
			self.actionChangeLog : self.showChangeLog,
			self.actionResetLocalChanges : self.resetLocalChanges,
			self.actionResetLocalFileChanges : self.resetLocalFileChanges,
			self.actionDownloadUpdates : self.downloadUpdates,
			self.actionReportBug : self.reportBug,
			self.actionThanksTo : self.thanksTo,
			self.actionAbout : self.about,
			
			# FAQ
			self.actionFAQUpdate : self.faqUpdate,
			self.actionFAQCompiling : self.faqCompiling,
			self.actionFAQTabs : self.faqTabs,
		}
		
		for action, function in actions.items():
			action.triggered.connect(function)
		
	def initWorkspaces(self):
		# Workspaces
		self.currentWorkspace = None
		self.workspacesContainer = QtGui.QWidget(self)
		self.workspacesContainer.setContentsMargins(0, 0, 0, 0)
		
		hBox = QtGui.QHBoxLayout()
		hBox.setContentsMargins(0, 0, 0, 0)
		self.workspacesContainer.setLayout(hBox)
		
		self.workspaces = [
			BPWorkspace(self, 0),
			BPWorkspace(self, 1),
			BPWorkspace(self, 2),
			BPWorkspace(self, 3),
			BPWorkspace(self, 4),
			BPWorkspace(self, 5),
			BPWorkspace(self, 6),
			BPWorkspace(self, 7),
		]
		
	def loadSession(self):
		self.progressBar.setValue(0)
		
		self.sessionParser = createConfigParser()
		
		try:
			with codecs.open(getConfigDir() + "studio/session.ini", "r", "utf-8") as inStream:
				self.sessionParser.readfp(inStream)
		except:
			self.newFile()
		else:
			maxFileNum = self.sessionParser.getint("General", "FileCount")
			
			# Prevent division by zero
			if maxFileNum == 0:
				maxFileNum = 1
			
			# Load all workspaces
			num = 0
			for ws in self.workspaces:
				section = "Workspace %d" % num
				
				try:
					self.setCurrentWorkspace(num)
					
					fileNum = 0
					while 1:
						filePath = self.sessionParser.get(section, "File%d" % fileNum)
						cursorPos = self.sessionParser.getint(section, "CursorPosition%d" % fileNum)
						
						# Open it
						ce = self.openFile(filePath, ignoreLoadingFinished = True)
						
						if ce:
							ce.setCursorPosition(cursorPos)
						
						fileNum += 1
						self.progressBar.setValue(fileNum / maxFileNum * 100)
				except:
					pass
				
				num += 1
				
			# Session settings
			self.setCurrentWorkspace(self.sessionParser.getint("General", "CurrentWorkspace"))
			self.currentWorkspace.changeCodeEdit(self.sessionParser.getint("General", "CurrentIndex"))
		
	def saveSession(self):
		self.sessionParser = createConfigParser()
		
		# Session settings
		self.sessionParser.add_section("General")
		self.sessionParser.set("General", "CurrentWorkspace", str(self.currentWorkspace.wsID))
		self.sessionParser.set("General", "CurrentIndex", str(self.currentWorkspace.currentIndex()))
		#self.sessionParser.set("General", "CurrentCursorPosition", str(self.codeEdit.getCursorPosition()))
		
		# Save all workspaces
		num = 0
		maxFileNum = 0
		for ws in self.workspaces:
			section = "Workspace %d" % num
			self.sessionParser.add_section(section)
			
			fileNum = 0
			for filePath, cursorPos in ws.getSessionInfo():
				if not self.isTmpPath(filePath):
					self.sessionParser.set(section, "File%d" % fileNum, filePath)
					self.sessionParser.set(section, "CursorPosition%d" % fileNum, str(cursorPos))
					fileNum += 1
			
			maxFileNum += fileNum
			num += 1
			
		# Max file count
		self.sessionParser.set("General", "FileCount", str(self.getFileCount()))
		
		with codecs.open(getConfigDir() + "studio/session.ini", "w", "utf-8") as outStream:
			self.sessionParser.write(outStream)
		
	def initTheme(self):
		if self.config.useBold:
			useBold = 'bold'
		else:
			useBold = ''
		
		self.themes = {
			"Default": {
				'default': cf("#272727"),
				'default-background': "#ffffff",
				'keyword': cf('blue'),
				'operator': cf('red'),
				'brace': cf('darkGray'),
				'comma': cf('#555555'),
				'output-target': cf('#666666'),
				'include-file': cf('#666666'),
				'string': cf('#009000'),
				'string2': cf('darkMagenta'),
				'comment': cf('#df4000'),
				'disabled': cf('#cccccc', 'italic'),
				'self': cf('#666666'),
				'number': cf('brown'),
				'hex-number': cf('brown'),
				'preprocessor': cf('#005000'),
				'file-link': cf('#0000ff', useBold),
				'matching-brackets': cf('', 'underline'),
				
				'function': cf('#171717', useBold),
				'side-effects-extern-function': cf('#ee0000', useBold),
				'no-side-effects-extern-function': cf('#000099', useBold),
				'ref-transparent-extern-function' : cf('#009900', useBold),
				
				'class-function': cf('#008000', useBold),
				'class-getter': cf('#003060', useBold),
				'class-setter': cf('#003060', useBold),
				'class-operator': cf('#008000', useBold),
				'class-iterator-type': cf('#008000', useBold),
				'class-cast-definition': cf('#500050', useBold),
				'class-name': cf('#000030'),
				
				'local-module-import': cf('#df2000', useBold), #cf2000
				'project-module-import': cf('#378737', useBold),
				'global-module-import': cf('#aa11aa', useBold),
				
				'module-browser-directory': QtGui.QBrush(QtGui.QColor("#adadad")),
				'module-browser-module': QtGui.QBrush(QtGui.QColor("#272727")),
				
				'doc-modified' : QtGui.QColor("#ff0000"),
				'doc-unmodified' : QtGui.QColor("#000000"),
				'doc-selected' : QtGui.QColor("#000000"),
				
				'error-line' : QtGui.QColor("#ffddcc"),
				'current-line' : None,
				
				'compile-log' : cf("#666666"),
				'benchmark' : cf("#333333"),
				'program-output' : cf('#10e010'),
				'traceback' : cf("#333333"),
				'compiler-error' : cf("#ff0000"),
				
				'internal-function' : cf('#ffa0c0', useBold),
				'internal-datatype' : cf('#aa11aa', useBold),
				'internal-main' : cf('#0000ff', useBold),
			},
			
			# Dark theme
			"Dark": {
				'default': cf("#eeeeee"),
				'default-background': "#272727",
				'keyword': cf('#eeccaa'),
				'operator': cf('#aaaaaa'),
				'brace': cf('#808080'),
				'comma': cf('#acacac'),
				'output-target': cf('#aa9988'),
				'include-file': cf('#aa9988'),
				'string': cf('#10e010'),
				'string2': cf('darkMagenta'),
				'comment': cf('#ffff99'),
				'disabled': cf('#cccccc', 'italic'),
				'self': cf('#cccccc'),
				'number': cf('#ff6020'),
				'hex-number': cf('#ff6020'),
				'preprocessor': cf('#00d000'),
				'file-link': cf('#0000ff', useBold),
				'matching-brackets': cf('#00ffff', 'bold', '#303030'),
				
				'function': cf('#10b0ff', useBold),
				
				'side-effects-extern-function': cf('#ff8000', useBold),
				'no-side-effects-extern-function': cf('#10c0df', useBold),
				'ref-transparent-extern-function' : cf('#21ee20', useBold),
				
				'class-function': cf('#ffaa00', useBold),
				'class-getter': cf('#eeaa00', useBold),
				'class-setter': cf('#eeaa00', useBold),
				'class-operator': cf('#eeaa00', useBold),
				'class-iterator-type': cf('#eeaa00', useBold),
				'class-cast-definition': cf('#eeaa00', useBold),
				'class-name': cf('#ffdd44'),
				
				'local-module-import': cf('#dfaf00', useBold), #cf2000
				'project-module-import': cf('#378737', useBold),
				'global-module-import': cf('#efdf00', useBold),
				
				'module-browser-directory': QtGui.QBrush(QtGui.QColor("#999999")),
				'module-browser-module': QtGui.QBrush(QtGui.QColor("#e8e8e8")),
				
				'doc-modified' : QtGui.QColor("#ff7421"),
				'doc-unmodified' : QtGui.QColor("#000000"),
				'doc-selected' : QtGui.QColor("#eeeeee"),
				
				'error-line' : QtGui.QColor("#f74727"),
				'current-line' : QtGui.QColor("#303030"),
				
				'compile-log' : cf("#ffffff"),
				'benchmark' : cf("#ffffcc"),
				'program-output' : cf('#ffffcc'),
				'traceback' : cf("#ffffcc"),
				'compiler-error' : cf("#ff9000"),
				
				'internal-function' : cf('#a0c0ff', useBold),
				'internal-datatype' : cf('#ffdd44', useBold),
				'internal-main' : cf('#00ffff', useBold),
			},
		}
		
		if not useBold:
			self.themes['Default']['function'] = cf('#071777')
		
		self.config.theme = self.themes[self.config.themeName]
		
	def initCompiler(self):
		# Set up the environments we have
		self.fluaEnvironment = FluaEnvironment(getModuleDir(), self.actionEnvFlua)
		self.pythonEnvironment = PythonEnvironment(getPython3ModuleDir(), self.actionEnvPython)
		self.cppEnvironment = CPPEnvironment(getCPPModuleDir(), self.actionEnvCPP)
		self.glslEnvironment = GLSLEnvironment("", self.actionEnvGLSL)
		self.baseEnvironment = BaseEnvironment(self.actionEnvNone)
		
		self.environments = {
			self.fluaEnvironment,
			self.pythonEnvironment,
			self.cppEnvironment,
			self.glslEnvironment,
			self.baseEnvironment,
		}
		
		# This is used for pure text files
		self.setEnvironment(self.baseEnvironment)
		
		# Create file extension -> environment mapping
		self.fileExtensionToEnvironment = dict()
		for environment in self.environments:
			for ext in environment.fileExtensions:
				self.fileExtensionToEnvironment[ext] = environment
		
		# Create a compiler for Flua
		self.inputCompiler = BPCCompiler(getModuleDir(), ".flua")
		self.processor = BPPostProcessor(self.inputCompiler)
		self.processorOutFile = None
		
		# Threads
		self.outputCompilerThread = BPOutputCompilerThread(self)
		self.runThread = BPRunThread(self)
		
	def initToolBar(self):
		pass

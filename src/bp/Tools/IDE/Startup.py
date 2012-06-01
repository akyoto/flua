from bp.Tools.IDE.Threads import *
from bp.Tools.IDE.Utils import *
from bp.Tools.IDE.Editor import *
from bp.Tools.IDE.Widgets import *
from bp.Tools.IDE.MenuActions import *

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
		
		self.startBenchmark("Init Docks")
		self.initDockIcons()
		self.initDocks()
		self.endBenchmark()
		
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
	
	def initPreferences(self):
		self.preferences = uic.loadUi("ui/preferences.ui")
		self.preferences.settings.expandToDepth(0)
		self.preferences.settings.currentItemChanged.connect(self.onSettingsItemChange)
		
	def initUI(self):
		uic.loadUi(getIDERoot() + "ui/blitzprog-ide.ui", self)
		
		# StatusBar
		self.statusBar.setFont(QtGui.QFont("Ubuntu", 9))
		
		# Window
		#self.setWindowTitle("Blitzprog IDE")
		#self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.setGeometry(0, 0, 1000, 650)
		self.center()
		
		# Status bar
		self.lineNumberLabel = QtGui.QLabel()
		self.moduleInfoLabel = QtGui.QLabel()
		self.evalInfoLabel = QtGui.QLabel("")
		self.lineNumberLabel.setMinimumWidth(100)
		self.progressBar = QtGui.QProgressBar(self.statusBar)
		self.progressBar.setTextVisible(False)
		#self.progressBar.setMinimumWidth(100)
		self.progressBar.hide()
		
		#spacer1 = QtGui.QWidget(self.statusBar)
		#spacer1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#spacer2 = QtGui.QWidget(self.statusBar)
		#spacer2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		
		#self.statusBar.addPermanentWidget(spacer1)
		self.statusBar.addWidget(self.lineNumberLabel)
		self.statusBar.addWidget(self.moduleInfoLabel)
		self.statusBar.addWidget(self.evalInfoLabel)
		self.statusBar.addPermanentWidget(self.progressBar, 0)
		
		# Syntax switcher
		self.syntaxSwitcher = QtGui.QComboBox(self)
		self.syntaxSwitcher.setToolTip("Syntax switcher")
		self.syntaxSwitcher.addItem("BPC Syntax         ")
		self.syntaxSwitcher.addItem("C++ Light          ")
		self.syntaxSwitcher.addItem("Almost Ruby        ")
		self.syntaxSwitcher.currentIndexChanged.connect(self.switchSyntax)
		self.statusBar.addPermanentWidget(self.syntaxSwitcher, 0)
		
		# Search
		self.searchEdit = BPSearchEdit(self)
		self.replaceEdit = BPReplaceEdit(self)
		self.statusBar.addPermanentWidget(self.searchEdit, 1)
		self.statusBar.addPermanentWidget(self.replaceEdit, 1)
		
		# Target switching
		self.targetSwitcher = QtGui.QComboBox(self)
		self.targetSwitcher.setToolTip("Target language")
		self.targetSwitcher.addItem("C++")
		self.targetSwitcher.addItem("Python 3 (in development)")
		
		self.statusBar.addPermanentWidget(self.targetSwitcher, 0)
		
		# Workspaces view
		self.workspacesView = BPWorkspacesView(self)
		self.statusBar.addPermanentWidget(self.workspacesView, 0)
		
		#self.statusBar.setLayout(hBoxLayout)
		
		self.codeEdit = None
		
		#self.statusBar.hide()
		self.toolBar.hide()
		#self.syntaxSwitcherBar.hide()
		
	def initDockIcons(self):
		defaultIcon = QtGui.QIcon("images/icons/categories/applications-other.png")
		self.dockIcons = {
			"Modules" : None,
			"Outline" : None,
			"XML" : None,
			"Files": None,
			"Meta data": None,
			"Dependencies": None,
			"Scribble": None,
			"Console" : None
		}
		
		for iconName in self.dockIcons.keys():
			self.dockIcons[iconName] = QtGui.QIcon("images/icons/docks/%s.png" % normalizeName(iconName).lower())
		
	def initDocks(self):
		# Console
		self.console = BPConsoleWidget(self)
		
		# XML view
		self.xmlView = XMLCodeEdit(self)
		self.xmlView.setReadOnly(1)
		
		# Dependency view
		self.dependencyView = BPDependencyView(self)
		self.dependencyView.setReadOnly(1)
		
		# File view
		#self.fileView = BPFileBrowser(self, getModuleDir())
		
		# Module view
		self.moduleView = BPModuleBrowser(self, getModuleDir())
		
		# Scribble - I absolutely love this feature in Geany!
		# It's always the little things that are awesome :)
		self.scribble = BPScribbleWidget(self, getIDERoot() + "miscellaneous/scribble.txt")
		
		# Chat
		#self.chatWidget = BPChatWidget(self)
		
		# Outline
		self.outlineView = BPOutlineView(self)
		
		# Meta data
		self.metaData = BPMetaDataWidget(self)
		
		#self.workspacesViewDock = self.createDockWidget("Workspaces", self.workspacesView, QtCore.Qt.LeftDockWidgetArea)
		#self.fileViewDock = self.createDockWidget("Files", self.fileView, QtCore.Qt.RightDockWidgetArea)
		#self.chatViewDock = self.createDockWidget("Chat", self.chatWidget, QtCore.Qt.BottomDockWidgetArea)
		#self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.LeftDockWidgetArea)
		
		self.moduleViewDock = self.createDockWidget("Modules", self.moduleView, QtCore.Qt.LeftDockWidgetArea)
		self.consoleDock = self.createDockWidget("Console", self.console, QtCore.Qt.BottomDockWidgetArea)
		self.outlineViewDock = self.createDockWidget("Outline", self.outlineView, QtCore.Qt.RightDockWidgetArea)
		self.metaDataViewDock = self.createDockWidget("Meta data", self.metaData, QtCore.Qt.RightDockWidgetArea)
		self.dependenciesViewDock = self.createDockWidget("Dependencies", self.dependencyView, QtCore.Qt.RightDockWidgetArea)
		self.scribbleDock = self.createDockWidget("Scribble", self.scribble, QtCore.Qt.BottomDockWidgetArea)
		self.xmlViewDock = self.createDockWidget("XML", self.xmlView, QtCore.Qt.RightDockWidgetArea)
		
		self.outlineViewDock.hide()
		self.metaDataViewDock.hide()
		self.scribbleDock.hide()
		
		#self.msgViewDock.hide()
		#self.fileViewDock.hide()
		#self.xmlViewDock.show()
		
		
		if not self.developerFlag:
			self.dependenciesViewDock.hide()
			self.xmlViewDock.hide()
			self.consoleDock.hide()
		
		# Needed for workspaces
		self.viewsInitialized = True
		
	def initActions(self):
		# File
		self.actionNew.triggered.connect(self.newFile)
		self.actionOpen.triggered.connect(self.openFile)
		self.actionSave.triggered.connect(self.saveFile)
		self.actionSaveAs.triggered.connect(self.saveAsFile)
		self.actionClose.triggered.connect(self.closeCurrentTab)
		self.actionReopenLastFile.triggered.connect(self.reopenLastFile)
		self.actionExit.triggered.connect(self.close)
		
		# Edit
		self.actionUndo.triggered.connect(self.undoLastAction)
		self.actionRedo.triggered.connect(self.redoLastAction)
		self.actionSearch.triggered.connect(self.showSearch)
		self.actionRegExSearch.triggered.connect(self.showRegexSearch)
		self.actionCopy.triggered.connect(self.copy)
		self.actionCut.triggered.connect(self.cut)
		self.actionPaste.triggered.connect(self.paste)
		self.actionPreferences.triggered.connect(self.showPreferences)
		
		# Module
		self.actionRun.triggered.connect(self.onRunModule)
		self.actionRunOptimized.triggered.connect(self.runModuleOptimized)
		self.actionRunProfiler.triggered.connect(self.runProfiler)
		self.actionRunModuleTest.triggered.connect(self.runModuleTest)
		self.actionCleanAllTargets.triggered.connect(self.cleanAllTargets)
		self.actionProperties.triggered.connect(self.showModuleProperties)
		
		# Repositories
		self.actionRepositoryList.triggered.connect(self.showRepositoryList)
		self.actionConnectWithGitHub.triggered.connect(self.connectWithGitHub)
		
		# Window
		self.actionToggleFullscreen.triggered.connect(self.toggleFullScreen)
		
		# Help
		self.actionIntroduction.triggered.connect(self.showIntroduction)
		self.actionChangeLog.triggered.connect(self.showChangeLog)
		self.actionResetLocalChanges.triggered.connect(self.resetLocalChanges)
		self.actionResetLocalFileChanges.triggered.connect(self.resetLocalFileChanges)
		self.actionDownloadUpdates.triggered.connect(self.downloadUpdates)
		self.actionReportBug.triggered.connect(self.reportBug)
		self.actionThanksTo.triggered.connect(self.thanksTo)
		self.actionAbout.triggered.connect(self.about)
		
		# FAQ
		self.actionFAQUpdate.triggered.connect(self.faqUpdate)
		self.actionFAQCompiling.triggered.connect(self.faqCompiling)
		
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
		]
		
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
				'file-link': cf('#0000ff', 'bold'),
				
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
				'current-line' : None#QtGui.QColor("#fefefe")
			},
			
			# Dark theme
			"Dark": {
				'default': cf("#eeeeee"),
				'default-background': "#272727",
				'keyword': cf('#eeccaa'),
				'operator': cf('#aaaaaa'),
				'brace': cf('darkGray'),
				'comma': cf('#acacac'),
				'output-target': cf('#aa9988'),
				'include-file': cf('#aa9988'),
				'string': cf('#10e010'),
				'string2': cf('darkMagenta'),
				'comment': cf('#ffff99'),
				'disabled': cf('#cccccc', 'italic'),
				'self': cf('#cccccc'),
				'number': cf('#ff6020'),
				'hex-number': cf('brown'),
				'preprocessor': cf('#00d000'),
				'file-link': cf('#0000ff', 'bold'),
				
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
				'class-name': cf('#ffffff'),
				
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
			},
		}
		
		if not useBold:
			self.themes['Default']['function'] = cf('#071777')
		
		self.config.theme = self.themes[self.config.themeName]
		
	def initCompiler(self):
		self.postProcessorThread = None
		self.inputCompiler = BPCCompiler(getModuleDir(), ".bp")
		self.processor = BPPostProcessor(self.inputCompiler)
		self.processorOutFile = None
		self.postProcessorThread = BPPostProcessorThread(self)
		self.outputCompilerThread = BPOutputCompilerThread(self)
		
	def initToolBar(self):
		pass

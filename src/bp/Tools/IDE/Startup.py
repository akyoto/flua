from bp.Tools.IDE.Threads import *
from bp.Tools.IDE.Utils import *
from bp.Tools.IDE.Editor import *
from bp.Tools.IDE.Widgets import *
from bp.Tools.IDE.MenuActions import *

class Startup:
	
	def initAll(self):
		self.startBenchmark("Init UI")
		self.initUI()
		self.endBenchmark()
		
		self.setCurrentWorkspace(0)
		
		self.startBenchmark("Init Theme")
		self.initTheme()
		self.endBenchmark()
		
		self.startBenchmark("Init Toolbar")
		self.initToolBar()
		self.endBenchmark()
		
		self.startBenchmark("Init Docks")
		self.initDocks()
		self.endBenchmark()
		
		self.startBenchmark("Init Compiler")
		self.initCompiler()
		self.endBenchmark()
		
		self.startBenchmark("Init Preferences")
		self.initPreferences()
		self.endBenchmark()
		
		self.startBenchmark("Init Actions")
		self.initActions()
		self.endBenchmark()
		
	def showIntroduction(self):
		# For beginners
		self.newFile()
		self.codeEdit.disableUpdatesFlag = True
		self.codeEdit.setPlainText('''# Press F5 to run this
print "Hello bp!"

# You are using BPC syntax at the moment.
# It's pretty similar to Python:
if 1 + 1 == 2
	print "I'm a genius!"
else
	print "Something's wrong here..."

# A function starts with a lowercase letter (this will be changeable in the settings later):
myFunction x, y
	return x + y

# Call the function:
a = myFunction(5, 5)

# By using type inference the compiler knows 'a' is an integer.

# Classes start with an uppercase letter (will be changeable)
# and must contain an init function as a constructor:
MyClass
	init self.message
		print self.message
		
	doSomething
		print "By the way I heard Unicode works: おはようございます。"

# Creating objects:
b = MyClass("Hey it's b here! Long time no see.")

# Calling methods (whether brackets are optional or not depends on the syntax module):
b.doSomething()

# The current version is not stable.
# If you find a bug you can either tell me about it on IRC (#blitzprog on irc.freenode.net)
# or wait until I setup a bug tracker. Settings and preferences currently aren't saved and
# in some cases aren't even used.
# There are still lots of features missing but they'll be implemented sooner or later.

# Happy alpha testing :)
			''')
		self.codeEdit.disableUpdatesFlag = False
		self.codeEdit.runUpdater()
	
	def initPreferences(self):
		self.preferences = uic.loadUi("ui/preferences.ui")
		self.preferences.settings.expandToDepth(0)
		self.preferences.settings.currentItemChanged.connect(self.onSettingsItemChange)
		
	def initUI(self):
		uic.loadUi("ui/blitzprog-ide.ui", self)
		
		# StatusBar
		self.statusBar.setFont(QtGui.QFont("SansSerif", 8))
		
		# Window
		#self.setWindowTitle("Blitzprog IDE")
		#self.setWindowIcon(QtGui.QIcon("images/bp.png"))
		self.setGeometry(0, 0, 1000, 650)
		self.center()
		
		# Status bar
		self.lineNumberLabel = QtGui.QLabel()
		self.moduleInfoLabel = QtGui.QLabel()
		self.evalInfoLabel = QtGui.QLabel(" Reserved")
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
		
		# Workspaces view
		self.workspacesView = BPWorkspacesView(self)
		self.statusBar.addPermanentWidget(self.workspacesView, 0)
		
		#self.statusBar.setLayout(hBoxLayout)
		
		self.codeEdit = None
		
		#self.statusBar.hide()
		self.toolBar.hide()
		self.syntaxSwitcherBar.hide()
		
	def initDocks(self):
		# Console
		self.console = BPConsoleWidget(self)
		
		# Message view
		self.msgView = BPMessageView(self)
		
		# XML view
		self.xmlView = XMLCodeEdit(self)
		self.xmlView.setReadOnly(1)
		
		# Dependency view
		self.dependencyView = BPDependencyView(self)
		self.dependencyView.setReadOnly(1)
		
		# File view
		self.fileView = BPFileBrowser(self, getModuleDir())
		
		# Module view
		self.moduleView = BPModuleBrowser(self, getModuleDir())
		
		# Scribble - I absolutely love this feature in Geany!
		# It's always the little things that are awesome :)
		self.scribble = BPScribbleWidget(self, "miscellaneous/scribble.txt")
		
		# IntelliView enabled?
		if self.intelliEnabled:
			# IntelliView
			self.intelliView = BPIntelliView(self)
			
			# IntelliView Dock
			self.intelliView.addIntelligentWidget(self.msgView)
			self.intelliView.addIntelligentWidget(self.dependencyView)
			#self.intelliView.addIntelligentWidget(self.xmlView)
			self.intelliView.vBox.addStretch(1)
			self.intelliViewDock = self.createDockWidget("IntelliView", self.intelliView, QtCore.Qt.RightDockWidgetArea)
		else:
			self.moduleViewDock = self.createDockWidget("Modules", self.moduleView, QtCore.Qt.LeftDockWidgetArea)
			
			#self.workspacesViewDock = self.createDockWidget("Workspaces", self.workspacesView, QtCore.Qt.LeftDockWidgetArea)
			
			self.dependenciesViewDock = self.createDockWidget("Dependencies", self.dependencyView, QtCore.Qt.RightDockWidgetArea)
			self.xmlViewDock = self.createDockWidget("XML", self.xmlView, QtCore.Qt.RightDockWidgetArea)
			self.fileViewDock = self.createDockWidget("Files", self.fileView, QtCore.Qt.RightDockWidgetArea)
			
			self.msgViewDock = self.createDockWidget("Messages", self.msgView, QtCore.Qt.BottomDockWidgetArea)
			self.consoleDock = self.createDockWidget("Console", self.console, QtCore.Qt.BottomDockWidgetArea)
			
			self.scribbleDock = self.createDockWidget("Scribble", self.scribble, QtCore.Qt.BottomDockWidgetArea)
			
		#self.dependenciesViewDock.hide()
		#self.xmlViewDock.hide()
		self.scribbleDock.hide()
		self.fileViewDock.hide()
		#self.consoleDock.hide()
		
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
		self.actionCopy.triggered.connect(self.codeEdit.copy)
		self.actionCut.triggered.connect(self.codeEdit.cut)
		self.actionPaste.triggered.connect(self.codeEdit.paste)
		self.actionPreferences.triggered.connect(self.preferences.show)
		
		# Module
		self.actionRun.triggered.connect(self.runModule)
		self.actionProperties.triggered.connect(self.showModuleProperties)
		
		# Help
		self.actionIntroduction.triggered.connect(self.showIntroduction)
		self.actionDownloadUpdates.triggered.connect(self.downloadUpdates)
		self.actionThanksTo.triggered.connect(self.thanksTo)
		self.actionAbout.triggered.connect(self.about)
		
	def initTheme(self):
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
				'comment': cf('darkGray', 'italic'),
				'self': cf('#373737', 'italic'),
				'number': cf('brown'),
				'hex-number': cf('brown'),
				'own-function': cf('#171717', 'bold'),
				'local-module-import': cf('#661166', 'bold'),
				'project-module-import': cf('#378737', 'bold'),
				'global-module-import': cf('#373737', 'bold'),
				'current-line' : None#QtGui.QColor("#fefefe")
			},
			
			"Orange": {
				'default': cf("#eeeeee"),
				'default-background': "#272727",
				'keyword': cf('orange'),
				'operator': cf('#ff2010'),
				'brace': cf('darkGray'),
				'comma': cf('#777777'),
				'output-target': cf('#888888'),
				'include-file': cf('#888888'),
				'string': cf('#00c000'),
				'string2': cf('darkMagenta'),
				'comment': cf('lightGray', 'italic'),
				'self': cf('#eeeeee', 'italic'),
				'number': cf('#00cccc'),
				'hex-number': cf('brown'),
				'own-function': cf('#ff8000', 'bold'),
				'local-module-import': cf('#77ee77', 'bold'),
				'project-module-import': cf('#dddddd', 'bold'),
				'global-module-import': cf('#22dd22', 'bold'),
				'current-line' : QtGui.QColor("#474747")
			},
		}
		
		self.config.theme = self.themes[self.config.themeName]
		
	def initCompiler(self):
		self.postProcessorThread = None
		self.bpc = BPCCompiler(getModuleDir(), ".bp")
		self.processor = BPPostProcessor()
		self.processorOutFile = None
		self.postProcessorThread = BPPostProcessorThread(self)
		self.newFile()
		
	def initToolBar(self):
		# Syntax switcher
		syntaxSwitcher = QtGui.QComboBox()
		syntaxSwitcher.addItem("BPC Syntax")
		syntaxSwitcher.addItem("C++/Java Syntax")
		syntaxSwitcher.addItem("Python Syntax")
		syntaxSwitcher.addItem("Ruby Syntax")
		
		spacerWidget = QtGui.QWidget()
		spacerWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		
		# Tool bar
		self.syntaxSwitcherBar.addSeparator()
		self.syntaxSwitcherBar.addWidget(spacerWidget)
		self.syntaxSwitcherBar.addWidget(syntaxSwitcher)
		self.syntaxSwitcherBar.addSeparator()

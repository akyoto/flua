import configparser
import codecs
import os
import gc
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from PyQt4 import QtGui, QtCore, uic

# Script path
configScriptPath = extractDir(os.path.realpath(__file__))

# Get IDE path
globalIDERoot = fixPath(os.path.abspath(configScriptPath + "../"))

# Get git path
if os.name == "nt":
	globalGitPath = fixPath(os.path.abspath(globalIDERoot + "../../../../../msysgit/bin/"))
else:
	globalGitPath = ""

def getIDERoot():
	global globalIDERoot
	return globalIDERoot

def getGitPath():
	if os.name == "nt":
		global globalGitPath
		return globalGitPath
	else:
		return ""

def getFindPath():
	if os.name == "nt":
		return getGitPath()
	else:
		return "/usr/bin/"
		
def getRmPath():
	if os.name == "nt":
		return getGitPath()
	else:
		return ""

def readFile(fileName):
	with open(fileName, "r") as f:
		return f.read()

class BPConfiguration:
	
	def __init__(self, bpIDE, fileName):
		self.bpIDE = bpIDE
		self.fileName = fileName
		self.parser = createConfigParser()
		
		self.darkStyleEnabled = False
		
		self.appStyleSheet = """
			#AutoCompleter {
				border: none;
				font-family: Ubuntu;
			}
			
			QPlainTextEdit, QTreeView, QListView {
				background-color: #ffffff;
				color: #272727;
				border-radius: 7px;
				border: 1px solid black;
			}
			
			QPlainTextEdit {
				border-top-left-radius: 0px;
				background-color: #ffffff;
			}
			
			#MessageView, #SearchResults {
				border-radius: 7px;
				color: rgba(0, 0, 0, 65%);
				background-color: rgba(255, 255, 255, 10%);
			}
			
			#Log, #Compiler, #Output {
				font-family: Ubuntu Mono;
				font-size: 11pt;
				border-radius: 0px;
			}
		""" #% (self.theme['default-background'])
		
		self.dialogStyleSheet = """
			QWidget {
				font-family: Ubuntu, Verdana; font-size: 12px;
			}
		"""
		
		self.darkStyleSheet = readFile(getIDERoot() + "themes/Dark/Dark.css")
		
		# Fonts
		if QtGui.QFontDatabase.addApplicationFont(getIDERoot() + "fonts/Ubuntu-R.ttf") == -1:
			print("Could not load Ubuntu font")
			
		if QtGui.QFontDatabase.addApplicationFont(getIDERoot() + "fonts/UbuntuMono-R.ttf") == -1:
			print("Could not load UbuntuMono font")
		
		self.loadSettings()
		
	def loadSettings(self):
		if os.name == "nt":
			ideConfig = "IDE:Windows"
			editorConfig = "Editor:Windows"
		else:
			ideConfig = "IDE"
			editorConfig = "Editor"
		
		self.gitHubName = "Unknown"
		
		with codecs.open(self.fileName, "r", "utf-8") as inStream:
			self.parser.readfp(inStream)
		
		self.gcMemoryThreshold = self.getInt("Application", "GCMemoryThreshold")
		self.developerMode = self.getBool("Application", "DeveloperMode")
		self.defaultEnvironmentName = self.get("Application", "DefaultEnvironment")
		
		self.updateInterval = self.getInt("Parser", "UpdateInterval")
		self.compilerUpdateInterval = self.getInt("Compiler", "UpdateInterval")
		
		self.autoSuggestionEnabled = self.getBool("AutoSuggestion", "Enabled")
		self.autoSuggestionMinChars = self.getInt("AutoSuggestion", "MinChars")
		self.autoSuggestionMinCompleteChars = self.getInt("AutoSuggestion", "MinCompleteChars")
		self.autoSuggestionMaxItemCount = self.getInt("AutoSuggestion", "MaxItemCount")
		
		self.editorFontFamily = self.get(editorConfig, "FontFamily")
		self.editorFontSize = self.getInt(editorConfig, "FontSize")
		self.tabWidth = self.getInt(editorConfig, "TabWidth")
		self.documentModeEnabled = self.getBool(editorConfig, "DocumentMode")
		self.useBold = self.getBool(editorConfig, "EnableBoldFormatting")
		self.enableDocBubbles = self.getBool(editorConfig, "EnableDocBubbles")
		self.bracketHighlightingEnabled = self.getBool(editorConfig, "EnableBracketHighlighting")
		
		self.themeName = self.get("Editor.Theme", "Theme")
		
		self.ideFontFamily = self.get(ideConfig, "FontFamily")
		self.ideFontSize = self.getInt(ideConfig, "FontSize")
		
		# Create fonts
		self.monospaceFont = QtGui.QFont(self.editorFontFamily, self.editorFontSize)
		self.standardFont = QtGui.QFont(self.ideFontFamily, self.ideFontSize)
		
	def get(self, category, option):
		return self.parser.get(category, option)
		
	def getInt(self, category, option):
		return self.parser.getint(category, option)
		
	def getBool(self, category, option):
		return self.parser.getboolean(category, option)
		
	def applySettings(self):
		# GC
		t = gc.get_threshold()
		multi = self.gcMemoryThreshold
		gc.set_threshold(int(t[0] * multi), int(t[1] * multi), int(t[2] * multi))
		
		# Fonts
		self.applyMonospaceFont(self.monospaceFont)
		self.applyStandardFont(self.standardFont)
		self.applyTheme(self.themeName)
		
		if os.name == "nt":
			self.applyMenuFont(self.standardFont)
		
	def saveSettings(self):
		studioConfig = getConfigDir() + "studio/"
		if not os.path.isdir(studioConfig):
			os.makedirs(studioConfig)
		
		with open(studioConfig + "settings.ini", "w") as configFileStream:
			self.parser.write(configFileStream)
		
	def applyTheme(self, themeName):
		if isinstance(themeName, str):
			self.themeName = themeName
			self.theme = self.bpIDE.themes[self.themeName]
		else:
			self.themeName = self.themeWidget.currentText()
			self.theme = self.bpIDE.themes[self.themeName]
		
		if not self.themeName in self.bpIDE.themes:
			return
		
		if self.themeName == "Dark":
			self.darkStyleEnabled = True
		else:
			self.darkStyleEnabled = False
		
		#codeEdit.setBackgroundColor(self.theme['default-background'])
		QtGui.QApplication.instance().setStyleSheet(self.appStyleSheet)
		
		if self.darkStyleEnabled:
			QtGui.QApplication.instance().setStyleSheet(self.darkStyleSheet)
			#QtGui.QApplication.instance().setStyleSheet(self.darkStyleSheet)
		
		# TODO: ...
		for workspace in self.bpIDE.workspaces:
			workspace.updateColors()
			for codeEdit in workspace.getCodeEditList():
				# Set current format
				defaultFormat = self.theme["default"]
				codeEdit.setCurrentCharFormat(defaultFormat)
				
				# Update the current view's format: YES WE NEED TO DO THIS!
				cursor = codeEdit.textCursor()
				cursor.select(QtGui.QTextCursor.Document)
				cursor.setCharFormat(defaultFormat)
				
				#codeEdit.setTextCursor(cursor)
				
				codeEdit.highlighter.rehighlight()
		
	def applyEditorFontFamily(self, font):
		self.editorFontFamily = font.family()
		self.monospaceFont.setFamily(self.editorFontFamily)
		self.applyMonospaceFont(self.monospaceFont)
		
	def applyEditorFontSize(self, value):
		self.editorFontSize = value
		self.monospaceFont.setPointSize(self.editorFontSize)
		self.applyMonospaceFont(self.monospaceFont)
		
	def applyMenuFont(self, font):
		self.bpIDE.mainMenuBar.setFont(font)
		for menuItem in self.bpIDE.mainMenuBar.children():
			menuItem.setFont(font)
		
	def applyMonospaceFont(self, font):
		self.monospaceFont = font
		
		# Widgets with monospace font
		for workspace in self.bpIDE.workspaces:
			for codeEdit in workspace.getCodeEditList():
				codeEdit.setFont(font)
				codeEdit.msgView.setFont(self.standardFont)
		
		self.bpIDE.xmlView.setFont(font)
		self.bpIDE.dependencyView.setFont(font)
		self.bpIDE.console.log.setFont(font)
		
	def applyStandardFont(self, font):
		self.standardFont = font
		
		QtGui.QToolTip.setFont(font)
		
		# Widgets with normal font
		self.bpIDE.workspacesContainer.setFont(font)
		
		if self.bpIDE.fileView:
			self.bpIDE.fileView.setFont(font)
		
		# All module views
		for env in self.bpIDE.environments:
			env.moduleView.setFont(font)
		
		# All docks
		for dock in self.bpIDE.docks:
			dock.setFont(font)
			
		self.bpIDE.searchResults.setFont(font)
		
	def applyTabWidth(self, value):
		self.tabWidth = value
		for workspace in self.bpIDE.workspaces:
			for codeEdit in workspace.getCodeEditList():
				codeEdit.setTabWidth(value)
		
	def initPreferencesWidget(self, uiFileName, widget):
		if uiFileName == "preferences/editor":
			widget.fontFamily.currentFontChanged.connect(self.applyEditorFontFamily)
			widget.fontSize.valueChanged.connect(self.applyEditorFontSize)
			widget.tabWidth.valueChanged.connect(self.applyTabWidth)
		elif uiFileName == "preferences/editor.theme":
			self.themeWidget.currentIndexChanged.connect(self.applyTheme)
			
	def updatePreferencesWidget(self, uiFileName, widget):
		if uiFileName == "preferences/editor":
			widget.fontFamily.setCurrentFont(self.monospaceFont)
			widget.fontSize.setValue(self.editorFontSize)
			widget.tabWidth.setValue(self.tabWidth)
		elif uiFileName == "preferences/editor.theme":
			self.themeWidget = widget.themeName
			self.themeWidget.setCurrentIndex(self.themeName == "Dark")
		elif uiFileName == "preferences/editor.performance":
			widget.parserInterval.setValue(self.updateInterval)
			widget.compilerInterval.setValue(self.compilerUpdateInterval)
			widget.gcMemThreshold.setValue(self.gcMemoryThreshold)
		elif uiFileName == "preferences/targets.c++":
			widget.compilerName.setText(getGCCCompilerName())
			widget.compilerPath.setText(getGCCCompilerPath())
			widget.compilerVersion.setText(getGCCCompilerVersion())
		elif uiFileName == "preferences/targets.python":
			widget.compilerName.setText(getPython3CompilerName())
			widget.compilerPath.setText(getPython3Path())
			widget.compilerVersion.setText(getPython3Version())

####################################################################
# Functions
####################################################################

# Creates a case sensitive config parser
def createConfigParser():
	parser = configparser.SafeConfigParser()
	
	# Make it case sensitive
	parser.optionxform = str
	
	return parser

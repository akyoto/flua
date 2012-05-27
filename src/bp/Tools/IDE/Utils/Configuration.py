import configparser
import codecs
import os
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from PyQt4 import QtGui, QtCore, uic

globalIDERoot = fixPath(os.path.abspath(extractDir(os.path.realpath(__file__)) + "../"))

if os.name == "nt":
	globalGitPath = fixPath(os.path.abspath("../msysgit/bin/"))
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

class BPConfiguration:
	
	def __init__(self, bpIDE, fileName):
		self.bpIDE = bpIDE
		self.fileName = fileName
		self.parser = configparser.SafeConfigParser()
		
		self.darkStyleEnabled = False
		
		self.appStyleSheet = """
			QPlainTextEdit { background-color: #ffffff; }
			#AutoCompleter {
				border: none;
				font-family: Ubuntu;
			}
		""" #% (self.theme['default-background'])
		
		self.dialogStyleSheet = """
			QWidget {
				font-family: Ubuntu, Verdana; font-size: 12px;
			}
		"""
		
		self.darkStyleSheet = """
			/*QDockWidget QWidget {
				background-color: #272727;
				color: #eeeeee;
			}*/
			
			QPlainTextEdit, QTreeView, QListView {
				background-color: #272727;
				border-radius: 7px;
				color: #eeeeee;
			}
			
			QPlainTextEdit {
				border-top-left-radius: 0px;
			}
			
			QTabBar::tab {
				background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 rgba(84, 84, 84, 32), stop:1 rgba(39, 39, 39, 48));
				border-top-left-radius: 6px;
				border-top-right-radius: 6px;
				padding: 3px;
				padding-left: 5px;
				padding-right: 0px;
			}
			
			QTabBar::tab:hover {
				background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 rgba(84, 84, 84, 164), stop:1 rgba(39, 39, 39, 172));
			}
			
			QTabBar::tab:selected {
				background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 rgba(84, 84, 84, 255), stop:1 rgba(39, 39, 39, 255));
			}
			
			#Log {
				margin-right: 16px;
				border-radius: 7px;
				font-size: 10pt;
			}
			
			QStatusBar, QLabel, QLineEdit, QComboBox {
				font-size: 9pt;
			}
"""

# QTabWidget::tab-bar {

 # }

 # QTabBar::tab {
  # background: #000000;
  # color: #ffffff;
  # padding: 7px;
  # padding-top: 4px;
  # padding-bottom: 4px;
  # border-top-right-radius: 7px 14px;
  # border-top-left-radius: 7px 14px;
 # }

 # QTabBar::tab:selected {
  # background: #888888;
 # }
		
		# Fonts
		if QtGui.QFontDatabase.addApplicationFont(getIDERoot() + "fonts/Ubuntu-R.ttf") == -1:
			print("Could not load Ubuntu font")
			
		if QtGui.QFontDatabase.addApplicationFont(getIDERoot() + "fonts/UbuntuMono-R.ttf") == -1:
			print("Could not load UbuntuMono font")
		
		self.loadSettings()
		
	def loadSettings(self):
		with codecs.open(self.fileName, "r", "utf-8") as inStream:
			self.parser.readfp(inStream)
		
		if os.name == "nt":
			ideConfig = "IDE:Windows"
			editorConfig = "Editor:Windows"
		else:
			ideConfig = "IDE"
			editorConfig = "Editor"
		
		self.editorFontFamily = self.parser.get(editorConfig, "FontFamily")
		self.editorFontSize = self.parser.getint(editorConfig, "FontSize")
		self.tabWidth = self.parser.getint(editorConfig, "TabWidth")
		self.documentModeEnabled = self.parser.getboolean(editorConfig, "DocumentMode")
		self.useBold = self.parser.getboolean(editorConfig, "EnableBoldFormatting")
		
		self.themeName = self.parser.get("Editor.Theme", "Theme")
		
		self.ideFontFamily = self.parser.get(ideConfig, "FontFamily")
		self.ideFontSize = self.parser.getint(ideConfig, "FontSize")
		
		self.updateInterval = self.parser.getint("Parser", "UpdateInterval")
		
		self.monospaceFont = QtGui.QFont(self.editorFontFamily, self.editorFontSize)
		self.standardFont = QtGui.QFont(self.ideFontFamily, self.ideFontSize)
		
	def applySettings(self):
		self.applyMonospaceFont(self.monospaceFont)
		self.applyStandardFont(self.standardFont)
		self.applyTheme(self.themeName)
		
		if os.name == "nt":
			self.applyMenuFont(self.standardFont)
		
	def saveSettings(self):
		pass
		#with open(getIDERoot() + "settings.ini", "wb") as configFileStream:
		#	self.parser.write(configFileStream)
		
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
		
		# TODO: ...
		for workspace in self.bpIDE.workspaces:
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
		self.bpIDE.menuBar.setFont(font)
		for menuItem in self.bpIDE.menuBar.children():
			menuItem.setFont(font)
		
	def applyMonospaceFont(self, font):
		# Widgets with monospace font
		for workspace in self.bpIDE.workspaces:
			for codeEdit in workspace.getCodeEditList():
				codeEdit.setFont(font)
		
		self.bpIDE.xmlView.setFont(font)
		self.bpIDE.dependencyView.setFont(font)
		self.bpIDE.console.log.setFont(font)
		
	def applyStandardFont(self, font):
		QtGui.QToolTip.setFont(font)
		
		# Widgets with normal font
		self.bpIDE.moduleView.setFont(font)
		self.bpIDE.msgView.setFont(font)
		self.bpIDE.workspacesContainer.setFont(font)
		
		# All docks
		for dock in self.bpIDE.docks:
			dock.setFont(font)
		
	def applyTabWidth(self, value):
		self.tabWidth = valued
		for workspace in self.bpIDE.workspaces:
			for codeEdit in workspace.getCodeEditList():
				codeEdit.setTabWidth(value)
		
	def initPreferencesWidget(self, uiFileName, widget):
		if uiFileName == "preferences/editor":
			widget.fontFamily.setCurrentFont(self.monospaceFont)
			widget.fontSize.setValue(self.editorFontSize)
			widget.tabWidth.setValue(self.tabWidth)
			
			#widget.fontFamily.connect()
			widget.fontFamily.currentFontChanged.connect(self.applyEditorFontFamily)
			widget.fontSize.valueChanged.connect(self.applyEditorFontSize)
			widget.tabWidth.valueChanged.connect(self.applyTabWidth)
		elif uiFileName == "preferences/editor.theme":
			self.themeWidget = widget.themeName
			self.themeWidget.setCurrentIndex(self.themeName == "Dark")
			self.themeWidget.currentIndexChanged.connect(self.applyTheme)
		elif uiFileName == "preferences/targets.c++":
			widget.compilerName.setText(getGCCCompilerName())
			widget.compilerPath.setText(getGCCCompilerPath())
			widget.compilerVersion.setText(getGCCCompilerVersion())
			#self.themeWidget = widget.themeName
			#self.themeWidget.currentIndexChanged.connect(self.applyTheme)

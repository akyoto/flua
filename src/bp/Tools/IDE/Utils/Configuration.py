import configparser
import codecs
import os
from bp.Compiler.Utils import *
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
	return ""

class BPConfiguration:
	
	def __init__(self, bpIDE, fileName):
		self.bpIDE = bpIDE
		self.fileName = fileName
		self.parser = configparser.SafeConfigParser()
		
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
		
		self.monospaceFont = QtGui.QFont(self.editorFontFamily, self.editorFontSize)
		self.standardFont = QtGui.QFont(self.ideFontFamily, self.ideFontSize)
		
	def applySettings(self):
		self.applyMonospaceFont(self.monospaceFont)
		self.applyStandardFont(self.standardFont)
		self.applyTheme(self.themeName)
		
		if os.name == "nt":
			self.applyMenuFont(self.standardFont)
		
	def applyTheme(self, themeName):
		if not themeName in self.bpIDE.themes:
			return
		
		if isinstance(themeName, str):
			self.themeName = themeName
			self.theme = self.bpIDE.themes[self.themeName]
		else:
			self.themeName = self.themeWidget.currentText()
			self.theme = self.bpIDE.themes[self.themeName]
		
		self.dialogStyleSheet = """
			QWidget {
				font-family: Ubuntu, Verdana; font-size: 12px;
			}
		"""
		
		#codeEdit.setBackgroundColor(self.theme['default-background'])
		QtGui.QApplication.instance().setStyleSheet("""
			QPlainTextEdit { background-color: %s; }
		""" % (self.theme['default-background']))
		
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
			self.themeWidget.currentIndexChanged.connect(self.applyTheme)

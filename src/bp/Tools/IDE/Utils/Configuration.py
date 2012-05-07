import configparser
import codecs
import os
from PyQt4 import QtGui, QtCore, uic

class BPConfiguration:
	
	def __init__(self, bpIDE, fileName):
		self.bpIDE = bpIDE
		self.fileName = fileName
		self.parser = configparser.SafeConfigParser()
		
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
		
		self.themeName = self.parser.get("Editor.Theme", "Theme")
		self.theme = self.bpIDE.themes[self.themeName]
		
		self.ideFontFamily = self.parser.get(ideConfig, "FontFamily")
		self.ideFontSize = self.parser.getint(ideConfig, "FontSize")
		
		self.monospaceFont = QtGui.QFont(self.editorFontFamily, self.editorFontSize)
		self.standardFont = QtGui.QFont(self.ideFontFamily, self.ideFontSize)
		
	def applySettings(self):
		self.applyMonospaceFont(self.monospaceFont)
		self.applyStandardFont(self.standardFont)
		self.applyTheme(self.themeName)
		
	def applyTheme(self, themeName):
		if isinstance(themeName, str):
			self.themeName = themeName
			self.theme = self.bpIDE.themes[self.themeName]
		else:
			self.themeName = self.themeWidget.currentText()
			self.theme = self.bpIDE.themes[self.themeName]
		
		#codeEdit.setBackgroundColor(self.theme['default-background'])
		QtGui.QApplication.instance().setStyleSheet("QPlainTextEdit { background-color: %s; }" % (self.theme['default-background']))
		
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
			widget.fontSize.setValue(self.ideFontSize)
			widget.tabWidth.setValue(self.tabWidth)
			
			#widget.fontFamily.connect()
			widget.fontFamily.currentFontChanged.connect(self.applyEditorFontFamily)
			widget.fontSize.valueChanged.connect(self.applyEditorFontSize)
			widget.tabWidth.valueChanged.connect(self.applyTabWidth)
		elif uiFileName == "preferences/editor.theme":
			self.themeWidget = widget.themeName
			self.themeWidget.currentIndexChanged.connect(self.applyTheme)

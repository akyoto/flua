from PyQt4 import QtGui, QtCore
from bp.Tools.IDE.Utils import *

class CLogHighlighter(QtGui.QSyntaxHighlighter):
	"""Syntax highlighter for the Changelog and the console.
	"""
	
	def __init__(self, document, bpIDE):
		QtGui.QSyntaxHighlighter.__init__(self, document)
		self.bpIDE = bpIDE
		#self.updateCharFormatFlag = False
	
	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		style = self.bpIDE.getCurrentTheme()
		
		if text.startswith("        "):
			self.setFormat(0, len(text), style['comment'])

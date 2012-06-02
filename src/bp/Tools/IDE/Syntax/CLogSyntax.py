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
		
		if text.startswith("Traceback (most recent call last):"):
			self.setCurrentBlockState(2)
			self.setFormat(0, len(text), style['traceback'])
			return
			
		if self.previousBlockState() == 2 and text:
			if text[0].isspace():
				self.setCurrentBlockState(2)
			self.setFormat(0, len(text), style['traceback'])
			return
		
		if self.previousBlockState() == 1 and self.bpIDE.running:
			self.setCurrentBlockState(1)
			if not text.startswith("---") and not text.startswith("Executing:"):
				self.setFormat(0, len(text), style['program-output'])
				return
		
		if text.startswith("        ") and len(text) > 8 and text[8].isalnum():
			self.setFormat(0, len(text), style['comment']) # Changelog message
		elif text.endswith("ms"):
			self.setFormat(0, len(text), style['benchmark'])
		elif text.startswith("Executing:") and self.currentBlockState() != 1:
			self.setCurrentBlockState(1)
			return
		else:
			self.setFormat(0, len(text), style['compile-log'])

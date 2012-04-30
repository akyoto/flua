# This syntax module was based on Eric Pierce's syntax highlighter for Python:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
# I reimplemented the highlightBlock function to not depend on RegEx evaluation
# which is a lot faster.

from PyQt4 import QtGui, QtCore
from bp.Tools.IDE import *
from bp.Compiler.Utils import *

class BPCHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Syntax highlighter for the BPC language.
	"""
	# Python keywords
	keywords = {
		'and', 'not', 'or', 'assert', 'break', 'class', 'continue',
		'elif', 'else',
		'for', 'from', 'to', 'until', 'if', 'import', 'in',
		'switch', 'case', 'target', 'compilerflags', 'get', 'set', 'operator', 'extern', 'include',
		'template', 'const',
		'return', 'try', 'throw', 'catch', 'while', 
		'target', 'include', 'private',
		'null', 'true', 'false',
	}
	
	# BPC operators
	operators = {
		'=',
		# Comparison
		'==', '!=', '<', '<=', '>', '>=',
		# Arithmetic
		'\+', '-', '\*', '/', '//', '\%', '\*\*',
		# In-place
		'\+=', '-=', '\*=', '/=', '\%=',
		# Bitwise
		'\^', '\|', '\&', '\~', '>>', '<<',
		# Data Flow
		'<-', '->', '<--', '-->' ,
		# Type declaration
		':',
	}

	# BPC braces
	braces = {
		'(', ')', '[', ']', '{', '}',
	}
	
	def __init__(self, document, bpIDE):
		QtGui.QSyntaxHighlighter.__init__(self, document)
		self.bpIDE = bpIDE
		self.style = bpIDE.getCurrentTheme()

	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		if not text:
			return
		
		# Do other syntax formatting
		#self.startBenchmark("Syntax Highlight")
		#for expression, nth, style in self.rules:
			#index = expression.indexIn(text, 0)
			
			#while index >= 0:
				## We actually want the index of the nth match
				#index = expression.pos(nth)
				#length = len(expression.cap(nth))
				#self.setFormat(index, length, style)
				#index = expression.indexIn(text, index + length)
		style = self.style
		
		i = 0
		text += " "
		textLen = len(text)
		while i < textLen:
			char = text[i]
			if char.isalpha():
				h = i + 1
				while h < textLen and text[h].isalnum():
					h += 1
				expr = text[i:h]
				
				if expr in BPCHighlighter.keywords:
					self.setFormat(i, h - i, style['keyword'])
				elif expr in self.bpIDE.processor.dTreeByFunctionName:
					self.setFormat(i, h - i, style['own-function'])
				
				i = h - 1
			elif char.isdigit():
				h = i + 1
				while h < textLen and text[h].isdigit():
					h += 1
				if (i == 0 or not text[i - 1].isalpha()) and not text[h].isalpha():
					self.setFormat(i, h - i, style['numbers'])
				#else:
				#	
				i = h - 1
			elif char == '"':
				h = i + 1
				while h < textLen and text[h] != '"':
					h += 1
				self.setFormat(i, h - i + 1, style['string'])
				i = h
			elif char == '#':
				self.setFormat(i, textLen - i, style['comment'])
				return
			elif char == ',':
				self.setFormat(i, 1, style['comma'])
			elif char in '+-*/=<>%&|:!\\~':
				#h = i + 1
				#while h < textLen and text[h]:
				#	h += 1
				self.setFormat(i, 1, style['operator'])
				#i = h
			elif char in BPCHighlighter.braces:
				self.setFormat(i, 1, style['brace'])
				
			i += 1
		#self.endBenchmark()
		
		self.setCurrentBlockState(0)

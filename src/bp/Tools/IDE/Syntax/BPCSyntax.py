# This syntax module was based on Eric Pierce's syntax highlighter for Python:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
# I reimplemented the highlightBlock function to not depend on RegEx evaluation
# which is a lot faster.

from PyQt4 import QtGui, QtCore
from bp.Tools.IDE import *
from bp.Compiler.Utils import *
from bp.Compiler.Config import *

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
		
		# TODO: Remove
		'require', 'ensure', 'maybe', 'test'
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
		#self.updateCharFormatFlag = False

	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		if not text or self.bpIDE.codeEdit.disableUpdatesFlag:
			return
		
		style = self.bpIDE.getCurrentTheme()
		
		i = 0
		text += " "
		textLen = len(text)
		#print("HIGHLIGHTING >%s< OF LENGTH %d" % (text, textLen))
		#if self.updateCharFormatFlag:
		#	self.setFormat(0, textLen, style['default'])
		
		while i < textLen:
			char = text[i]
			if char.isalpha() or char == '_':
				h = i + 1
				while h < textLen and (text[h].isalnum() or text[h] == '_'):
					h += 1
				expr = text[i:h]
				
				if expr in BPCHighlighter.keywords:
					self.setFormat(i, h - i, style['keyword'])
					if expr == "target":
						j = h + 1
						while j < textLen and not text[j].isspace():
							j += 1
						self.setFormat(h, j - h, style['output-target'])
						h = j
					elif expr == "import":
						j = h + 1
						while j < textLen and not text[j].isspace():
							j += 1
						importedModule = text[h+1:j]
						importType = self.bpIDE.getModuleImportType(importedModule)
						if importType == 1 or importType == 2:
							self.setFormat(h, j - h, style['local-module-import'])
						elif importType == 3 or importType == 4:
							self.setFormat(h, j - h, style['project-module-import'])
						elif importType == 5 or importType == 6:
							self.setFormat(h, j - h, style['global-module-import'])
						h = j
				elif expr == "my":
					self.setFormat(i, h - i, style['self'])
				elif self.bpIDE.processor.getFirstDTreeByFunctionName(expr):
					self.setFormat(i, h - i, style['own-function'])
				i = h - 1
			elif char.isdigit():
				h = i + 1
				while h < textLen and text[h].isdigit():
					h += 1
				if (i == 0 or not text[i - 1].isalpha()) and not text[h].isalpha():
					self.setFormat(i, h - i, style['number'])
				elif text[i] == '0' and text[h] == 'x':
					h += 1
					while h < textLen and (text[h].isdigit() or text[h] in "ABCDEFabcdef"):
						h += 1
					self.setFormat(i, h - i, style['hex-number'])
				#else:
				#	
				i = h - 1
			elif char == '"':
				h = i + 1
				while h < textLen and text[h] != '"':
					h += 1
				
				# TODO: WHY IS THIS CALL SO BUGGY ON WINDOWS?!
				if h < textLen - 1 and text[h] == '"':
					self.setFormat(i, h - i + 1, style['string'])
				
				#print(i, h - i, style['string'])
				#if h < textLen - 1:
				#	if text[h] == '"':
				#		self.setFormat(i, h - i + 1, style['string'])
				#	else:
				#		self.setFormat(i, h - i, style['string'])
				#else:
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
		
		#self.setCurrentBlockState(0)

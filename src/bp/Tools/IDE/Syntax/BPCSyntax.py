# This syntax module was based on Eric Pierce's syntax highlighter for Python:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
# I reimplemented the highlightBlock function to not depend on RegEx evaluation
# which is a lot faster.

from PyQt4 import QtGui, QtCore
from bp.Tools.IDE import *
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from bp.Compiler.Input.bpc import *

class BPCHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Syntax highlighter for the BPC language.
	"""
	# Python keywords
	keywords = [{}] * 97 + [
		{'and', 'assert'},
		{'break'},
		{'class', 'continue', 'const', 'case', 'catch', 'compilerflags'},
		{},
		{'elif', 'else', 'ensure', 'extern'},
		{'for', 'false'},
		{'get'},
		{},
		{'if', 'in', 'include', 'import'},
		{},
		{},
		{},
		{'maybe'},
		{'not', 'null', 'namespace'},
		{'or', 'operator'},
		{'private'},
		{},
		{'return', 'require'},
		{'set', 'switch'},
		{'target', 'to', 'try', 'template', 'throw', 'true', 'test'},
		{'until'},
		{},
		{'while'},
		{},
		{},
		{},
		{},
	] + [{}] * (256 - 97 - 26)
	
	# Keyword list
	keywordList = {
		'and', 'assert',
		'break',
		'class', 'continue', 'const', 'case', 'catch', 'compilerflags',
		'elif', 'else', 'ensure', 'extern',
		'for', 'false',
		'get',
		'if', 'in', 'include', 'import',
		'maybe',
		'not', 'null', 'namespace',
		'or', 'operator',
		'private',
		'return', 'require',
		'set', 'switch',
		'to', 'try', 'template', 'target', 'throw', 'true', 'test',
		'until',
		'while',
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
		if not text or (self.bpIDE.codeEdit and self.bpIDE.codeEdit.disableUpdatesFlag):
			return
		
		style = self.bpIDE.getCurrentTheme()
		
		i = 0
		text += " "
		textLen = len(text)
		userData = self.currentBlockUserData()
		
		#print("HIGHLIGHTING >%s< OF LENGTH %d" % (text, textLen))
		#if self.updateCharFormatFlag:
		#	self.setFormat(0, textLen, style['default'])
		
		while i < textLen:
			char = text[i]
			if char.isalpha() or char == '_' or char == '~':
				h = i + 1
				while h < textLen and (text[h].isalnum() or text[h] == '_'): #or (char =='~' and (text[h] == '<' or text[h] == '>'))):
					h += 1
				expr = text[i:h]
				
				# No highlighting for unicode
				ascii = ord(char)
				if ascii > 255:
					i = h
					continue
				
				#print(ord(expr[0]))
				#print(BPCHighlighter.keywords[ord(expr[0])])
				
				if (userData and userData.node):
					node = userData.node
					inClass = (node.parentNode.parentNode.tagName == "class" or (node.parentNode.parentNode.tagName != "module" and node.parentNode.parentNode.parentNode.tagName == "class"))
					if inClass and node.tagName in functionNodeTagNames and i == countTabs(text):
						self.setFormat(i, h - i, style['class-' + userData.node.tagName])
						i = h
						continue
					elif userData.node.tagName == "class":
						self.setFormat(i, h - i, style['class-name'])
						i = h
						continue
				
				if expr in (BPCHighlighter.keywords[ascii]):
					if expr == "target":
						self.setFormat(i, h - i, style['keyword'])
						j = h + 1
						while j < textLen and not text[j].isspace():
							j += 1
						self.setFormat(h, j - h, style['output-target'])
						h = j
					elif expr == "import":
						self.setFormat(i, h - i, style['keyword'])
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
					elif expr == "until" or expr == "to":
						# Possible bug, but ignorable
						if (len(text) >= 3 and text.lstrip()[:3] == "for") or text.lstrip()[:2] == "to":
							self.setFormat(i, h - i, style['keyword'])
					else:
						self.setFormat(i, h - i, style['keyword'])
				elif expr.startswith("bp_"):
					self.setFormat(i, h - i, style['extern-function'])	
					i = h
					continue
				elif expr == "my":
					self.setFormat(i, h - i, style['self'])
					i = h
					continue
				elif self.bpIDE.processor.getFirstDTreeByFunctionName(expr):
					self.setFormat(i, h - i, style['function'])
					i = h
					continue
				
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
				if i < textLen - 1 and text[i + 1].isspace():
					self.setFormat(i, textLen - i, style['comment'])
				else:
					self.setFormat(i, textLen - i, style['disabled'])
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

# This syntax module is based on Eric Pierce's syntax highlighter for Python:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting

from PyQt4 import QtGui, QtCore
from bp.Tools.IDE import *

class BPCHighlighter(QtGui.QSyntaxHighlighter):
	"""Syntax highlighter for the Python language.
	"""
	# Python keywords
	keywords = [
		'and', 'assert', 'break', 'class', 'continue',
		'elif', 'else', 'except',
		'for', 'from', 'to', 'until', 'if', 'import', 'in',
		'switch', 'case', 'target', 'compilerflags', 'get', 'set', 'operator', 'extern', 'include',
		'template', 'not', 'or',
		'return', 'try', 'catch', 'while',
		'target', 'include',
		'null', 'true', 'false',
	]
	
	# Python operators
	operators = [
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
	]

	# Python braces
	braces = [
		'\{', '\}', '\(', '\)', '\[', '\]', '\<', '\>',
	]
	
	def __init__(self, document, STYLES):
		QtGui.QSyntaxHighlighter.__init__(self, document)

		# Multi-line strings (expression, flag, style)
		# FIXME: The triple-quotes in these two lines will mess up the
		# syntax highlighting from this point onward
		self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
		self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

		rules = []

		# Keyword, operator, and brace rules
		rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
			for w in BPCHighlighter.keywords]
		rules += [(r'%s' % o, 0, STYLES['operator'])
			for o in BPCHighlighter.operators]
		rules += [(r'%s' % b, 0, STYLES['brace'])
			for b in BPCHighlighter.braces]

		# All other rules
		rules += [
			# 'self'
			(r'\bself\b', 0, STYLES['self']),
			
			# From '#' until a newline
			(r'#[^\n]*', 0, STYLES['comment']),
			
			# Double-quoted string, possibly containing escape sequences
			(r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
			# Single-quoted string, possibly containing escape sequences
			(r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

			# 'target' followed by an identifier
			#(r'\btarget\b\s*(\w\++)', 1, STYLES['output-target']),
			#(r'\binclude\b\s*(.*)', 1, STYLES['include-file']),
			# 'class' followed by an identifier
			#(r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

			# From '#' until a newline
			(r'#[^\n]*', 0, STYLES['comment']),

			# Numeric literals
			(r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
			(r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
			(r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
		]
		
		# Own functions
		#self.ownFunctionRule = QtCore.QRegExp(r'\b([a-zA-Z0-9_]*)\b\s*\(.*\)')
		#self.ownFunctionStyle = STYLES['own-function']
		
		# Build a QRegExp for each pattern
		self.rules = [(QtCore.QRegExp(pat), index, fmt)
			for (pat, index, fmt) in rules]


	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		# Do other syntax formatting
		for expression, nth, style in self.rules:
			index = expression.indexIn(text, 0)
			
			while index >= 0:
				# We actually want the index of the nth match
				index = expression.pos(nth)
				length = len(expression.cap(nth))
				self.setFormat(index, length, style)
				index = expression.indexIn(text, index + length)
		
		# Own functions
		#expression = self.ownFunctionRule
		#nth = 1
		#style = self.ownFunctionStyle
		#index = expression.indexIn(text, 0)
		#while index >= 0:
		#	# We actually want the index of the nth match
		#	index = expression.pos(nth)
		#	length = len(expression.cap(nth))
		#	self.setFormat(index, length, style)
		#	index = expression.indexIn(text, index + length)
		
		self.setCurrentBlockState(0)

		# Do multi-line strings
		#in_multiline = self.match_multiline(text, *self.tri_single)
		#if not in_multiline:
		#	in_multiline = self.match_multiline(text, *self.tri_double)

	def match_multiline(self, text, delimiter, in_state, style):
		"""Do highlighting of multi-line strings. ``delimiter`` should be a
		``QRegExp`` for triple-single-quotes or triple-double-quotes, and
		``in_state`` should be a unique integer to represent the corresponding
		state changes when inside those strings. Returns True if we're still
		inside a multi-line string when this function is finished.
		"""
		# If inside triple-single quotes, start at 0
		if self.previousBlockState() == in_state:
			start = 0
			add = 0
		# Otherwise, look for the delimiter on this line
		else:
			start = delimiter.indexIn(text)
			# Move past this match
			add = delimiter.matchedLength()

		# As long as there's a delimiter match on this line...
		while start >= 0:
			# Look for the ending delimiter
			end = delimiter.indexIn(text, start + add)
			# Ending delimiter on this line?
			if end >= add:
				length = end - start + add + delimiter.matchedLength()
				self.setCurrentBlockState(0)
			# No; multi-line string
			else:
				self.setCurrentBlockState(in_state)
				length = text.length() - start + add
			# Apply formatting
			self.setFormat(start, length, style)
			# Look for the next match
			start = delimiter.indexIn(text, start + length)

		# Return True if still inside a multi-line string, False otherwise
		if self.currentBlockState() == in_state:
			return True
		else:
			return False

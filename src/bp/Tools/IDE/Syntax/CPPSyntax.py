from PyQt4 import QtGui, QtCore
from bp.Tools.IDE import *
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from bp.Compiler.Input.bpc import *

class CPPHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Syntax highlighter for the C++ language.
	"""
	# C++ keywords
	keywords = [{}] * 97 + [
		{'and', 'assert'},
		{'break'},
		{'class', 'continue', 'const', 'case', 'catch'},
		{'default', 'delete'},
		{'elif', 'else', 'ensure', 'extern', 'extends'},
		{'for', 'false', },
		{'get'},
		{},
		{'if', 'inline', 'include'},
		{},
		{},
		{'long'},
		{},
		{'not', 'namespace', 'new'},
		{'or', 'operator'},
		{'private', 'public'},
		{},
		{'return'},
		{'sizeof', 'switch', 'struct'},
		{'try', 'typename', 'typedef', 'template', 'throw', 'true'},
		{'until'},
		{'virtual', 'volatile'},
		{'while'},
		{},
		{},
		{},
		{},
	] + [{}] * (256 - 97 - 26)
	
	# Keyword list
	keywordList = {
		'and', 'assert',
		'break', 'bool',
		'class', 'continue', 'const', 'char', 'case', 'catch',
		'double', 'default', 'delete',
		'elif', 'else', 'ensure', 'extern', 'extends',
		'for', 'false', 'float',
		'get',
		'if', 'inline', 'include', 'int',
		'long',
		'not', 'null', 'namespace', 'new',
		'or', 'operator',
		'private', 'public',
		'return',
		'sizeof', 'switch', 'struct',
		'try', 'typename', 'typedef', 'template', 'throw', 'true',
		'until',
		'void', 'virtual', 'volatile',
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
		'<-', '->', '<--', '-->',
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
		bpIDE = self.bpIDE
		if not text:
			return
		
		style = bpIDE.getCurrentTheme()
		
		if bpIDE.outputCompiler:
			externFuncs = bpIDE.outputCompiler.mainClass.externFunctions
		else:
			externFuncs = {}
		
		i = 0
		text += " "
		textLen = len(text)
		userData = None
		
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
				print(expr)
				# No highlighting for unicode
				ascii = ord(char)
				if ascii > 255:
					i = h
					continue
				
				if expr in (CPPHighlighter.keywords[ascii]):
					self.setFormat(i, h - i, style['keyword'])
				elif expr in externFuncs:
					# Extern function call
					
					# Temporary hack
					if not expr in bpIDE.processor.externFuncNameToMetaDict:
						pos = expr.find("_")
						if pos != -1:
							expr = expr[pos+1:]
					
					if expr in bpIDE.processor.externFuncNameToMetaDict:
						meta = bpIDE.processor.externFuncNameToMetaDict[expr]
						
						sideEffects = not ("no-side-effects" in meta and meta["no-side-effects"] == "true")
						sameOutput = ("same-output-for-input" in meta and meta["same-output-for-input"] == "true")
						
						if sameOutput and not sideEffects:
							self.setFormat(i, h - i, style['ref-transparent-extern-function'])
						elif sideEffects:
							self.setFormat(i, h - i, style['side-effects-extern-function'])
						else:
							self.setFormat(i, h - i, style['no-side-effects-extern-function'])
					else:
						meta = None
						self.setFormat(i, h - i, style['default'])
					
					i = h
					continue
				elif expr == "this":
					self.setFormat(i, h - i, style['self'])
					i = h
					continue
				elif expr in {
						# C
						'char', 'bool', 'void', 'int', 'float', 'double', 'short',
						
						# GLSL
						'vec2', 'vec3', 'vec4',
						'bvec2', 'bvec3', 'bvec4',
						'ivec2', 'ivec3', 'ivec4',
						'mat2', 'mat3', 'mat4',
						'sampler1D', 'sampler2D', 'sampler3D', 'samplerCube',
						'sampler1DShadow', 'sampler2DShadow',
						}:
					# Quick hack
					self.setFormat(i, h - i, style['c-datatypes'])
					i = h
					continue
				elif expr in {
						# GLSL
						'in', 'out', 'inout',
						
						'attribute', 'uniform', 'varying',
						}:
					self.setFormat(i, h - i, style['keyword'])
					i = h
					continue
				elif expr == "main":
					# Quick hack
					self.setFormat(i, h - i, style['c-main'])
					i = h
					continue
				elif bpIDE.processor.getFirstDTreeByFunctionName(expr):
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
			elif char == '/' and text[i + 1] == '/':
				if i < textLen - 1 and text[i + 2].isspace():
					self.setFormat(i, textLen - i, style['comment'])
				else:
					self.setFormat(i, textLen - i, style['disabled'])
				return
			elif char == '#':
				self.setFormat(i, textLen - i, style['preprocessor'])
				return
			elif char == ',':
				self.setFormat(i, 1, style['comma'])
			elif char in '+-*/=<>%&|:!\\~':
				#h = i + 1
				#while h < textLen and text[h]:
				#	h += 1
				self.setFormat(i, 1, style['operator'])
				#i = h
			elif char in CPPHighlighter.braces:
				self.setFormat(i, 1, style['brace'])
				
			i += 1
		#self.endBenchmark()
		
		#self.setCurrentBlockState(0)


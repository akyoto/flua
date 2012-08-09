from PyQt4 import QtGui, QtCore
from flua.Tools.IDE import *
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Compiler.Input.bpc import *
from flua.Compiler.Output import *

class CPPHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Syntax highlighter for the C++ language.
	"""
	def __init__(self, document, bpIDE):
		QtGui.QSyntaxHighlighter.__init__(self, document)
		Benchmarkable.__init__(self)
		
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
				elif expr in CPPHighlighter.cFuncs:
					self.setFormat(i, h - i, style['c-function'])
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
				elif expr in CPPHighlighter.cDataTypes or expr in nonPointerClasses or expr.startswith("GL") or expr.endswith("_t"):
					# Quick hack
					self.setFormat(i, h - i, style['internal-datatypes'])
					i = h
					continue
				elif expr in CPPHighlighter.glslQualifiers:
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


from PyQt4 import QtGui, QtCore
from flua.Tools.IDE import *
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Compiler.Input.bpc import *
import flua.Compiler.Input.bpc.BPCUtils as bpcUtils

class GenericHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Generic syntax highlighter
	"""
	def __init__(self, environment, document, bpIDE):
		QtGui.QSyntaxHighlighter.__init__(self, document)
		Benchmarkable.__init__(self)
		
		self.environment = environment
		self.bpIDE = bpIDE
		
	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		bpIDE = self.bpIDE
		ce = bpIDE.codeEdit
		
		# Environment
		currentNamespace = self.environment.mainNamespace
		typeDefinitions = self.environment.defines
		keywords = self.environment.highlightKeywords
		operators = self.environment.operators
		braces = self.environment.braces
		singleLineCommentIndicators = self.environment.singleLineCommentIndicators
		preprocessorIndicators = self.environment.preprocessorIndicators
		specialKeywords = self.environment.specialKeywords
		internalDataTypes = self.environment.internalDataTypes
		internalFunctions = self.environment.internalFunctions
		selfReferences = self.environment.selfReferences
		
		if not text:
			return
		
		style = bpIDE.getCurrentTheme()
		
		i = 0
		text += " "
		textLen = len(text)
		userData = self.currentBlockUserData()
		expr = ""
		previousExpr = ""
		
		while i < textLen:
			char = text[i]
			
			if char.isalpha() or char == '_' or char == '~':
				h = i + 1
				while h < textLen and (text[h].isalnum() or text[h] == '_'): #or (char =='~' and (text[h] == '<' or text[h] == '>'))):
					h += 1
				
				previousExpr = expr
				expr = text[i:h]
				
				if (userData and userData.node):
					node = userData.node
					if node.nodeType != Node.TEXT_NODE:
						inClass = node.parentNode.tagName != "module" and (node.parentNode.parentNode.tagName == "class" or (node.parentNode.parentNode.tagName != "module" and node.parentNode.parentNode.parentNode.tagName == "class"))
						isStart = (i == countTabs(text))
						if inClass and node.tagName in functionNodeTagNames and isStart:
							if not bpcUtils.currentSyntax == SYNTAX_PYTHON:
								self.setFormat(i, h - i, style['class-' + userData.node.tagName])
								i = h
								continue
							else:
								pos = text.find("(")
								#self.setFormat(i, h - i, style['keyword']) # def keyword
								self.setFormat(h, pos - h, style['class-' + userData.node.tagName]) # class element
							
						elif userData.node.tagName == "class":
							if not bpcUtils.currentSyntax == SYNTAX_PYTHON:
								self.setFormat(i, h - i, style['class-name'])
								i = h
								continue
						elif userData.node.tagName == "extern-function": #and expr.startswith("flua_"):
							# TODO: Optimize using bpIDE.processor
							if isMetaDataTrue(getMetaData(node, "no-side-effects")):
								if isMetaDataTrue(getMetaData(node, "same-output-for-input")):
									self.setFormat(i, h - i, style['ref-transparent-extern-function'])
								else:
									self.setFormat(i, h - i, style['no-side-effects-extern-function'])
							else:
								self.setFormat(i, h - i, style['side-effects-extern-function'])
							i = h
							return
				
				# Ignore properties as keyword names
				if i > 0 and text[i-1] == ".":
					i = h
					continue
				
				if expr in keywords:
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
						importType = bpIDE.getModuleImportType(importedModule)
						if importType == 1 or importType == 2:
							self.setFormat(h, j - h, style['local-module-import'])
						elif importType == 3 or importType == 4:
							self.setFormat(h, j - h, style['project-module-import'])
						elif importType == 5 or importType == 6:
							self.setFormat(h, j - h, style['global-module-import'])
						h = j
					# Flua includes
					elif expr == "include":
						self.setFormat(i, h - i, style['keyword'])
						i = text.find("#")
						if i != -1:
							continue
						else:
							return
					elif expr in {"until", "to", "counting"}:
						# Possible bug, but ignorable
						if (len(text) >= 4 and text.lstrip()[:4] in {"for ", "pfor"}) or text.strip() == "to":
							self.setFormat(i, h - i, style['keyword'])
					elif expr == "parallel":
						if (len(text) >= 8 and text.lstrip()[:8] == "parallel"):
							self.setFormat(i, h - i, style['keyword'])
					else:
						self.setFormat(i, h - i, style['keyword'])
				elif expr in currentNamespace.externFunctions or (("%s_%s" % (previousExpr, expr)) in currentNamespace.externFunctions):
					# Extern function call
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
				elif expr in selfReferences:
					self.setFormat(i, h - i, style['self'])
					i = h
					continue
				elif expr in internalFunctions:
					self.setFormat(i, h - i, style['internal-function'])
					i = h
					continue
				elif expr in internalDataTypes: #or expr in nonPointerClasses or expr.startswith("GL") or expr.endswith("_t"):
					# Quick hack
					self.setFormat(i, h - i, style['internal-datatype'])
					i = h
					continue
				elif expr in specialKeywords:
					self.setFormat(i, h - i, style['keyword'])
					i = h
					continue
				elif expr in currentNamespace.functions: #bpIDE.processor.getFirstDTreeByFunctionName(expr):
					currentNamespace = self.environment.mainNamespace
					self.setFormat(i, h - i, style['function'])
					i = h
					continue
				elif expr in currentNamespace.classes or expr in typeDefinitions:
					currentNamespace = self.environment.mainNamespace
					self.setFormat(i, h - i, style['class-name'])
					i = h
					continue
				elif expr in currentNamespace.namespaces:
					if text[h] == ".":
						currentNamespace = currentNamespace.namespaces[expr]
					self.setFormat(i, h - i, style['namespace'])
					i = h
					continue
				
				currentNamespace = self.environment.mainNamespace
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
			elif char == '"' or char == "'":
				h = i + 1
				while h < textLen and text[h] != char:
					h += 1
				
				# TODO: WHY IS THIS CALL SO BUGGY ON WINDOWS?!
				if h < textLen - 1 and text[h] == char:
					self.setFormat(i, h - i + 1, style['string'])
				
				#print(i, h - i, style['string'])
				#if h < textLen - 1:
				#	if text[h] == '"':
				#		self.setFormat(i, h - i + 1, style['string'])
				#	else:
				#		self.setFormat(i, h - i, style['string'])
				#else:
				i = h
			elif char == ',':
				self.setFormat(i, 1, style['comma'])
			else:
				# Single line comments
				for indicator in singleLineCommentIndicators:
					indLen = len(indicator)
					
					if i + indLen < textLen and text[i : i + indLen] == indicator:
						if ce.isTextFile or (i < textLen - 1 and text[i + 1].isspace()):
							self.setFormat(i, textLen - i, style['comment'])
						else:
							self.setFormat(i, textLen - i, style['disabled'])
						return
				
				# Check XML data
				if userData and userData.node and userData.node.nodeType != Node.TEXT_NODE:
					# Operators
					if i == 0 and userData.node.tagName == "operator":
						if not bpcUtils.currentSyntax == SYNTAX_PYTHON:
							start = getNextNonWhitespacePos(text, i)
							end = getNextWhitespacePos(text, start + 1)
							self.setFormat(start, end - start, style['class-operator'])
							i = end + 1
							continue
				
				# Other cases
				if char in preprocessorIndicators:
					self.setFormat(i, textLen - i, style['preprocessor'])
					return
				elif char in operators:
					#h = i + 1
					#while h < textLen and text[h]:
					#	h += 1
					self.setFormat(i, 1, style['operator'])
					#i = h
				elif char in braces:
					self.setFormat(i, 1, style['brace'])
				
			i += 1


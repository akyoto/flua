from flua.Tools.IDE.Syntax.GenericSyntax import *
import flua.Compiler.Input.bpc.BPCUtils as bpcUtils

class FluaHighlighter(GenericHighlighter, Benchmarkable):
	"""Syntax highlighter for the Flua language.
	"""
	
	def __init__(self, document, bpIDE):
		GenericHighlighter.__init__(self, document, bpIDE)
	
	#def highlightBlock(self, text):
		#"""Apply syntax highlighting to the given block of text.
		#"""
		#bpIDE = self.bpIDE
		#ce = bpIDE.codeEdit
		
		##if ce and ce.completer:
		##	model = ce.completer.bpcModel
		##	externFuncs = model.externFuncs
		##else:
		##	externFuncs = {}
		
		#if bpIDE.outputCompiler:
			#externFuncs = bpIDE.outputCompiler.mainClass.externFunctions
		#else:
			#externFuncs = {}
		
		#if not text or (ce and ce.disableUpdatesFlag):
			#return
		
		##self.startBenchmark("Highlight block")
		
		#style = bpIDE.getCurrentTheme()
		
		#i = 0
		#text += " "
		#textLen = len(text)
		#userData = self.currentBlockUserData()
		#expr = ""
		#previousExpr = ""
		
		##print("HIGHLIGHTING >%s< OF LENGTH %d" % (text, textLen))
		##if self.updateCharFormatFlag:
		##	self.setFormat(0, textLen, style['default'])
		
		## Ruby
		#if text.strip() == "end":
			#self.setFormat(0, textLen, style['keyword'])
			#return
		
		#while i < textLen:
			#char = text[i]
			#if char.isalpha() or char == '_' or char == '~':
				#h = i + 1
				#while h < textLen and (text[h].isalnum() or text[h] == '_'): #or (char =='~' and (text[h] == '<' or text[h] == '>'))):
					#h += 1
					
				#previousExpr = expr
				#expr = text[i:h]
				
				## No highlighting for unicode
				#ascii = ord(char)
				#if ascii > 255:
					#i = h
					#continue
				
				##print(ord(expr[0]))
				##print(FluaHighlighter.keywords[ord(expr[0])])
				#if (userData and userData.node):
					#node = userData.node
					#if userData.node.nodeType != Node.TEXT_NODE:
						#inClass = node.parentNode.tagName != "module" and (node.parentNode.parentNode.tagName == "class" or (node.parentNode.parentNode.tagName != "module" and node.parentNode.parentNode.parentNode.tagName == "class"))
						#if inClass and node.tagName in functionNodeTagNames and i == countTabs(text):
							#if not bpcUtils.currentSyntax == SYNTAX_PYTHON:
								#self.setFormat(i, h - i, style['class-' + userData.node.tagName])
								#i = h
								#continue
							#else:
								#pos = text.find("(")
								##self.setFormat(i, h - i, style['keyword']) # def keyword
								#self.setFormat(h, pos - h, style['class-' + userData.node.tagName]) # class element
							
						#elif userData.node.tagName == "class":
							#if not bpcUtils.currentSyntax == SYNTAX_PYTHON:
								#self.setFormat(i, h - i, style['class-name'])
								#i = h
								#continue
						#elif userData.node.tagName == "extern-function": #and expr.startswith("flua_"):
							## TODO: Optimize using bpIDE.processor
							#if isMetaDataTrue(getMetaData(node, "no-side-effects")):
								#if isMetaDataTrue(getMetaData(node, "same-output-for-input")):
									#self.setFormat(i, h - i, style['ref-transparent-extern-function'])
								#else:
									#self.setFormat(i, h - i, style['no-side-effects-extern-function'])
							#else:
								#self.setFormat(i, h - i, style['side-effects-extern-function'])
							#i = h
							#return
				
				#if expr in (FluaHighlighter.keywords[ascii]):
					#if expr == "target":
						#self.setFormat(i, h - i, style['keyword'])
						#j = h + 1
						#while j < textLen and not text[j].isspace():
							#j += 1
						#self.setFormat(h, j - h, style['output-target'])
						#h = j
					#elif expr == "import":
						#self.setFormat(i, h - i, style['keyword'])
						#j = h + 1
						#while j < textLen and not text[j].isspace():
							#j += 1
						#importedModule = text[h+1:j]
						#importType = bpIDE.getModuleImportType(importedModule)
						#if importType == 1 or importType == 2:
							#self.setFormat(h, j - h, style['local-module-import'])
						#elif importType == 3 or importType == 4:
							#self.setFormat(h, j - h, style['project-module-import'])
						#elif importType == 5 or importType == 6:
							#self.setFormat(h, j - h, style['global-module-import'])
						#h = j
					#elif expr in {"until", "to", "counting"}:
						## Possible bug, but ignorable
						#if (len(text) >= 4 and text.lstrip()[:4] in {"for ", "pfor"}) or text.lstrip()[:2] == "to":
							#self.setFormat(i, h - i, style['keyword'])
					#elif expr == "parallel":
						#if (len(text) >= 8 and text.lstrip()[:8] == "parallel"):
							#self.setFormat(i, h - i, style['keyword'])
					#else:
						#self.setFormat(i, h - i, style['keyword'])
				#elif expr in externFuncs or (("%s_%s" % (previousExpr, expr)) in externFuncs):
					## Extern function call
					#if expr in bpIDE.processor.externFuncNameToMetaDict:
						#meta = bpIDE.processor.externFuncNameToMetaDict[expr]
						
						#sideEffects = not ("no-side-effects" in meta and meta["no-side-effects"] == "true")
						#sameOutput = ("same-output-for-input" in meta and meta["same-output-for-input"] == "true")
						
						#if sameOutput and not sideEffects:
							#self.setFormat(i, h - i, style['ref-transparent-extern-function'])
						#elif sideEffects:
							#self.setFormat(i, h - i, style['side-effects-extern-function'])
						#else:
							#self.setFormat(i, h - i, style['no-side-effects-extern-function'])
					#else:
						#meta = None
						#self.setFormat(i, h - i, style['default'])
					
					#i = h
					#continue
				#elif expr in {"my", "this", "self"}:
					#self.setFormat(i, h - i, style['self'])
					#i = h
					#continue
				#elif bpIDE.processor.getFirstDTreeByFunctionName(expr):
					#self.setFormat(i, h - i, style['function'])
					#i = h
					#continue
				
				#i = h - 1
			#elif char.isdigit():
				#h = i + 1
				#while h < textLen and text[h].isdigit():
					#h += 1
				#if (i == 0 or not text[i - 1].isalpha()) and not text[h].isalpha():
					#self.setFormat(i, h - i, style['number'])
				#elif text[i] == '0' and text[h] == 'x':
					#h += 1
					#while h < textLen and (text[h].isdigit() or text[h] in "ABCDEFabcdef"):
						#h += 1
					#self.setFormat(i, h - i, style['hex-number'])
				##else:
				##	
				#i = h - 1
			#elif char == '"' or char == "'":
				#h = i + 1
				#while h < textLen and text[h] != char:
					#h += 1
				
				## TODO: WHY IS THIS CALL SO BUGGY ON WINDOWS?!
				#if h < textLen - 1 and text[h] == char:
					#self.setFormat(i, h - i + 1, style['string'])
				
				##print(i, h - i, style['string'])
				##if h < textLen - 1:
				##	if text[h] == '"':
				##		self.setFormat(i, h - i + 1, style['string'])
				##	else:
				##		self.setFormat(i, h - i, style['string'])
				##else:
				#i = h
			#elif char == '#':
				#if i < textLen - 1 and text[i + 1].isspace():
					#self.setFormat(i, textLen - i, style['comment'])
				#else:
					#self.setFormat(i, textLen - i, style['disabled'])
				#return
			#elif char == ',':
				#self.setFormat(i, 1, style['comma'])
			#elif char in '+-*/=<>%&|:!\\~^':
				##h = i + 1
				##while h < textLen and text[h]:
				##	h += 1
				#self.setFormat(i, 1, style['operator'])
				##i = h
			#elif char in FluaHighlighter.braces:
				#self.setFormat(i, 1, style['brace'])
				
			#i += 1
		
		##self.endBenchmark()
		
		##self.setCurrentBlockState(0)

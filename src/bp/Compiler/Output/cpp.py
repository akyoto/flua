####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
# 
# This file is part of Blitzprog.
# 
# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from ExpressionParser import *
from Utils import *
import codecs
import subprocess

####################################################################
# Classes
####################################################################
class CPPClass:
	
	def __init__(self, name):
		self.name = name
		self.functions = {}
		
class CPPVariable:
	
	def __init__(self, name, type, value, isConst = False):
		self.name = name
		self.type = type
		self.value = value
		self.isConst = isConst
		
class CPPFunction:
	
	def __init__(self, file, node):
		self.file = file
		self.node = node
		self.implementations = {}
		
	def getName(self):
		return self.node.getElementsByTagName("name")[0].childNodes[0].nodeValue

class FunctionImplRequest:
	
	def __init__(self, name, paramTypes):
		self.name = name
		self.paramTypes = paramTypes
		self.implementation = ""
		
	def getName(self):
		return self.name
		
	def getPrototype(self):
		return self.name + "(" + ", ".join(self.paramTypes) + ")"
	
	def isImplemented(self):
		return self.implementation != ""

class CPPOutputCompiler:
	
	def __init__(self, inpCompiler):
		self.inputCompiler = inpCompiler
		self.inputFiles = inpCompiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.projectDir = self.inputCompiler.projectDir
		self.modDir = inpCompiler.modDir
		self.stringCounter = 0;
		self.fileCounter = 0;
		self.outputDir = ""
		self.mainFile = ""
		self.globalScope = Scope()
		self.implementationRequests = {}
		self.functionTypes = {}
		
		self.classes = {}
		self.classes[""] = CPPClass("")
	
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile)
		self.compiledFiles[inpFile] = cppOut
		self.compiledFilesList.insert(0, cppOut)
		
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		cppOut.compile()
		
#		self.inputFiles.reverse()
#		for inpFile in self.inputFiles:
#			cppOut = CPPOutputFile(self, inpFile)
#			cppOut.compile()
#			self.compiledFiles[inpFile] = cppOut
#			self.compiledFilesList.append(cppOut)
			
		# 2 times because at the first run there might have appeared new calls
#		for i in range(2):
#			for cppFile in self.compiledFiles.values():
#				cppFile.implement()
	
	def writeToFS(self, dirOut):
		dirOut = fixPath(os.path.abspath(dirOut)) + "/"
		self.outputDir = dirOut
		
		for cppFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(os.path.relpath(cppFile.file, self.projectDir)) + "-out.hpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				outStream.write(cppFile.getCode())
			
			# CPP main file
			if cppFile.isMainFile:
				hppFile = os.path.basename(fileOut)
				
				fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + "-out.cpp"
				self.mainFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
	def build(self):
		exe = stripExt(self.mainFile)
		if os.path.isfile(exe):
			os.unlink(exe)
		
		cmd = ["g++", self.mainFile, "-o", exe, "-I" + self.outputDir]
		try:
			proc = subprocess.Popen(cmd)
			proc.wait()
		except OSError:
			print("Couldn't start g++")
		
		return exe
	
	def execute(self, exe):
		cmd = [exe]
		
		try:
			proc = subprocess.Popen(cmd)
			proc.wait()
		except OSError:
			print("Build process failed")
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.compiledFilesList:
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"
	
class CPPOutputFile(ScopeController):
	
	def __init__(self, compiler, inpFile):
		self.currentTabLevel = 0
		
		ScopeController.__init__(self)
		
		self.compiler = compiler
		self.file = inpFile.file
		self.root = inpFile.getRoot()
		self.isMainFile = inpFile.isMainFile
		self.dir = inpFile.dir
		self.codeNode = self.root.getElementsByTagName("code")[0]
		self.headerNode = self.root.getElementsByTagName("header")[0]
		self.dependencies = self.headerNode.getElementsByTagName("dependencies")[0]
		self.strings = self.headerNode.getElementsByTagName("strings")[0]
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		self.classes = dict()
		self.classes[""] = CPPClass("")
		
		self.currentClass = self.compiler.classes[""]
		
		self.inConst = False
		self.inClass = False
		self.inFunction = False
		self.currentFuncReturnTypes = []
		
		self.dataTypeWeights = {
			"Bool" : 1,
			"Byte" : 2,
			"Short" : 3,
			"Int" : 4,
			"Float" : 5,
			"Double" : 6
		}
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"]
		}
		
		#self.id = self.file.replace("/", "_").replace(".", "_")
		self.id = "file_" + str(self.compiler.fileCounter)
		self.compiler.fileCounter += 1
		
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.topLevel = ""
		self.footer = "#endif\n"
		self.stringsHeader = ""
		self.varsHeader = ""
		self.functionsHeader = ""
		self.classesHeader = ""
		self.typeDefsHeader = "\n// Typedefs\n"
		self.prototypesHeader = "\n// Prototypes\n"
		
	def pushScope(self):
		self.currentTabLevel += 1
		ScopeController.pushScope(self)
		
	def popScope(self):
		self.currentTabLevel -= 1
		ScopeController.popScope(self)
		
	def compile(self):
		print("Output: " + self.file)
		
		# Find classes
		self.findDefinitions(self.codeNode)
		
		# Header
		self.header += "// Includes\n";
		for node in self.dependencies.childNodes:
			self.header += self.handleImport(node)
		
		self.header += "\n#define String const char *\n"
		
		# Functions
		self.functionsHeader += "\n// Functions\n";
		
		# Code
		self.topLevel += "// Module execution\n";
		self.topLevel += "void exec_" + self.id + "() {\n"
		
		# Strings
		self.stringsHeader = "\t// Strings\n";
		for node in self.strings.childNodes:
			self.stringsHeader += "\t" + self.handleString(node)
		self.stringsHeader += "\n\t// Code\n"
		
		self.topLevel += self.stringsHeader
		
		# Top level code
		self.topLevel += self.parseChilds(self.codeNode, "\t" * self.currentTabLevel, ";\n")
		self.topLevel += "}\n"
		
		# Variables
		self.varsHeader = "\n// Variables\n";
		for var in self.getTopLevelScope().variables.values():
			if var.isConst:
				self.varsHeader += "const " + var.type + " " + var.name + " = " + var.value + ";\n";
			else:
				self.varsHeader += var.type + " " + var.name + ";\n";
		
		#print(self.getCode())
		
	def parseChilds(self, parent, prefix = "", postFix = ""):
		lines = ""
		for node in parent.childNodes:
			line = self.parseExpr(node)
			if line:
				lines += prefix + line + postFix
		return lines
		
	def findDefinitions(self, parent):
		for node in parent.childNodes:
			if isTextNode(node):
				pass
			elif node.tagName == "class":
				self.handleClass(node)
			elif node.tagName == "function":
				self.handleFunction(node)
		
	def parseExpr(self, node):
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_" + node.nodeValue
			else:
				return node.nodeValue
		elif node.tagName == "value":
			return self.parseExpr(node.childNodes[0])
		elif node.tagName == "const":
			self.inConst = True
			expr = self.parseExpr(node.childNodes[0])
			self.inConst = False
			
			return expr
		elif node.tagName == "assign":
			return self.handleAssign(node)
		elif node.tagName == "call":
			return self.handleCall(node)
		elif node.tagName == "if-block" or node.tagName == "try-block":
			return self.parseChilds(node, "", "")
		elif node.tagName == "else":
			return self.handleElse(node)
		elif node.tagName == "class":
			return ""
		elif node.tagName == "function":
			if self.currentClass.name == "":
				return ""
			return self.handleFunction(node)
		elif node.tagName == "extern":
			return self.handleExtern(node)
		elif node.tagName == "extern-function":
			return self.handleExternFunction(node)
		elif node.tagName == "target":
			return self.handleTarget(node)
		elif node.tagName == "new":
			return self.handleNew(node)
		elif node.tagName == "return":
			return self.handleReturn(node)
		elif node.tagName == "include":
			self.header += "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			return ""
		elif node.tagName == "noop":
			return ""
		
		# Check parameterized blocks
		if node.tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			condition = self.parseExpr(node.getElementsByTagName(paramTagName)[0].childNodes[0])
			
			self.pushScope()
			code = self.parseChilds(node.getElementsByTagName(codeTagName)[0], "\t" * self.currentTabLevel, ";\n")
			self.popScope()
			
			return keywordName + "(" + condition + ") {\n" + code + "\t" * self.currentTabLevel + "}"
		
		# Check operators
		for opLevel in self.compiler.inputCompiler.parser.operatorLevels:
			for op in opLevel.operators:
				if node.tagName == op.name:
					if op.type == Operator.BINARY:
						if op.text == "\\":
							return self.parseBinaryOperator(node, " / ")
						elif op.text == ".":
							return self.parseBinaryOperator(node, "->")
						return self.parseBinaryOperator(node, " " + op.text + " ")
					elif op.type == Operator.UNARY:
						return op.text + "(" + self.parseExpr(node.childNodes[0]) + ")"
		
		return "";
		
	def handleAssign(self, node):
		variable = self.parseExpr(node.childNodes[0])
		value = self.parseExpr(node.childNodes[1])
		valueTypeOriginal = self.getExprDataType(node.childNodes[1].childNodes[0])
		
		if not self.variableExistsAnywhere(variable):
			var = CPPVariable(variable, valueTypeOriginal, value, self.inConst)
			self.getCurrentScope().variables[variable] = var
			if self.getCurrentScope() == self.getTopLevelScope():
				self.compiler.globalScope.variables[variable] = var
				
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const " + valueTypeOriginal + " " + variable + " = " + value
			#print(variable + " = " + valueTypeOriginal)
		
		return variable + " = " + value
		
	def handleExtern(self, node):
		self.pushScope()
		code = self.parseChilds(node, "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return code
	
	def handleExternFunction(self, node):
		name = node.getElementsByTagName("name")[0].childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		self.compiler.functionTypes[name] = type
		
		return ""
		
	def buildCallPostfix(self, types):
		postfix = ""
		for dataType in types:
			postfix += "__" + dataType
		return postfix
		
	def handleReturn(self, node):
		expr = self.parseExpr(node.childNodes[0])
		self.currentFuncReturnTypes.append(self.getExprDataType(node.childNodes[0]))
		return "return " + expr
		
	def handleNew(self, node):
		typeName = self.parseExpr(node.getElementsByTagName("type")[0].childNodes[0])
		params = node.getElementsByTagName("parameters")[0]
		
		paramsString, paramTypes = self.handleParameters(params)
		
		prefix = ""
		if not typeName in self.dataTypeWeights:
			prefix = "BP"
		
		oldClass = self.currentClass
		self.currentClass = self.compiler.classes[typeName]
		
		# Implement init
		funcName = "init"
		func = self.currentClass.functions[funcName]
		
		self.inClass = True
		
		func.implementations[self.buildCallPostfix(paramTypes)] = self.implementFunction(func.node, paramTypes, "\t")
		
		self.inClass = False
		self.currentClass = oldClass
		
		return "new " + prefix + typeName + "(" + paramsString + ")"
		
	def handleCall(self, node):
		funcName = self.parseExpr(node.getElementsByTagName("function")[0].childNodes[0])
		params = node.getElementsByTagName("parameters")[0]
		
		paramsString, paramTypes = self.handleParameters(params)
		implRequest = FunctionImplRequest(funcName, paramTypes)
		
		fullName = funcName + self.buildCallPostfix(paramTypes)
		
		if not funcName.startswith("bp_"):
			if not implRequest.getPrototype() in self.compiler.implementationRequests:
				self.compiler.implementationRequests[implRequest.getPrototype()] = implRequest
				print("Requested implementation of " + implRequest.getPrototype())
				
				className = ""
				if funcName in self.compiler.classes[className].functions:
					func = self.compiler.classes[className].functions[funcName]
				else:
					raise CompilerException("Function '" + funcName + "' has not been defined")
				
				self.functionsHeader += self.implementFunction(func.node, implRequest.paramTypes)
				self.prototypesHeader += "inline " + self.compiler.functionTypes[fullName] + " " + fullName + "(" + ", ".join(paramTypes) + ");\n"
			
			return fullName + "(" + paramsString + ")"
		else:
			return funcName + "(" + paramsString + ")"
		
	def getCallDataType(self, node):
		funcName = self.parseExpr(node.getElementsByTagName("function")[0].childNodes[0])
		params = node.getElementsByTagName("parameters")[0]
		
		paramsString, paramTypes = self.handleParameters(params)
		
		if not funcName.startswith("bp_"):
			funcName += self.buildCallPostfix(paramTypes)
		
		if not funcName in self.compiler.functionTypes:
			raise CompilerException("Function '" + funcName + "' has not been defined")
		
		return self.compiler.functionTypes[funcName]
		
	def handleClass(self, node):
		name = node.getElementsByTagName("name")[0].childNodes[0].nodeValue
		
		self.pushScope()
		self.inClass = True
		self.currentClass = self.classes[name] = self.compiler.classes[name] = CPPClass(name)
		
		code = self.parseChilds(node.getElementsByTagName("code")[0], "\t", ";\n")
		
		self.currentClass = self.compiler.classes[""]
		self.inClass = False
		self.popScope()
		
		return ""
		
	def handleFunction(self, node):
		name = node.getElementsByTagName("name")[0].childNodes[0].nodeValue
		self.currentClass.functions[name] = CPPFunction(self, node)
		
		#print("Registered " + name)
		return ""
		
	def implementFunction(self, node, types, tabLevel = ""):
		name = node.getElementsByTagName("name")[0].childNodes[0].nodeValue
		
		#if self.inClass:
		#	tabLevel *= self.currentTabLevel
		
		self.pushScope()
		self.inFunction = True
		self.currentFuncReturnTypes = []
		
		parameters = self.getParameterDefinitions(node.getElementsByTagName("parameters")[0], types)
		code = self.parseChilds(node.getElementsByTagName("code")[0], tabLevel + "\t", ";\n")
		
		self.inFunction = False
		self.popScope()
		
		funcReturnType = self.getFunctionReturnType()
		
		print(name + self.buildCallPostfix(types) + " -> " + funcReturnType)
		self.compiler.functionTypes[name + self.buildCallPostfix(types)] = funcReturnType
		
		funcName = funcReturnType + " " + name + self.buildCallPostfix(types)
		if self.inClass and name == "init":
			funcName = "BP" + self.currentClass.name
		
		return "inline " + funcName + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#		if self.inClass:
#			return tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#		else:
#			self.functionsHeader += tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#			return ""
		
	def getFunctionReturnType(self):
		heaviest = None
		
		for type in self.currentFuncReturnTypes:
			if type in self.dataTypeWeights:
				heaviest = self.heavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(node.getElementsByTagName("code")[0], "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return " else {\n" + code + "\t" * self.currentTabLevel + "}"
		
	def handleTarget(self, node):
		name = node.getElementsByTagName("name")[0].childNodes[0].nodeValue
		if name == self.compiler.getTargetName():
			return self.parseChilds(node.getElementsByTagName("code")[0], "\t" * self.currentTabLevel, ";\n")
		
	def handleString(self, node):
		id = self.id + "_" + node.getAttribute("id")
		value = node.childNodes[0].nodeValue
		line = id + " = \"" + value + "\";\n"
		self.getTopLevelScope().variables[id] = CPPVariable(id, "String", value)
		self.compiler.stringCounter += 1
		return line
		
	def handleParameters(self, pNode):
		pList = ""
		pTypes = []
		for node in pNode.childNodes:
			pList += self.parseExpr(node.childNodes[0]) + ", "
			pTypes.append(self.getExprDataType(node.childNodes[0]))
		
		return pList[:len(pList)-2], pTypes
	
	def getParameterList(self, pNode):
		pList = []
		
		for node in pNode.childNodes:
			pList.append(self.parseExpr(node.childNodes[0]))
		
		return pList
	
	def getParameterDefinitions(self, pNode, types):
		pList = ""
		counter = 0
		
		for node in pNode.childNodes:
			name = self.parseExpr(node.childNodes[0])
			pList += types[counter] + " " + name + ", "
			self.getCurrentScope().variables[name] = CPPVariable(name, types[counter], "")
			counter += 1
		
		return pList[:len(pList)-2]
	
	def handleImport(self, node):
		importedModulePath = node.childNodes[0].nodeValue.replace(".", "/")
		
		# Local
		importedFile = self.dir + importedModulePath + ".bpc"
		
		importedInFolder = self.dir + importedModulePath
		importedInFolder += "/" + stripAll(importedInFolder) + ".bpc"
		
		# Project
		pImportedFile = self.compiler.projectDir + importedModulePath + ".bpc"
		
		pImportedInFolder = self.compiler.projectDir + importedModulePath
		pImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		# Global
		gImportedFile = self.compiler.modDir + importedModulePath + ".bpc"
		
		gImportedInFolder = self.compiler.modDir + importedModulePath
		gImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		modPath = ""
		
		if os.path.isfile(importedFile):
			modPath = importedFile
		elif os.path.isfile(importedInFolder):
			modPath = importedInFolder
		elif os.path.isfile(pImportedFile):
			modPath = pImportedFile
		elif os.path.isfile(pImportedInFolder):
			modPath = pImportedInFolder
		
		if modPath != "":
			modPath = modPath[len(self.compiler.projectDir):]
		elif os.path.isfile(gImportedFile):
			modPath = gImportedFile
		elif os.path.isfile(gImportedInFolder):
			modPath = gImportedInFolder
		
		return "#include <" + stripExt(modPath) + "-out.hpp>\n"
		
	def parseBinaryOperator(self, node, connector):
		if connector != " / ":
			return self.exprPrefix + self.parseExpr(node.childNodes[0]) + connector + self.parseExpr(node.childNodes[1]) + self.exprPostfix
		else:
			return self.exprPrefix + "float(" + self.parseExpr(node.childNodes[0]) + ")" + connector + self.parseExpr(node.childNodes[1]) + self.exprPostfix
		
	def getCombinationResult(self, operation, operatorType1, operatorType2):
		if operatorType1 in self.dataTypeWeights and operatorType2 in self.dataTypeWeights:
			if operation == "divide":
				dataType = self.heavierOperator(operatorType1, operatorType2)
				if dataType == "Double":
					return dataType
				else:
					return "Float"
			else:
				return self.heavierOperator(operatorType1, operatorType2)
		else:
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
		
	def heavierOperator(self, operatorType1, operatorType2):
		if operatorType1 is None:
			return operatorType2
		if operatorType2 is None:
			return operatorType1
		
		weight1 = self.dataTypeWeights[operatorType1]
		weight2 = self.dataTypeWeights[operatorType2]
		
		if weight1 > weight2:
			return operatorType1
		else:
			return operatorType2
		
	def getExprDataType(self, node):
		if isTextNode(node):
			if node.nodeValue.isdigit():
				return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("bp_string_"):
				return "String"
			else:
				return self.getVariableTypeAnywhere(node.nodeValue)
		else:
			# Binary operators
			if node.tagName == "new":
				# TODO: Template based types
				return node.getElementsByTagName("type")[0].childNodes[0].nodeValue
			elif node.tagName == "call":
				return self.getCallDataType(node)
			elif len(node.childNodes) == 2:
				return self.getCombinationResult(node.tagName, self.getExprDataType(node.childNodes[0].childNodes[0]), self.getExprDataType(node.childNodes[1].childNodes[0]))
			
		raise CompilerException("Unknown data type for: " + node.toxml())
		
	def variableExistsAnywhere(self, name):
		if self.variableExists(name) or name in self.compiler.globalScope.variables:
			return 1
		
		return 0
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			return var.type
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope.variables[name].type
		
		raise CompilerException("Unknown variable: " + name)
		
#	def implement(self):
#		funcs = self.classes[""].functions.copy()
#		reqs = self.compiler.implementationRequests.copy()
#		
#		for func in funcs.values():
#			for implRequest in reqs.values():
#				if func.getName() == implRequest.getName() and not implRequest.isImplemented():
#					print("Implementing " + implRequest.getPrototype())
#					implRequest.implementation = self.implementFunction(func.node, implRequest.paramTypes)
#					self.functionsHeader += implRequest.implementation
		
	def getCode(self):
		for classObj in self.classes.values():
			if classObj.name != "":
				code = ""
				for func in classObj.functions.values():
					for impl in func.implementations.values():
						code += "\t" + impl + "\n"
				prefix = "BP"
				
				self.typeDefsHeader += "class " + prefix + classObj.name + ";\ntypedef " + prefix + classObj.name + "* " + classObj.name + ";\n"
				self.classesHeader += "class " + prefix + classObj.name + " {\npublic:\n" + code + "};\n"
		
		return self.header + self.typeDefsHeader + self.prototypesHeader + self.varsHeader + self.functionsHeader + self.classesHeader + "\n" + self.topLevel + "\n" + self.footer
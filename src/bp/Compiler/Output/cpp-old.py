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
# Global
####################################################################
pointerType = "SPtr"

dataTypeDefinitions = {
	"Bool" : "bool",
	"Byte" : "char",
	"Short" : "short",
	"Int" : "int_fast32_t",
	"Int32" : "int32_t",
	"Int64" : "int64_t",
	"Size" : "size_t",
	"Float" : "float",
	"Float32" : "float",
	"Float64" : "double",
	"String" : "const char *"
}

dataTypeWeights = {
	"Bool" : 1,
	"Byte" : 2,
	"Short" : 3,
	"Int" : 4,
	"Int32" : 5,
	"Int64" : 6,
	"Size" : 7,
	"Float" : 8,
	"Float32" : 9,
	"Float64" : 10,
	"String" : 11
}

nonPointerClasses = {
	"Bool" : 1,
	"Byte" : 2,
	"Short" : 3,
	"Int" : 4,
	"Int32" : 5,
	"Int64" : 6,
	"Size" : 7,
	"Float" : 8,
	"Float32" : 9,
	"Float64" : 10,
	"String" : 11
}

####################################################################
# Classes
####################################################################
class CPPClass:
	
	def __init__(self, name, cppFile, isExtern):
		self.name = name
		self.cppFile = cppFile
		self.functions = {}
		self.members = {}
		self.templateParams = []
		self.usesActorModel = False
		self.isExtern = isExtern
		
	def mapTemplateParams(self, params):
		paramMap = {}
		paramsList = params.split(', ')
		for i in range(len(self.templateParams)):
			param = paramsList[i]
#			paramClass = removeGenerics(param)
#			pointer = ""
#			if not paramClass in nonPointerClasses:
#				paramClass = "BP" + paramClass
#				pointer = "*"
			paramMap[self.templateParams[i]] = param #+ pointer
		return paramMap
		
	def setTemplateParams(self, nList):
		self.templateParams = nList
		
	def getNameWithTemplates(self):
		if self.templateParams:
			return self.name + "<" +  ", ".join(self.templateParams) + ">"
		else:
			return self.name

class CPPVariable:
	
	def __init__(self, name, type, value, isConst, isPointer):
		self.name = name
		self.type = type
		self.value = value
		self.isConst = isConst
		self.isPointer = isPointer
	
	def getFullPrototype(self, templateParams):
		return adjustDataType(self.type, True, templateParams) + " " + self.name
		
class CPPFunction:
	
	def __init__(self, file, node):
		self.file = file
		self.node = node
		self.paramNames = []
		self.returnTypes = []
		self.implementations = {}
		
	def addImplementation(self, impl):
		self.implementations[impl.buildPostfix()] = impl
		impl.func = self
		
	def getName(self):
		return getElementByTagName(self.node, "name").childNodes[0].nodeValue
	
	def isOperator(self):
		return self.node.tagName == "operator"
	
	def getParamNames(self):
		return self.paramNames
	
	def getInitList(self):
		stri = ""
		for param in self.paramNames:
			stri += "%s(%s), " % (param, param)
		return stri[:-2]

class FunctionImplementation:
	
	def __init__(self, typeName, funcName, paramTypes):
		self.typeName = typeName
		self.funcName = funcName
		self.paramTypes = paramTypes
		
		self.adjustedParamTypes = []
		for type in paramTypes:
			self.adjustedParamTypes.append(adjustDataType(type, True))
		
		self.code = ""
		self.returnType = ""
		
	def buildPostfix(self):
		postfix = ""
		for dataType in self.paramTypes:
			postfix += "__" + dataType.replace("<", "_").replace(">", "_").replace("~", "_")
		return postfix
		
	def getParamTypes(self):
		return self.paramTypes
	
	def getParamsString(self):
		stri = ""
		for i in range(len(self.paramTypes)):
			stri += "%s %s, " % (self.paramTypes[i], self.func.paramNames[i])
		return stri[:-2]
		
	def setReturnType(self, type):
		self.returnType = type
		
	def getReturnType(self):
		return self.returnType
		
	def getTypeName(self):
		return self.typeName
	
	def getFuncName(self):
		return self.funcName
	
	def getFullFuncName(self):
		return self.funcName + self.buildPostfix()
		
	def getDeclName(self):
		return self.getTypeName() + "::" + self.funcName
		
	def getMsgHandlerName(self):
		return self.getFullFuncName() + "_msgHandler"
	
	def getMsgStructName(self):
		return self.getFullFuncName() + "_msgType"
	
	def getMsgStructVars(self):
		stri = ""
		for i in range(len(self.paramTypes)):
			stri += "\t%s %s;\n" % (self.paramTypes[i], self.func.paramNames[i])
		return stri
		
	def getPrototype(self):
		if self.typeName:
			return self.typeName + "::" + self.getFullFuncName() + "(" + ", ".join(self.adjustedParamTypes) + ")"
		else:
			return self.getFullFuncName() + "(" + ", ".join(self.adjustedParamTypes) + ")"
	
	def isImplemented(self):
		return self.code != ""
	
	def getInnerCode(self):
		return self.code
	
	def getFullCode(self):
		return self.code

class CPPOutputCompiler:
	
	def __init__(self, inpCompiler):
		self.inputCompiler = inpCompiler
		self.inputFiles = inpCompiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.projectDir = self.inputCompiler.projectDir
		self.modDir = inpCompiler.modDir
		self.bpRoot = fixPath(os.path.abspath(self.modDir + "../")) + "/"
		self.libsDir = fixPath(os.path.abspath(inpCompiler.modDir + "../libs/cpp/"))
		self.stringCounter = 0;
		self.fileCounter = 0;
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.addDestructorOutput = False
		self.customCompilerFlags = []
		
		self.globalScope = Scope()
		self.classes = {}
		self.classes[""] = CPPClass("", None, False)
		
		# TODO: Get rid of these
		self.implementationRequests = {}
		self.functionTypes = {}
		
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile)
		
		if len(self.compiledFiles) == 0:
			self.mainFile = cppOut
		
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		
		# Import files
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		# This needs to be executed AFTER the imported files have been compiled
		# It'll make sure the files are called in the correct (recursive) order
		self.compiledFilesList.append(cppOut)
		
		# After the dependencies have been compiled, compile itself
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
				self.mainCppFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include <bp_decls.hpp>\n#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
		# Decls file
		fileOut = dirOut + "bp_decls.hpp"
		with open(fileOut, "w") as outStream:
			outStream.write("#ifndef " + "bp__decls__hpp" + "\n#define " + "bp__decls__hpp" + "\n\n")
			
			# Basic data types
			outStream.write("#include <cstdint>\n")
			outStream.write("#include <cstdlib>\n")
			for dataType, definition in dataTypeDefinitions.items():
				outStream.write("typedef %s %s;\n" % (definition, dataType))
			outStream.write("typedef %s %s;\n" % ("const char*", "String"))
			outStream.write("#define %s %s\n" % ("SPtr", "boost::shared_ptr"))
			outStream.write("\n")
			
			for className, classObj in self.classes.items():
				if className:
					if classObj.templateParams:
						outStream.write("template <typename %s> " % (", typename ".join(classObj.templateParams)))
					outStream.write("class BP" + className + ";\n\n")
					
					if classObj.templateParams:
						outStream.write("template <typename %s> " % (", typename ".join(classObj.templateParams)))
					outStream.write("class BPActor" + className + ";\n\n")
					
					if classObj.templateParams:
						outStream.write("template <typename %s> " % (", typename ".join(classObj.templateParams)))
					outStream.write("class BPActorWrapper" + className + ";\n\n")
			
			for impl in self.implementationRequests.values():
				protoType = impl.getPrototype()
				if protoType.startswith("::"):
					protoType = protoType[2:]
					reqName = impl.getDeclName()
					funcType = self.functionTypes[reqName + impl.buildPostfix()]
					outStream.write("inline " + funcType + " " + protoType + ";\n")
					
			outStream.write("\n#endif\n")
	
	def build(self):
		exe = stripExt(self.mainCppFile)
		if os.path.isfile(exe):
			os.unlink(exe)
		
#		-march=athlon-xp -O3 -fexpensive-optimizations 
#		-funroll-loops -frerun-cse-after-loop -frerun-loop-opt 
#		-fomit-frame-pointer -fschedule-insns2 -minline-all-stringops 
#		-mfancy-math-387 -mfp-ret-in-387 -m3dnow -msse -mfpmath=sse -mmmx 
#		-malign-double -falign-functions=4 -preferred-stack-boundary=4
#		-fforce-addr -pipe
		compilerName = "g++"
		
		# Compiler
		ccCmd = [
			compilerName,
			"-c",
			self.mainCppFile,
			"-o%s" % (exe + ".o"),
			"-I" + self.outputDir,
			"-I" + self.modDir,
			"-I" + self.bpRoot + "include/cpp/",
			#"-L" + self.libsDir,
			"-std=c++0x",
			"-pipe",
			#"-funroll-loops",
			#"-frerun-cse-after-loop",
			#"-frerun-loop-opt",
			#"-ffast-math",
			"-Wall",
			#"-O3"
		]
		
		# Linker
		linkCmd = [
			compilerName,
			"-o%s" % (exe),
			exe + ".o",
			"-L" + self.libsDir,
			#"-ltheron",
			#"-lboost_thread",
			#"-lpthread"
		] + self.customCompilerFlags
		
		try:
			print("\nStarting compiler:")
			print(" \\\n ".join(ccCmd))
			#print("\n" + " ".join(ccCmd))
			procCompile = subprocess.Popen(ccCmd)
			procCompile.wait()
			
			print("\nStarting linker:")
			print("\n ".join(linkCmd))
			#print("\n" + " ".join(linkCmd))
			procLink = subprocess.Popen(linkCmd)
			procLink.wait()
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
		self.codeNode = getElementByTagName(self.root, "code")
		self.headerNode = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.headerNode, "dependencies")
		self.strings = getElementByTagName(self.headerNode, "strings")
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		self.classes = dict()
		self.classes[""] = CPPClass("", self, False)
		self.compiler.classes[""].cppFile = self
		
		self.currentClass = self.compiler.classes[""]
		self.currentFunction = None
		self.currentTemplateParams = {}
		
		self.inUnmanaged = 0
		self.inTypeDeclaration = 0
		self.inConst = False
		self.inClass = False
		self.inFunction = False
		self.inGetter = False
		self.inSetter = False
		self.inExtern = False
		self.inOperators = False
		self.inOperator = False
		
		self.callDepth = 0
		
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
		self.actorClassesHeader = ""
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
		
		#self.header += "\n#define String const char *\n"
		
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
				self.varsHeader += "const " + var.getFullPrototype([]) + " = " + var.value + ";\n";
			else:
				self.varsHeader += var.getFullPrototype([]) + ";\n";
		
		#print(self.getCode())
		#print("\nFunctions:")
		#print("\n".join(self.compiler.implementationRequests))
		
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
			elif node.tagName == "function" or node.tagName == "operator":
				self.handleFunction(node)
			elif node.tagName == "extern":
				self.inExtern += 1
				self.findDefinitions(node)
				self.inExtern -= 1
			elif node.tagName == "operators":
				self.inOperators += 1
				self.findDefinitions(node)
				self.inOperators -= 1
			elif node.tagName == "extern-function":
				self.handleExternFunction(node)
		
	def parseExpr(self, node):
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_" + node.nodeValue
			else:
				return node.nodeValue
		
		tagName = node.tagName
		
		if tagName == "value":
			return self.parseExpr(node.childNodes[0])
		elif tagName == "access":
			return self.handleAccess(node)
		elif tagName == "assign":
			return self.handleAssign(node)
		elif tagName == "call":
			return self.handleCall(node)
		elif tagName == "if-block" or tagName == "try-block":
			return self.parseChilds(node, "", "")
		elif tagName == "else":
			return self.handleElse(node)
		elif tagName == "index":
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			index = self.parseExpr(node.childNodes[1].childNodes[0])
			
			memberFunc = "[]"
			virtualIndexCall = parseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
			#print(virtualIndexCall.toprettyxml())
			
			return self.handleCall(virtualIndexCall)
		elif tagName == "class":
			return ""
		elif tagName == "function" or tagName == "operator":
			if self.currentClass.name == "":
				return ""
			return self.handleFunction(node)
		elif tagName == "extern":
			return ""
		elif tagName == "operators":
			return self.parseChilds(node, "", "")
		elif tagName == "extern-function":
			return ""
		elif tagName == "target":
			return self.handleTarget(node)
		elif tagName == "new":
			return self.handleNew(node)
		elif tagName == "return":
			return self.handleReturn(node)
		elif tagName == "for":
			return self.handleFor(node)
		elif tagName == "include":
			self.header += "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			return ""
		elif tagName == "const":
			return self.handleConst(node)
		elif tagName == "break":
			return "break"
		elif tagName == "continue":
			return "continue"
		elif tagName == "get" or tagName == "set":
			return self.parseChilds(node, "", "")
		elif tagName == "getter":
			self.inGetter = True
			result = self.handleFunction(node)
			self.inGetter = False
			return result
		elif tagName == "setter":
			self.inSetter = True
			result = self.handleFunction(node)
			self.inSetter = False
			return result
		elif tagName == "template":
			return self.handleTemplate(node)
		elif node.tagName == "template-call":
			return self.handleTemplateCall(node)
		elif node.tagName == "declare-type":
			return self.handleTypeDeclaration(node)
		elif node.tagName == "unmanaged":
			return self.handleUnmanaged(node)
		elif node.tagName == "compiler-flags":
			return self.parseChilds(node, "", "")
		elif node.tagName == "compiler-flag":
			return self.handleCompilerFlag(node)
		elif tagName == "noop":
			return ""
		
		# Check parameterized blocks
		if tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			condition = self.parseExpr(getElementByTagName(node, paramTagName).childNodes[0])
			
			self.pushScope()
			code = self.parseChilds(getElementByTagName(node, codeTagName), "\t" * self.currentTabLevel, ";\n")
			self.popScope()
			
			return keywordName + "(" + condition + ") {\n" + code + "\t" * self.currentTabLevel + "}"
		
		# Check operators
		for opLevel in self.compiler.inputCompiler.parser.operatorLevels:
			for op in opLevel.operators:
				if tagName == op.name:
					if op.type == Operator.BINARY:
						if op.text == "\\":
							return self.parseBinaryOperator(node, " / ", True)
						return self.parseBinaryOperator(node, " " + op.text + " ", True)
					elif op.type == Operator.UNARY:
						return op.text + "(" + self.parseExpr(node.childNodes[0]) + ")"
		
		return "";
		
	def handleUnmanaged(self, node):
		self.inUnmanaged += 1
		expr = self.parseExpr(node.childNodes[0])
		self.inUnmanaged -= 1
		return expr
		
	def handleTypeDeclaration(self, node):
		self.inTypeDeclaration += 1
		typeName = self.parseExpr(node.childNodes[1])
		varName = self.parseExpr(node.childNodes[0])
		self.inTypeDeclaration -= 1
		
		if varName.startswith("this->"):
			varName = varName[len("this->"):]
			self.currentClass.members[varName] = typeName
			return ""
		
		if self.variableExistsAnywhere(varName):
			raise CompilerException("'" + varName + "' has already been defined as a %s variable of the type '" % (["local", "global"][self.getVariableScopeAnywhere(varName) == self.getTopLevelScope()]) + self.getVariableTypeAnywhere(varName) + "'")
		else:
			#print("Declaring '%s' as '%s'" % (varName, typeName))
			var = CPPVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses)
			self.registerVariable(var)
			return adjustDataType(typeName, True, self.currentClass.templateParams) + " " + varName
			
		return varName
		
	def handleTemplate(self, node):
		self.currentClass.setTemplateParams(self.getParameterList(node))
		
	def handleCompilerFlag(self, node):
		self.compiler.customCompilerFlags.insert(0, node.childNodes[0].nodeValue)
		return ""
		
	def handleTemplateCall(self, node):
		op1 = self.parseExpr(node.childNodes[0])
		op2 = self.parseExpr(node.childNodes[1])
		
		return op1 + "<" + op2 + ">"
		
	def isMemberAccessFromOutside(self, op1, op2):
		op1Type = removeUnmanaged(removeGenerics(self.getExprDataType(op1)))
		#print(("get" + op2.nodeValue.title()) + " -> " + str(self.compiler.classes[op1Type].functions.keys()))
		
		if not op1Type in self.compiler.classes:
			return False
		
		accessingGetter = ("get" + op2.nodeValue.title()) in self.compiler.classes[op1Type].functions
		if isTextNode(op2) and op1Type in self.compiler.classes and (accessingGetter or (op2.nodeValue in self.compiler.classes[op1Type].members)):
			#print(self.currentFunction.getName() + " -> " + varGetter)
			#print(self.currentFunction.getName() == varGetter)
			
			if not (isTextNode(op1) and op1.nodeValue == "self"):
				# Make a virtual call
				return True
		
		return False
				
		
	def handleAccess(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		
		callerType = self.getExprDataType(op1)
		callerClassName = removeUnmanaged(removeGenerics(callerType))
		
		if callerClassName in self.compiler.classes:
			if callerClassName == "MemPointer" and isTextNode(op2) and op2.nodeValue == "data" and isUnmanaged(callerType):
				return "(*%s)" % (self.parseExpr(op1))
			# TODO: Optimize
			# GET access
			isMemberAccess = self.isMemberAccessFromOutside(op1, op2)
			if isMemberAccess:
				#print("Replacing ACCESS with CALL: %s.%s" % (op1.toxml(), "get" + op2.nodeValue.title()))
				getFunc = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (op1.toxml(), "get" + op2.nodeValue.title())).documentElement
				#print(getFunc.toprettyxml())
				return self.handleCall(getFunc)
		
		return self.parseBinaryOperator(node, "->")
		
	def handleAssign(self, node):
		self.inAssignment = True
		
		# Member access (setter)
		op1 = node.childNodes[0].childNodes[0]
		if not isTextNode(op1):
			if op1.tagName == "access":
				accessOp1 = op1.childNodes[0].childNodes[0]
				accessOp2 = op1.childNodes[1].childNodes[0]
				
				# data access from a pointer
				accessOp1Type = self.getExprDataType(accessOp1)
				if removeUnmanaged(removeGenerics(accessOp1Type)) == "MemPointer" and accessOp2.nodeValue == "data" and isUnmanaged(accessOp1Type):
					return "*" + self.parseExpr(accessOp1) + " = " + self.parseExpr(node.childNodes[1])
				
				isMemberAccess = self.isMemberAccessFromOutside(accessOp1, accessOp2)
				if isMemberAccess:
					setFunc = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (accessOp1.toxml(), "set" + accessOp2.nodeValue.title(), node.childNodes[1].childNodes[0].toxml())).documentElement
					return self.handleCall(setFunc)
				#pass
				#variableType = self.getExprDataType(op1)
				#variableClass = self.compiler.classes[removeGenerics(variableType)]
			elif op1.tagName == "index":
				return self.parseExpr(node.childNodes[0]) + " = " + self.parseExpr(node.childNodes[1])
		
		variable = self.parseExpr(node.childNodes[0])
		value = self.parseExpr(node.childNodes[1])
		valueTypeOriginal = self.getExprDataType(node.childNodes[1].childNodes[0])
		
		if variable.startswith("this->"):
			variable = variable[len("this->"):]
			
			if not variable in self.currentClass.members:
				self.currentClass.members[variable] = valueTypeOriginal
		
		variableExisted = self.variableExistsAnywhere(variable)
		
		self.inAssignment = False
		
		if not variableExisted:
			var = CPPVariable(variable, valueTypeOriginal, value, self.inConst, not valueTypeOriginal in nonPointerClasses)
			self.registerVariable(var)
				
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const %s = %s" % (var.getFullPrototype(), value)
			
			#print(variable + " = " + valueTypeOriginal)
		
		declaredInline = (tagName(node.childNodes[0].childNodes[0]) == "declare-type")
		
		if self.getCurrentScope() == self.getTopLevelScope():
			return variable + " = " + value
		elif declaredInline:
			return adjustDataType(self.getVariableTypeAnywhere(variable), True, self.currentClass.templateParams) + " " + variable + " = " + value
		elif variableExisted:
			return variable + " = " + value
		else:
			return var.getFullPrototype(self.currentClass.templateParams) + " = " + value
	
	def handleExternFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		self.compiler.functionTypes[name] = type
		
		return ""
		
	def buildCallPostfix(self, types):
		postfix = ""
		for dataType in types:
			postfix += "__" + dataType.replace("<", "_").replace(">", "_").replace("~", "_")
		return postfix
		
	def handleReturn(self, node):
		expr = self.parseExpr(node.childNodes[0])
		self.currentFunction.returnTypes.append(self.getExprDataTypeClean(node.childNodes[0]))
		return "return " + expr
		
	def handleNew(self, node):
		typeName = self.parseExpr(getElementByTagName(node, "type").childNodes[0])
		params = getElementByTagName(node, "parameters")
		
		# Template params
		className = ""
		pos = typeName.find("<")
		if pos != -1:
			className = removeUnmanaged(typeName[:pos])
			
			# Actor
			if className == "Actor":
				actorBoundClass = removeUnmanaged(removeGenerics(typeName[pos+1:-1]))
				self.compiler.classes[actorBoundClass].usesActorModel = True
			elif className == "MemPointer":
				ptrType = typeName[pos+1:-1]
				if len(params.childNodes) > 1:
					raise CompilerException("Too many parameters for the MemPointer constructor (only size needed)")
				
				paramsString, paramTypes = self.handleParameters(params)
				return "new %s[%s]" % (ptrType, paramsString)
		else:
			className = typeName
		
		paramsString, paramTypes = self.handleParameters(params)
		
		oldClass = self.currentClass
		self.currentClass = self.compiler.classes[className]
		
		# Implement init
		funcName = "init"
		if not funcName in self.currentClass.functions:
			raise CompilerException("Every class needs a constructor called 'init' which doesn't exist in '%s'" % (self.currentClass.name))
		func = self.currentClass.functions[funcName]
		
		self.inClass = True
		
		self.currentTemplateParams = self.getTemplateParams(typeName, className, self.currentClass)
		impl = FunctionImplementation(typeName, funcName, paramTypes)
		impl.code = self.implementFunction(func.node, paramTypes, "\t")
		
		func.addImplementation(impl)
		#func.implementations[self.buildCallPostfix(paramTypes)] = impl
		
		self.inClass = False
		self.currentClass = oldClass
		
		finalTypeName = adjustDataType(typeName, False, self.currentClass.templateParams)
		
		if self.inUnmanaged:
			return "" + finalTypeName + "(" + paramsString + ")"
		else:
			return pointerType + "< " + finalTypeName + " >(new " + finalTypeName + "(" + paramsString + "))"
		
	def handleClass(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		
		self.pushScope()
		self.inClass = True
		self.currentClass = self.classes[name] = self.compiler.classes[name] = CPPClass(name, self, self.inExtern)
		
		code = self.parseChilds(getElementByTagName(node, "code"), "\t", ";\n")
		
		self.currentClass = self.compiler.classes[""]
		self.inClass = False
		self.popScope()
		
		return ""
		
	def handleFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		
		if self.inGetter:
			getElementByTagName(node, "name").childNodes[0].nodeValue = name = "get" + name.title()
		elif self.inSetter:
			getElementByTagName(node, "name").childNodes[0].nodeValue = name = "set" + name.title()
		#elif self.inOperators:
		#	getElementByTagName(node, "name").childNodes[0].nodeValue = name = "operator" + getOperatorName(name)
		
		# Index operator
		name = correctOperators(name)
		
		self.currentClass.functions[name] = CPPFunction(self, node)
		
		#print("Registered " + name)
		return ""
		
	def getCallFunction(self, node):
		if getElementByTagName(node, "function"):
			funcNameNode = getElementByTagName(node, "function").childNodes[0]
		else:
			funcNameNode = getElementByTagName(node, "operator").childNodes[0]
		
		caller = ""
		callerType = ""
		if isTextNode(funcNameNode): #and funcNameNode.tagName == "access":
			funcName = funcNameNode.nodeValue
		else:
			#print("XML: " + funcNameNode.childNodes[0].childNodes[0].toxml())
			callerType = self.getExprDataType(funcNameNode.childNodes[0].childNodes[0])
			caller = self.parseExpr(funcNameNode.childNodes[0].childNodes[0])
			funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
			#print(callerType + "::" + funcName)
		
		return caller, callerType, correctOperators(funcName)
		
	def handleCall(self, node):
		caller, callerType, funcName = self.getCallFunction(node)
		
		callDepthTabs = "\t" * self.callDepth
		#print(callDepthTabs)
		#print(callDepthTabs + "*************************************************************")
		#print(callDepthTabs + " HandleCall: " + callerType + "::" + funcName)
		#print(callDepthTabs + "*************************************************************")
		
		self.callDepth += 1
		
		if caller == "self":
			caller = "this"
		
		callerType = removeUnmanaged(callerType)
		
		if callerType.startswith("Actor<"):
			callerType = callerType[len("Actor<"):-1]
		
		callerClass = removeUnmanaged(removeGenerics(callerType))
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		if callerClass == "MemPointer":
			if funcName == "operatorIndex":
				self.callDepth -= 1
				return caller + "[" + paramsString + "]"
			elif funcName == "free":
				self.callDepth -= 1
				return "delete [] " + caller;
		
		fullName = funcName + self.buildCallPostfix(paramTypes)
		
		implementation = FunctionImplementation(callerType, funcName, paramTypes)
		
		if not funcName.startswith("bp_"):
			if not implementation.getPrototype() in self.compiler.implementationRequests:
				self.compiler.implementationRequests[implementation.getPrototype()] = implementation
				#print("New impl: " + implementation.getPrototype())
				#print("Requested implementation of " + implRequest.getPrototype())
				
#				getter = "get" + funcName.title()
#				setter = "set" + funcName.title()
				if funcName in self.compiler.classes[callerClass].functions:
					func = self.compiler.classes[callerClass].functions[funcName]
#				elif getter in self.compiler.classes[callerClass].functions:
#					func = self.compiler.classes[callerClass].functions[getter]
#				elif setter in self.compiler.classes[callerClass].functions:
#					func = self.compiler.classes[callerClass].functions[setter]
				else:
					raise CompilerException("Function '%s.%s' has not been defined" % (callerClass, funcName))
				
				oldClass = self.currentClass
				self.currentClass = self.compiler.classes[callerClass]
				
				oldFunction = self.currentFunction
				self.currentFunction = self.currentClass.functions[funcName]
				
				if callerType:
					definedInFile = self.currentClass.cppFile
					definedInFile.currentClass = self.currentClass
					definedInFile.currentFunction = self.currentFunction
					
					# Consider template types
					oldParams = definedInFile.currentTemplateParams
					definedInFile.currentTemplateParams = self.getTemplateParams(callerType, callerClass, self.currentClass)
					#print("Current template params: " + str(definedInFile.currentTemplateParams))
					self.callDepth += 1
					implementation.code = definedInFile.implementFunction(func.node, implementation.paramTypes)
					self.callDepth -= 1
					definedInFile.currentTemplateParams = oldParams
					
					definedInFile.currentFunction.addImplementation(implementation)
				else:
					definedInFile = func.file
					definedInFile.currentFunction = self.currentFunction
					#if not self.inClass:
					#	definedInFile.currentTemplateParams = {}
					
					oldParams = definedInFile.currentTemplateParams
					self.callDepth += 1
					implementation.code = definedInFile.implementFunction(func.node, implementation.paramTypes)
					self.callDepth -= 1
					definedInFile.currentTemplateParams = oldParams
					
					definedInFile.currentFunction.addImplementation(implementation)
					definedInFile.functionsHeader += implementation.getFullCode()
					
					#prototype = "inline " + self.compiler.functionTypes[callerType + "::" + fullName] + " " + fullName + "(" + ", ".join(implementation.adjustedParamTypes) + ");\n"
					prototype = "inline " + self.compiler.functionTypes[callerType + "::" + fullName] + " " + implementation.getPrototype() + ";\n"
					self.prototypesHeader += prototype
					
					#if self.oldClass.cppFile != self:
					#	self.oldClass.cppFile.prototypesHeader += prototype
						#self.oldClass.cppFile.functionsHeader += implementation
				
				self.currentFunction = oldFunction
				self.currentClass = oldClass
			
			self.callDepth -= 1
			if callerClass in nonPointerClasses:
				return ["", caller + "."][caller != ""] + fullName + "(" + paramsString + ")"
			else:
				return ["", caller + "->"][caller != ""] + fullName + "(" + paramsString + ")"
		else:
			self.callDepth -= 1
			return funcName + "(" + paramsString + ")"
		
	def getTemplateParams(self, callerType, callerClass, mappingClass):
		templateParams = callerType[len(callerClass) + 1: -1]
		return mappingClass.mapTemplateParams(templateParams)
		
	def getSelfType(self):
		stri = ""
		for param in self.currentTemplateParams.values():
			stri += param + ", "
		
		if len(stri) > 2:
			return self.currentClass.name + "<" + stri[:-2] + ">"
		
		return self.currentClass.name
		
	def implementFunction(self, node, types, tabLevel = ""):
		oldGetter = self.inGetter
		oldSetter = self.inSetter
		oldOperator = self.inOperator
		
		if node.tagName == "getter":
			self.inGetter = True
		elif node.tagName == "setter":
			self.inSetter = True
		elif node.tagName == "operator":
			self.inOperator = True
		
		origName = name = correctOperators(getElementByTagName(node, "name").childNodes[0].nodeValue)
		self.currentFunction = self.currentClass.functions[name]
		
		#callDepthTabs = "\t" * self.callDepth
		#print(callDepthTabs)
		#print(callDepthTabs + "*************************************************************")
		#print(callDepthTabs + " ImplementFunction: " + origName + "(" + ", ".join(types) + ")")
		#print(callDepthTabs + "*************************************************************")
		
		#if self.inClass:
		#	tabLevel *= self.currentTabLevel
		tabLevel = "\t" * self.currentTabLevel
		
		self.pushScope()
		self.getCurrentScope().variables["self"] = CPPVariable("self", self.getSelfType(), "", False, True)
		#print(" - Implementing function " + name)
		#print("self : " + self.getCurrentScope().variables["self"].type)
		
		# TODO: Do we need this?
		# Add class member to scope
		#for memberName, memberType in self.currentClass.members.items():
		#	self.getCurrentScope().variables[memberName] = CPPVariable(memberName, memberType, "", False, (not memberType in nonPointerClasses))
		
		#for var in self.getCurrentScope().variables.values():
		#	print(var.name + " ->" + var.type)
		
		self.inFunction = True
		self.currentFunction.returnTypes = []
		
		parameters, funcStartCode = self.getParameterDefinitions(getElementByTagName(node, "parameters"), types)
		code = self.parseChilds(getElementByTagName(node, "code"), tabLevel + "\t", ";\n")
		
		self.inFunction = False
		self.popScope()
		
		funcReturnType = self.getFunctionReturnType()
		
		# Translate the return type if it's a template data type
		funcReturnTypeTranslated = self.translateTemplateParam(funcReturnType, self.currentTemplateParams)
		
		name = self.currentClass.name + "::" + name
		
		#print("%s (Name + Postfix) of type '%s' " % (name + self.buildCallPostfix(types), funcReturnType))
		for i in range(len(types)):
			#print(types[i])
			types[i] = self.translateTemplateParam(types[i], self.currentTemplateParams)
		
		self.compiler.functionTypes[name + self.buildCallPostfix(types)] = funcReturnTypeTranslated
		
		funcName = adjustDataType(funcReturnType, True, self.currentClass.templateParams) + " " + origName + self.buildCallPostfix(types)
		if name == self.currentClass.name + "::init":
			funcName = "BP" + self.currentClass.name
		
		self.inGetter = oldGetter
		self.inSetter = oldSetter
		self.inOperator = oldOperator
		
		return "inline " + funcName + "(" + parameters + ") {\n" + funcStartCode + code + tabLevel + "}\n\n"
#		if self.inClass:
#			return tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#		else:
#			self.functionsHeader += tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#			return ""
		
	def translateTemplateParam(self, type, templateParams):
		#print("Translating " + type)
		pos = 0
		postFixCount = 0
		
		if type in templateParams:
			return templateParams[type]
		
		type = "<" + type + ">"
		
		# Replace template types in generics
		while 1:
			pos = type.find('<', pos)
			if pos == -1:
				break
			postFixCount += 1
			typeName = type[pos+1:-postFixCount]
			className = removeUnmanaged(removeGenerics(typeName))
			
			#print(" " + type)
			#print(" " + className)
			#print(" " + str(templateParams))
			
			if className in templateParams:
				type = type[:pos+1] + templateParams[className] + type[-postFixCount:]
				
			pos += 1
		
		#print("To " + type[1:-1])
		#print("")
		return type[1:-1]
		
	def getFunctionReturnType(self):
		heaviest = None
		
		for type in self.currentFunction.returnTypes:
			if type in dataTypeWeights:
				heaviest = self.heavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def handleFor(self, node):
		fromNodeContent = getElementByTagName(node, "from").childNodes[0]
		fromType = self.getExprDataType(fromNodeContent)
		
		iterExpr = self.parseExpr(getElementByTagName(node, "iterator").childNodes[0])
		fromExpr = self.parseExpr(fromNodeContent)
		toExpr = self.parseExpr(getElementByTagName(node, "to").childNodes[0])
		#stepExpr = self.parseExpr(getElementByTagName(node, "step").childNodes[0])
		
		self.pushScope()
		var = CPPVariable(iterExpr, fromType, fromExpr, False, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = fromType + " "
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return "for(%s%s = %s; %s <= %s; ++%s) {\n%s%s}" % (typeInit, iterExpr, fromExpr, iterExpr, toExpr, iterExpr, code, "\t" * self.currentTabLevel)
		
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return " else {\n" + code + "\t" * self.currentTabLevel + "}"
		
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName():
			return self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		
	def handleString(self, node):
		id = self.id + "_" + node.getAttribute("id")
		value = node.childNodes[0].nodeValue
		line = id + " = \"" + value + "\";\n"
		self.getTopLevelScope().variables[id] = CPPVariable(id, "String", value, False, False)
		self.compiler.stringCounter += 1
		return line
		
	def handleParameters(self, pNode):
		pList = ""
		pTypes = []
		for node in pNode.childNodes:
			paramType = self.getExprDataType(node.childNodes[0])
			paramType = self.translateTemplateParam(paramType, self.currentTemplateParams)
			pList += self.parseExpr(node.childNodes[0]) + ", "
			pTypes.append(paramType)
		
		return pList[:len(pList)-2], pTypes
	
	def handleConst(self, node):
		self.inConst = True
		expr = self.handleAssign(node.childNodes[0])
		self.inConst = False
		
		return expr
		
	def registerVariable(self, var):
		#print("Registered variable '" + var.name + "' of type '" + var.type + "'")
		self.getCurrentScope().variables[var.name] = var
		if self.getCurrentScope() == self.getTopLevelScope():
			self.compiler.globalScope.variables[var.name] = var
	
	def getParameterList(self, pNode):
		pList = []
		
		for node in pNode.childNodes:
			pList.append(self.parseExpr(node.childNodes[0]))
		
		return pList
	
	def getParameterDefinitions(self, pNode, types):
		pList = ""
		funcStartCode = ""
		counter = 0
		typesLen = len(types)
		
		for node in pNode.childNodes:
			name = self.parseExpr(node.childNodes[0])
			
			# Not enough parameters
			if counter >= typesLen:
				raise CompilerException("You forgot to specify the parameter '%s' of the function '%s'" % (name, self.currentFunction.getName()))
			
			usedAs = types[counter]
			if name.startswith("this->"):
				member = name[len("this->"):]
				self.currentClass.members[member] = usedAs
				name = "__" + member
				funcStartCode += "\t" * self.currentTabLevel + "this->" + member + " = " + name + ";\n"
			
			self.currentFunction.paramNames.append(name)
			
			pList += adjustDataType(usedAs) + " " + name + ", "
			
			declaredInline = (tagName(node.childNodes[0]) == "declare-type")
			if not declaredInline:
				self.getCurrentScope().variables[name] = CPPVariable(name, usedAs, "", False, not usedAs in nonPointerClasses)
			else:
				definedAs = self.getVariableTypeAnywhere(name)
				if definedAs != usedAs:
					if definedAs in nonPointerClasses and usedAs in nonPointerClasses:
						heavier = self.heavierOperator(definedAs, usedAs)
						if usedAs == heavier:
							compilerWarning("Information might be lost by converting '%s' to '%s' for the parameter '%s' in the function '%s'" % (usedAs, definedAs, name, self.currentFunction.getName()))
					else:
						raise CompilerException("'%s' expects the type '%s' where you used the type '%s' for the parameter '%s'" % (self.currentFunction.getName(), definedAs, usedAs, name))
			
			counter += 1
		
		return pList[:len(pList)-2], funcStartCode
	
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
		elif os.path.isfile(gImportedFile):
			modPath = gImportedFile
		elif os.path.isfile(gImportedInFolder):
			modPath = gImportedInFolder
		
		if modPath.startswith(self.compiler.projectDir):
			modPath = modPath[len(self.compiler.projectDir):]
		elif modPath.startswith(self.compiler.modDir):
			modPath = modPath[len(self.compiler.modDir):]
		
		return "#include <" + stripExt(modPath) + "-out.hpp>\n"
		
	def parseBinaryOperator(self, node, connector, checkPointer = False):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		if op2 == "self":
			op2 = "this"
		
		if op1 == "self":
			op1 = "this"
		
		if checkPointer:
			op1type = self.getExprDataType(node.childNodes[0].childNodes[0])
			print("%s%s%s (%s)" % (op1, connector, op2, op1 + " is a '" + op1type + "'"))
			if (not op1type in nonPointerClasses) and (not isUnmanaged(op1type)) and (not connector == " == "):
				return self.exprPrefix + op1 + "->operator" + connector.replace(" ", "") + "(" + op2 + ")" + self.exprPostfix
		
		if connector != " / ":
			return self.exprPrefix + op1 + connector + op2 + self.exprPostfix
		else:
			return self.exprPrefix + "float(" + op1 + ")" + connector + op2 + self.exprPostfix
		
	def getCombinationResult(self, operation, operatorType1, operatorType2):
		if operatorType1 in dataTypeWeights and operatorType2 in dataTypeWeights:
			if operation == "divide":
				dataType = self.heavierOperator(operatorType1, operatorType2)
				if dataType == "Double":
					return dataType
				else:
					return "Float"
			else:
				return self.heavierOperator(operatorType1, operatorType2)
		else:
			if operatorType1.startswith("~MemPointer"):
				if operation == "index":
					return operatorType1[len("~MemPointer<"):-1]
				return self.getCombinationResult(operation, "Size", operatorType2)
			if operatorType2.startswith("~MemPointer"):
				return self.getCombinationResult(operation, operatorType1, "Size")
			
			# TODO: Remove temporary fix
			if operation == "index" and operatorType1.startswith("Array<"):
				return operatorType1[len("Array<"):-1]
			
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
		
	def heavierOperator(self, operatorType1, operatorType2):
		if operatorType1 is None:
			return operatorType2
		if operatorType2 is None:
			return operatorType1
		
		weight1 = dataTypeWeights[operatorType1]
		weight2 = dataTypeWeights[operatorType2]
		
		if weight1 > weight2:
			return operatorType1
		else:
			return operatorType2
		
	def getExprDataType(self, node):
		dataType = self.getExprDataTypeClean(node)
		if dataType in self.currentTemplateParams:
			return self.currentTemplateParams[dataType]
		else:
			return dataType
		
	def getExprDataTypeClean(self, node):
		if isTextNode(node):
			if node.nodeValue.isdigit():
				return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("bp_string_"):
				return "String"
			elif node.nodeValue == "True" or node.nodeValue == "False":
				return "Bool"
			else:
				return self.getVariableTypeAnywhere(node.nodeValue)
		else:
			# Binary operators
			if node.tagName == "new":
				typeNode = getElementByTagName(node, "type").childNodes[0]
				
				if isTextNode(typeNode):
					return typeNode.nodeValue
				else:
					# Template parameters
					return self.parseExpr(typeNode)
					#return typeNode.childNodes[0].childNodes[0].nodeValue
			elif node.tagName == "call":
				if self.inFunction:
					# Recursive functions: Try to guess
					if self.currentFunction and getElementByTagName(node, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							raise CompilerException("Unknown data type for recursive call: " + self.currentFunction.getName())
						
				return self.getCallDataType(node)
			elif node.tagName == "access":
				callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
				callerClassName = removeUnmanaged(removeGenerics(callerType))
				callerClass = self.compiler.classes[callerClassName]
				memberName = node.childNodes[1].childNodes[0].nodeValue
				
				if memberName in callerClass.members:
					memberType = callerClass.members[memberName]
					templateParams = self.getTemplateParams(callerType, callerClassName, callerClass)
#					print(memberType)
#					print(callerType)
#					print(callerClassName)
#					print(self.currentTemplateParams)
#					print(templateParams)
#					print("-----")
					return self.translateTemplateParam(memberType, templateParams)
				else:
					# data access from a pointer
					if callerClassName == "MemPointer" and memberName == "data":
						return callerType[callerType.find('<')+1:-1]
					
					memberFunc = "get" + memberName.title()
					virtualGetCall = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc)).documentElement
					return self.getCallDataType(virtualGetCall)
				
#				templatesUsed = (callerClassName != callerType)
#				
#				if templatesUsed:
#					templateParams = callerType[len(callerClassName) + 1: -1]
#					translateTemplateParams = callerClass.mapTemplateParams(templateParams)
#					
#					if memberType in translateTemplateParams:
#						return translateTemplateParams[memberType]
#					else:
#						return memberType
#				else:
#					return memberType
			elif node.tagName == "unmanaged":
				self.inUnmanaged += 1
				expr = self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
				self.inUnmanaged -= 1
				return "~" + expr
			elif node.tagName == "negative":
				return self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
			elif len(node.childNodes) == 2:
				op1 = node.childNodes[0].childNodes[0]
				op2 = node.childNodes[1].childNodes[0]
				
				if self.inFunction and self.currentFunction:
					# Recursive functions: Try to guess
					if tagName(op2) == "call" and getElementByTagName(op2, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							return self.getExprDataType(op1)
					elif tagName(op1) == "call" and getElementByTagName(op1, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							return self.getExprDataType(op2)
				
				return self.getCombinationResult(node.tagName, self.getExprDataType(op1), self.getExprDataType(op2))
			
		raise CompilerException("Unknown data type for: " + node.toxml())
		
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getCallFunction(node)
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		
		if not funcName.startswith("bp_"):
			funcName += self.buildCallPostfix(paramTypes)
			
			callerClassName = removeUnmanaged(removeGenerics(callerType))
			
#			templatesUsed = 0
#			if callerClassName != callerType:
#				templatesUsed = 1
#				callerClass = self.compiler.classes[callerClassName]
#				templateParams = callerType[len(callerClassName) + 1: -1]
#				translateTemplateParams = callerClass.mapTemplateParams(templateParams)
			
			# data access from a pointer
			if callerClassName == "MemPointer" and funcName == "getData":
				return callerType[callerType.find('<')+1:-1]
			
			if not (callerClassName + "::" + funcName) in self.compiler.functionTypes:
				raise CompilerException("Function '" + (callerClassName + "::" + funcName) + "' has not been defined")
			
			return self.compiler.functionTypes[callerClassName + "::" + funcName]
#			if templatesUsed:
#				param = self.compiler.functionTypes[callerClassName + "::" + funcName]
#				if param in translateTemplateParams:
#					return translateTemplateParams[param]
#				else:
#					return param
#			else:
#				return self.compiler.functionTypes[callerClassName + "::" + funcName]
		else:
			if not (funcName) in self.compiler.functionTypes:
				raise CompilerException("Function '" + funcName + "' has not been defined")
			
			return self.compiler.functionTypes[funcName]
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			return var.type
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope.variables[name].type
		
		#print(self.getTopLevelScope().variables)
		#print(self.compiler.globalScope.variables)
		if name in self.compiler.classes:
			raise CompilerException("You forgot to create an instance of the class '" + name + "' by using brackets")
		raise CompilerException("Unknown variable: " + name)
		
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope
		
		raise CompilerException("Unknown variable: " + name)
		
	def variableExistsAnywhere(self, name):
		if self.variableExists(name) or (name in self.compiler.globalScope.variables) or (name in self.currentClass.members):
			#print(name + " exists")
			return 1
		#print(name + " doesn't exist")
		return 0
		
	def implementActorClasses(self):
		prefix = "BP"
		actorPrefix = "BPActor"
		wrapperPrefix = "BPActorWrapper"
		actorInit = ""
		wrapperInit = ""
		
		for classObj in self.classes.values():
			if classObj.name != "" and classObj.usesActorModel and not classObj.isExtern:
				code = ""
				wrapperCode = ""
				structCode = ""
				actorClassName = actorPrefix + classObj.name
				wrapperClassName = wrapperPrefix + classObj.name
				
				actorInit = "%s() {\n" % (actorClassName)
				wrapperInit = "%s() : actorRef(theronFramework.CreateActor< %s >()) {\n" % (wrapperClassName, actorPrefix + classObj.getNameWithTemplates())
				
				for func in classObj.functions.values():
					if func.getName() != "init":
						for impl in func.implementations.values():
							# Call parameters
							callParams = ""
							if func.getParamNames():
								callParams = ("message." + ", message.".join(func.getParamNames()))
							paramsString = impl.getParamsString()
							initList = ""
							if paramsString:
								initList = " : %s" % (func.getInitList())
							
							# Msg struct
							structCode += "struct %s {\n%s" % (impl.getMsgStructName(), impl.getMsgStructVars())
							structCode += "\t%s(%s)%s {}\n" % (impl.getMsgStructName(), paramsString, initList)
							structCode += "};\n"
							
							# Msg handler
							code += "\tinline void %s(const %s &message, const Theron::Address from) {\n\t\t" % (impl.getMsgHandlerName(), impl.getMsgStructName())
							code += "this->sequentialObj.%s(%s);" % (impl.getFullFuncName(), callParams)
							code += "\n\t}\n\n"
							
							# Msg sender
							wrapperCode += "\tinline void %s(%s) {\n\t\t" % (impl.getFullFuncName(), paramsString)
							wrapperCode += "this->actorRef.Push(%s(%s), theronReceiver.GetAddress());" % (impl.getMsgStructName(), ", ".join(func.getParamNames()))
							wrapperCode += "\n\t}\n\n"
							
							# Register the msg handler
							actorInit += "\t\tRegisterHandler(this, &%s::%s);\n" % (actorClassName, impl.getMsgHandlerName())
				
				actorInit += "\t}"
				wrapperInit += "\t}"
				
				code += "\t" + actorInit + "\n"
				wrapperCode += "\t" + wrapperInit + "\n"
				
				# Private members
				code += "private:\n"
				code += "\t%s sequentialObj;\n" % (prefix + classObj.getNameWithTemplates())
				
				wrapperCode += "private:\n"
				wrapperCode += "\tTheron::ActorRef actorRef;\n"
				
				# Structs
				self.actorClassesHeader += structCode + "\n"
				
				# Templates
				if classObj.templateParams:
					self.actorClassesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
				
				# Add code to classes header
				self.actorClassesHeader += "class " + actorClassName + ": public Theron::Actor " + ("{\npublic:\n" + code + "};\n")
				
				self.actorClassesHeader += "\n"
				
				# Templates
				if classObj.templateParams:
					self.actorClassesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
				
				# Add code to classes header
				self.actorClassesHeader += "class " + wrapperClassName + " " + ("{\npublic:\n" + wrapperCode + "};\n\n")
				
	def implementClasses(self):
		prefix = "BP"
		
		for classObj in self.classes.values():
			if classObj.name != "" and not classObj.isExtern:
				code = ""
				
				# Functions
				for func in classObj.functions.values():
					for impl in func.implementations.values():
						code += "\t" + impl.getFullCode() + "\n"
				
				# Destructor
				if self.compiler.addDestructorOutput:
					code += "~" + prefix + classObj.name + "() {bp_print(\"Destructed " + classObj.name + "\");}"
					code += "\n"
				
				# Private members
				code += "private:\n"
				for memberName, memberType in classObj.members.items():
					code += "\t" + adjustDataType(memberType, True, classObj.templateParams) + " " + memberName + ";\n"
				
				code += "\t\n"
				
				# Templates
				if classObj.templateParams:
					self.classesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
				
				# Add code to classes header
				self.classesHeader += "// %s\nclass %s" % (classObj.name, prefix + classObj.name) + " {\npublic:\n" + code + "};\n\n"
		
	def getCode(self):
		self.implementClasses()
		self.implementActorClasses()
		
		return self.header + self.typeDefsHeader + self.prototypesHeader + self.varsHeader + self.classesHeader + self.actorClassesHeader + self.functionsHeader + "\n" + self.topLevel + "\n" + self.footer

####################################################################
# Functions
####################################################################
def correctOperators(sign):
	if sign == "[]":
		return "operatorIndex"
	
	return sign

def isUnmanaged(type):
	return type.startswith("~")

def removeUnmanaged(type):
	return type.replace("~", "")

def replaceActorGenerics(type, actorPrefix):
	while 1:
		posActor = type.find('Actor<')
		if posActor != -1:
			type = actorPrefix + type[posActor + len('Actor<'):-1]
		else:
			break
	return type

def adjustDataType(type, adjustOuterAsWell = True, templateParams = []):
	if type == "void" or type in nonPointerClasses or type in templateParams:
		return type
	
	# Adjust template params
	pos = type.find('<')
	postFixCount = 0
	typeName = ""
	className = ""
	standardClassPrefix = "BP"
	actorPrefix = "ActorWrapper"
	
	classPrefix = pointerType + "<" + standardClassPrefix
	classPostfix = ">"
	
	# Actors
	type = replaceActorGenerics(type, actorPrefix)
	
	if adjustOuterAsWell:
		if pos != -1:
			className = type[:pos]
		else:
			className = type
		
		classNameClean = removeUnmanaged(className)
		if (not classNameClean in nonPointerClasses) and (not classNameClean in templateParams):
			# Unmanaged
			if className.startswith("~"):
				if classNameClean == "MemPointer":
					innerType = type[pos+1:-1]
					innerClass = removeUnmanaged(removeGenerics(innerType))
					#debugStop()
					if innerClass in nonPointerClasses or innerClass in templateParams:
						type = innerType + "*"
						postFixCount += 1
						pos = 0
					else:
						type = classPrefix + innerType + classPostfix + "*"
						postFixCount += len(classPostfix) + 1
						pos += len(classPrefix)
				else:
					type = standardClassPrefix + type[1:]
			else:
				pos += len(classPrefix)
				postFixCount += len(classPostfix)
				type = classPrefix + type + classPostfix
	else:
		type = standardClassPrefix + type
	
	while 1:
		pos = type.find('<', pos)
		if pos == -1:
			break
		postFixCount += 1
		typeName = type[pos+1:-postFixCount]
		className = removeUnmanaged(removeGenerics(typeName))
		
		if className in nonPointerClasses or className in templateParams:
			pos += 1
		else:
			type = type[:pos+1] + classPrefix + type[pos+1:-postFixCount] + classPostfix + type[-postFixCount:]
			
			# Because of the postfix pointer sign
			postFixCount += 1
			
			# Because of the prefixes
			pos += len(classPrefix) + len(classPostfix) + 1
	
	return type.replace("<", "< ").replace(">", " >")
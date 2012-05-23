####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2011  Eduard Urbach
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
from bp.Compiler.ExpressionParser import *
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from bp.Compiler.Output.BaseOutputFile import *
from bp.Compiler.Output.cpp.datatypes import *
from bp.Compiler.Output.cpp.CPPClass import *
from bp.Compiler.Output.cpp.CPPFunction import *
from bp.Compiler.Output.cpp.CPPVariable import *
from bp.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Classes
####################################################################
class CPPOutputFile(BaseOutputFile):
	
	def __init__(self, compiler, file, root):
		self.currentTabLevel = 0
		
		BaseOutputFile.__init__(self, compiler, file, root)
		
		self.localClasses = []
		self.localFunctions = []
		self.additionalCodePerLine = []
		self.customThreads = dict()
		self.customThreadsString = ""
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"]
		}
		
		# Inserted for mathematical expressions
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		# String class
		self.stringClassDefined = False
		
		# Codes
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.body = ""
		self.footer = "#endif\n"
		
		# Other code types
		self.stringsHeader = "\t// Strings\n";
		self.varsHeader = "\n// Variables\n";
		self.functionsHeader = "// Functions\n"
		self.classesHeader = ""
		self.actorClassesHeader = ""
		self.prototypesHeader = "\n// Prototypes\n"
		
		# Debugging
		self.lastParsedNode = list()
		
		# Memory management
		self.useGC = True
		self.useReferenceCounting = False
		
		# Syntax
		self.lineLimiter = ";\n"
		self.myself = "this"
		self.trySyntax = "try {\n%s\n\t}"
		self.catchSyntax = " catch (%s) {\n%s\n\t}"
		self.returnSyntax = "return %s"
		self.memberAccessSyntax = "this->"
		self.parameterSyntax = "%s %s, "
		self.newObjectSyntax = "(new %s(%s))"
		self.binaryOperatorSyntax = "%s%s%s%s%s"
		self.binaryOperatorDivideSyntax = "%sfloat(%s)%s%s%s"
		
	def handleCompilerFlag(self, node):
		flag = node.childNodes[0].nodeValue
		if flag.startswith("-l"):
			self.compiler.customLinkerFlags.insert(0, flag)
		else:
			self.compiler.customCompilerFlags.insert(0, flag)
		return ""
		
	def compile(self):
		print("Compiling: " + self.file)
		
		# Check whether string class has been defined or not
		# NOTE: This has to be called before self.scanAhead is executed.
		self.stringClassDefined = self.classExists("UTF8String")
		
		# Find classes, functions, operators and external stuff
		self.scanAhead(self.codeNode)
		
		# Implement operator = of the string class manually to enable assignments
		if self.compiler.needToInitStringClass:
			#self.implementFunction("UTF8String", correctOperators("="), ["~MemPointer<ConstChar>"])
			self.implementFunction("UTF8String", "init", [])
			self.implementFunction("UTF8String", "init", ["~MemPointer<Byte>"])
			self.compiler.needToInitStringClass = False
		
		if self.classExists("UTF8String") and self.stringClassDefined == False:
			self.compiler.needToInitStringClass = True
		
		# Header
		self.header += "// Includes\n"
		self.header += "#include <bp_decls.hpp>\n"
		for node in self.dependencies.childNodes:
			if isElemNode(node) and node.tagName == "import":
				self.header += self.handleImport(node)
		
		# Strings
		for node in self.strings.childNodes:
			self.stringsHeader += "\t" + self.handleString(node)
		self.stringsHeader += "\n"
		
		# Top level code
		self.body += "// Module execution\n"
		self.body += "void exec_" + self.id + "() {\n"
		self.body += self.stringsHeader
		self.body += "\t// Code\n"
		self.body += self.parseChilds(self.codeNode, "\t" * self.currentTabLevel, ";\n")
		self.body += "}\n"
		
		# Custom Threads
		self.customThreadsString = '\n'.join(self.customThreads.values()) + '\n'
		
		# Variables
		for var in self.getTopLevelScope().variables.values():
			if var.isConst:
				self.varsHeader += "const " + var.getPrototype() + " = " + var.value + ";\n";
			elif not isUnmanaged(var.type) or var.type == self.compiler.stringDataType:
				self.varsHeader += var.getPrototype() + ";\n";
				
		self.varsHeader += "\n"
	
	def createVariable(self, name, type, value, isConst, isPointer, isPublic):
		return CPPVariable(name, type, value, isConst, isPointer, isPublic)
		
	def handleAssign(self, node):
		self.inAssignment += 1
		isSelfMemberAccess = False
		
		# Member access (setter)
		op1 = node.childNodes[0].childNodes[0]
		if not isTextNode(op1):
			if op1.tagName == "access":
				accessOp1 = op1.childNodes[0].childNodes[0]
				accessOp2 = op1.childNodes[1].childNodes[0]
				
				# data access from a pointer
				accessOp1Type = self.getExprDataType(accessOp1)
				if extractClassName(accessOp1Type) == "MemPointer" and accessOp2.nodeValue == "data" and isUnmanaged(accessOp1Type):
					return "*" + self.parseExpr(accessOp1) + " = " + self.parseExpr(node.childNodes[1])
				
				isMemberAccess = self.isMemberAccessFromOutside(accessOp1, accessOp2)
				if isMemberAccess:
					#print("Using setter for type '%s'" % (accessOp1type))
					setFunc = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (accessOp1.toxml(), "set" + capitalize(accessOp2.nodeValue), node.childNodes[1].childNodes[0].toxml())).documentElement
					return self.handleCall(setFunc)
				#pass
				#variableType = self.getExprDataType(op1)
				#variableClass = self.compiler.classes[removeGenerics(variableType)]
			elif op1.tagName == "index":
				return self.parseExpr(node.childNodes[0]) + " = " + self.parseExpr(node.childNodes[1])
		
		# Inline type declarations
		declaredInline = (tagName(node.childNodes[0].childNodes[0]) == "declare-type")
		
		# Inline declaration + top level scope = don't include type name
		variableName = self.getNamespacePrefix()
		if declaredInline and self.getCurrentScope() == self.getTopLevelScope():
			variableName += self.handleTypeDeclaration(node.childNodes[0].childNodes[0], insertTypeName = False)
		else:
			variableName += self.parseExpr(node.childNodes[0].childNodes[0])
		
		# In parameter definition?
		if node.parentNode.tagName == "parameter":
			return variableName
		
		# Parse value
		value = self.parseExpr(node.childNodes[1].childNodes[0], False)
		
		# Parse value type
		valueType = self.getExprDataType(node.childNodes[1].childNodes[0])
		if valueType == "void":
			raise CompilerException("'%s' which is assigned to '%s' does not return a value (void)" % (value, variableName))
		
		memberName = variableName
		
		# Did we define a type?
		try:
			variableType = self.getVariableTypeAnywhere(variableName)
		except:
			variableType = ""
		
		# Member access?
		if variableName.startswith("this->"):
			memberName = variableName[len("this->"):]
			isSelfMemberAccess = True
		
		if isSelfMemberAccess:
			var = CPPVariable(memberName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			#if not variableName in self.currentClass.members:
			#	self.currentClass.addMember(var)
			
			if not memberName in self.currentClassImpl.members:
				self.currentClassImpl.addMember(var)
			
			variableExisted = True
		else:
			variableExisted = self.variableExistsAnywhere(variableName)
		
		# Need to register it here?
		if not variableExisted and not declaredInline:
			var = CPPVariable(variableName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			self.registerVariable(var)
			
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const %s = %s" % (var.getFullPrototype(), value)
		
		#else:
		#	var = self.getVariableTypeAnywhere(variableName)
		
		#if not variable in self.currentClassImpl.members:
		#	self.currentClassImpl.add
		
		# Int = BigInt
		if variableType in {"Int", "Int32", "Int64"} and valueType == "BigInt":
			value = "static_cast< %s >( BigInt(%s).get_si() )" % (variableType, value)
		
		self.inAssignment -= 1
		
		#print(node.toprettyxml())
		#print(variableName, "|", variableType, "|", value, "|", valueType)
		
		# Unmanaged types
		if isUnmanaged(valueType) and not variableExisted:
			return var.getPrototype() + "(" + value + ")"
		
		# Casts
		if variableExisted and variableType and variableType != valueType and not valueType in nonPointerClasses and not extractClassName(valueType) == "MemPointer":
			debug("Need to cast %s to %s" % (valueType, variableType))
			#if variableType in nonPointerClasses:
			#	castType = "static_cast"
			#else:
			#	castType = "reinterpret_cast"
			value = "((%s)->to%s())" % (value, normalizeName(variableType))
		
		if self.getCurrentScope() == self.getTopLevelScope():
			return variableName + " = " + value
		elif variableExisted:
			return variableName + " = " + value
		elif declaredInline:
			return variableName + " = " + value #+ ";//Declared inline"
		else:
			return var.getPrototype() + " = " + value
		
		return variableName + " = " + value
		
	def handleTry(self, node):
		codeNode = getElementByTagName(node, "code")
		
		self.pushScope()
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return self.trySyntax % code
		
	def handleCatch(self, node):
		varNode = getElementByTagName(node, "variable")
		codeNode = getElementByTagName(node, "code")
		
		var = self.parseExpr(varNode)
		
		# Declare-type on exceptions
		if not var and varNode.firstChild and varNode.firstChild.nodeType != Node.TEXT_NODE and varNode.firstChild.tagName == "declare-type":
			varName = varNode.firstChild.childNodes[0].childNodes[0].nodeValue
			typeName = varNode.firstChild.childNodes[1].childNodes[0].nodeValue
			
			#print("Registering")
			#print(varName)
			#print(typeName)
			varObject = CPPVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses, False)
			self.registerVariable(varObject)
			
			var = "%s %s" % (adjustDataTypeCPP(typeName), varName)
		
		if not var:
			var = "..."
		
		# Code needs to be compiled AFTER THE EXCEPTION VARIABLE HAS BEEN REGISTERED
		self.pushScope()
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return self.catchSyntax % (var, code)
	
	def createNamespace(self, name):
		return CPPNamespace(name)
		
	# def handleDefine(self, node):
		# self.inDefine += 1
		# code = self.parseChilds(node, "\t" * self.currentTabLevel, ";\n")
		# self.inDefine -= 1
		
		# return code
		
	def handleCall(self, node):
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		
		# For casts
		funcName = self.prepareTypeName(funcName)
		
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		debug(("--> [CALL] " + caller + "." + funcName + "(" + paramsString + ")").ljust(70) + " [my : " + callerType + "]")
		
		callerClassName = extractClassName(callerType)
		#if callerClassName == "void":
		#	raise CompilerException("Function '%s' has no return value" % getElementByTagName(node, "function"))
		callerClass = self.getClass(callerClassName)
		
		# MemPointer.free
		if funcName == "free" and callerClassName == "MemPointer":
			return "delete [] %s" % (caller)
		
		if not self.compiler.mainClass.hasExternFunction(funcName): #not funcName.startswith("bp_"):
			if not funcName in callerClass.functions:
				# Check extended classes
				func = findFunctionInBaseClasses(callerClass, funcName)
				
				if not func:
					if funcName[0].islower():
						raise CompilerException("Function '%s.%s' has not been defined [Error code 1]" % (callerType, funcName))
					else:
						raise CompilerException("Class '%s' has not been defined  [Error code 2]" % (funcName))
			else:
				func = callerClass.functions[funcName]
			
			# Optimized string concatenation
			if self.compiler.optimizeStringConcatenation:
				if funcName == "operatorAdd" and callerType == "UTF8String" and paramTypes[0] in {"UTF8String", "Int"}:
					# Check if above our node is an add node
					op = getElementByTagName(node, "operator")
					secondAddNode = op.firstChild.firstChild.firstChild
					
					if op and op.firstChild.tagName == "access" and tagName(secondAddNode) == "add":
						string1 = secondAddNode.childNodes[0].firstChild
						string2 = secondAddNode.childNodes[1].firstChild
						if string1 and string2:
							# Add one more parameter to the operator
							paramTypes = [self.getExprDataType(string2)] + paramTypes
							paramsString = "%s, %s" % (self.parseExpr(string2), paramsString)
							secondAddNode.parentNode.replaceChild(string1, secondAddNode)
							caller = self.parseExpr(string1)
							# Remove add node
							
						#print(("--> [CALL] " + caller + "." + funcName + "(" + paramsString + ")").ljust(70) + " [my : " + callerType + "]")
			
			# Default parameters
			paramTypes, paramsString = self.addDefaultParameters(callerType, funcName, paramTypes, paramsString)
			
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			fullName = funcImpl.getName()
			
			# Check whether the given parameters match the default parameter types
			#defaultValueTypes = funcImpl.func.getParamDefaultValueTypes()
			#for i in range(len(defaultValueTypes)):
			#	if i >= paramTypesLen:
			#		break
			#	
			#	if defaultValueTypes[i] and paramTypes[i] != defaultValueTypes[i]:
			#		raise CompilerException("Call parameter types don't match the parameter default types of '%s'" % (funcName))
			
			# Parallel
			if self.inParallel >= 0 and node.parentNode and node.parentNode.parentNode and node.parentNode.parentNode.tagName == "parallel":
				threadID = self.compiler.customThreadsCount
				threadFuncID = fullName
				self.buildThreadFunc(threadFuncID, paramTypes)
				self.parallelBlockStack[-1].append(threadID)
				self.compiler.customThreadsCount += 1
				tabs = "\t" * self.currentTabLevel
				
				threadCreation =  "pthread_t bp_threadHandle_%d;\n%s" % (threadID, tabs)
				
				if paramTypes:
					threadCreation += "bp_thread_args_%s* bp_threadArgs_%d = new (NoGC) bp_thread_args_%s(%s);\n%s" % (threadFuncID, threadID, threadFuncID, paramsString, tabs)
					threadCreation += "pthread_create(&bp_threadHandle_%d, NULL, &bp_thread_func_%s, bp_threadArgs_%d);\n%s" % (threadID, threadFuncID, threadID, tabs)
				else:
					threadCreation += "pthread_create(&bp_threadHandle_%d, NULL, &bp_thread_func_%s, reinterpret_cast<void*>(NULL));\n%s" % (threadID, threadFuncID, tabs)
				
				return threadCreation
				
			if (callerClass in nonPointerClasses) or isUnmanaged(callerType):
				return ["::", caller + "."][caller != ""] + fullName + "(" + paramsString + ")"
			else:
				return ["::", caller + "->"][caller != ""] + fullName + "(" + paramsString + ")"
		else:
			return funcName + "(" + paramsString + ")"
		
	def buildThreadFunc(self, funcName, paramTypes):
		count = 0
		params = []
		paramNames = []
		constructorList = []
		initList = []
		
		for typeName in paramTypes:
			nTypeName = adjustDataTypeCPP(typeName)
			params.append(nTypeName)
			params.append(" _%d;\n\t" % count)
			
			constructorList.append("%s __%d" % (nTypeName, count))
			initList.append("_%d(__%d)" % (count, count))
			
			paramNames.append("args->_%d" % count)
			count += 1
		
		if initList:
			initParams = ": " + ', '.join(initList)
		else:
			initParams = ""
		
		func = """
typedef struct bp_thread_args_%s {
	%s
	inline bp_thread_args_%s(%s) %s {}
} bp_thread_args_%s;

void* bp_thread_func_%s(void *bp_arg_struct_void) {
	bp_thread_args_%s *args = reinterpret_cast<bp_thread_args_%s*>(bp_arg_struct_void);
	%s(%s);
	if(args)
		delete args;
	return NULL;
}
""" % (funcName, ''.join(params), funcName, ', '.join(constructorList), initParams, funcName, funcName, funcName, funcName, funcName, ', '.join(paramNames))
		self.customThreads[funcName] = func
		
	def waitCustomThreadsCode(self, block):
		joinCodes = []
		tabs = "\t" * self.currentTabLevel
		for threadID in block:
			joinCodes.append("\n%spthread_join(bp_threadHandle_%d, NULL);" % (tabs, threadID))
		return ''.join(joinCodes)
		
	def adjustDataType(self, typeName, adjustOuterAsWell = True):
		return adjustDataTypeCPP(typeName, adjustOuterAsWell)
		
	def addDivisionByZeroCheck(self, op):
		if isNumeric(op):
			if op != "0" and op != "0.0":
				return
			else:
				self.additionalCodePerLine.append('throw new BPDivisionByZeroException()')
				return
		
		self.additionalCodePerLine.append('if(%s == 0) throw new BPDivisionByZeroException()' % op)
	
	def handleFor(self, node):
		fromNodeContent = getElementByTagName(node, "from").childNodes[0]
		toLimiterNode = getElementByTagName(node, "to")
		
		if toLimiterNode:
			toNodeContent = toLimiterNode.childNodes[0]
			operator = "<="
		else:
			toNodeContent = getElementByTagName(node, "until").childNodes[0]
			operator = "<"
		
		fromType = self.getExprDataType(fromNodeContent)
		
		iterExpr = self.parseExpr(getElementByTagName(node, "iterator").childNodes[0])
		fromExpr = self.parseExpr(fromNodeContent)
		toExpr = self.parseExpr(toNodeContent)
		toType = self.getExprDataType(toNodeContent)
		#stepExpr = self.parseExpr(getElementByTagName(node, "step").childNodes[0])
		
		self.pushScope()
		var = CPPVariable(iterExpr, getHeavierOperator(fromType, toType), fromExpr, False, False, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = var.type + " "
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		varDefs = ""
		if not self.variableExistsAnywhere(toExpr):
			toVar = CPPVariable("bp_for_end_%s" % (self.compiler.forVarCounter), toType, "", False, not toType in nonPointerClasses, False)
			#self.getTopLevelScope().variables[toVar.name] = toVar
			self.varsHeader += toVar.type + " " + toVar.name + ";\n"
			varDefs = "%s = %s;\n" % (toVar.name, toExpr)
			varDefs += "\t" * self.currentTabLevel
			toExpr = toVar.name
			self.compiler.forVarCounter += 1
		
		return varDefs + "for(%s%s = %s; %s %s %s; ++%s) {\n%s%s}" % (typeInit, iterExpr, fromExpr, iterExpr, operator, toExpr, iterExpr, code, "\t" * self.currentTabLevel)
	
	def handleFlowTo(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[0].childNodes[0]
		
		op1Expr = self.parseExpr(op1)
		op2Expr = self.parseExpr(op2)
		
		# TODO: Implement data flow
		return op1Expr
	
	def handleTypeDeclaration(self, node, insertTypeName = True):
		self.inTypeDeclaration += 1
		typeName = self.parseExpr(node.childNodes[1], True)
		
		# Typedefs
		typeName = self.prepareTypeName(typeName)
		
		typeName = self.currentClassImpl.translateTemplateName(typeName)
		varName = self.parseExpr(node.childNodes[0])
		self.inTypeDeclaration -= 1
		
		if varName.startswith("this->"):
			memberName = varName[len("this->"):]
			self.currentClassImpl.addMember(CPPVariable(memberName, typeName, "", False, not extractClassName(typeName) in nonPointerClasses, False))
			return varName # ""
		
		variableExists = self.variableExistsAnywhere(varName)
		if variableExists:
			#["local", "global"][self.getVariableScopeAnywhere(varName) == self.getTopLevelScope()]
			for item in self.scopes:
				print(item.variables)
				print("===")
			raise CompilerException("'" + varName + "' has already been defined as a %s variable of the type '" % (["local", "class", "global"][variableExists - 1]) + self.getVariableTypeAnywhere(varName) + "'")
		else:
			#debug("Declaring '%s' as '%s'" % (varName, typeName))
			var = CPPVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses, False)
			self.registerVariable(var)
			
			if insertTypeName:
				return adjustDataTypeCPP(typeName) + " " + varName
			else:
				return varName
	
	def handleConst(self, node):
		self.inConst += 1
		expr = self.handleAssign(node.childNodes[0])
		self.inConst -= 1
		
		return expr
	
	def handleTemplateCall(self, node):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		# Template translation
		op1 = self.currentClassImpl.translateTemplateName(op1)
		op2 = self.currentClassImpl.translateTemplateName(op2)
		
		op2 = self.prepareTypeName(op2)
		
		return op1 + "<" + op2 + ">"
	
	def handleString(self, node):
		id = self.id + "_" + node.getAttribute("id")
		value = decodeCDATA(node.childNodes[0].nodeValue)
		
		# TODO: classExists(self.compiler.stringDataType)
		if self.stringClassDefined:
			dataType = self.compiler.stringDataType
			line = id + " = new BPUTF8String(const_cast<Byte*>(\"" + value + "\"));\n"
		else:
			dataType = "CString"
			line = id + " = const_cast<Byte*>(\"" + value + "\");\n"
		
		var = CPPVariable(id, dataType, value, False, False, True)
		#self.currentClassImpl.addMember(var)
		self.getTopLevelScope().variables[id] = var
		self.compiler.stringCounter += 1
		return line
	
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return " else {\n" + code + "\t" * self.currentTabLevel + "}"
	
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName() or matchesCurrentPlatform(name):
			return self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
	
	def handleImport(self, node):
		#print(node.toprettyxml())
		importedModulePath = node.childNodes[0].nodeValue.strip()
		importedModule = getModulePath(importedModulePath, extractDir(self.file), self.compiler.getProjectDir(), ".bp")
		#print("MODULE: " + importedModule)
		return "#include <" + extractDir(importedModule) + "C++/" + stripAll(importedModule) + ".hpp>\n"
	
	def createClass(self, name, node):
		return CPPClass(name, node)
	
	def createFunction(self, node):
		return CPPFunction(self, node)
	
	def writeFunctions(self):
		for func in self.localFunctions:
			for funcImpl in func.implementations.values():
				self.functionsHeader += "%s\n" % (funcImpl.getFullCode())
	
	def writeClasses(self):
		prefix = "BP"
		
		for classObj in self.localClasses:
			if not classObj.isExtern:
				for classImplId, classImpl in classObj.implementations.items():
					code = ""
					
					# Functions
					for funcImpl in classImpl.funcImplementations.values():
						if funcImpl.getFuncName() == "init":
							code += "\t" + funcImpl.getConstructorCode() + "\n"
						elif funcImpl.getFuncName() == "finalize":
							code += "\t" + funcImpl.getDestructorCode() + "\n"
						else:
							code += "\t" + funcImpl.getFullCode() + "\n"
					
					# Private members
					# TODO: SET IT BACK TO PRIVATE AFTER FIXING FORCE INCLUSION
					code += "public:\n"
					for member in classImpl.members.values():
						#print(member.name + " is of type " + member.type)
						code += "\t" + adjustDataTypeCPP(member.type, True) + " " + member.name + ";\n"
					
					code += "\t\n"
					
					# Templates
					templatePrefix = ""
					templatePostfix = ""
					if classObj.templateNames:
						templatePrefix += "template <>\n"
						templatePostfix = classImpl.getTemplateValuesString(True)
						#self.classesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
					
					# Comment
					self.classesHeader += "// %s\n" % (prefix + classObj.name + templatePostfix)
					self.classesHeader += templatePrefix
					
					# Add code to classes header
					finalClassName = prefix + classObj.name + templatePostfix
					
					# Memory management
					if self.useGC:
						# Ensure destructor call?
						if classObj.ensureDestructorCall:
							gcClass = "gc_cleanup"
						else:
							gcClass = "gc"
						self.classesHeader += "class %s: public %s" % (finalClassName, gcClass)
					elif self.useReferenceCounting:
						self.classesHeader += "class %s: public boost::enable_shared_from_this< %s >" % (finalClassName, finalClassName)
					else:
						self.classesHeader += "class %s" % (finalClassName)
					
					# For debugging the GC add this commented line to the string:
					# ~%s(){std::cout << \"Destroying %s\" << std::endl;}\n
					self.classesHeader += " {\npublic:\n" + code + "};\n\n"
			#else:
			#	print("Extern: " + classObj.name)
	
	def getCode(self):
		self.writeFunctions()
		self.writeClasses()
		return self.header + self.prototypesHeader + self.varsHeader + self.classesHeader + self.functionsHeader + self.actorClassesHeader + self.customThreadsString + self.body + self.footer

####################################################################
# Header
####################################################################
# File:		Base class for output files
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
# 
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Compiler.Output import *
from flua.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Globals
####################################################################
INT32_MAX = 2147483647
INT32_MIN = -2147483648

enableOperatorOverloading = {
	"add",
	"subtract",
	"multiply",
	"divide",
	"equal",
	"not-equal",
	"assign-add",
	"assign-substract",
	"assign-multiply",
	"assign-divide",
}

replacedNodeValues = {
	"from" : "flua__from",
	"do" : "flua__do",
	"char" : "flua__char",
	"int" : "flua__int",
	"bool" : "flua_bool",
}

####################################################################
# Classes
####################################################################
class BaseOutputFile(ScopeController, BaseOutputFileHandler, BaseOutputFileScan):
	
	def __init__(self, compiler, file, root):
		ScopeController.__init__(self)
		
		self.compiler = compiler
		self.file = fixPath(file)
		self.dir = extractDir(file)
		
		# XML
		self.root = root
		self.codeNode = getElementByTagName(self.root, "code")
		self.headerNode = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.headerNode, "dependencies")
		self.strings = getElementByTagName(self.headerNode, "strings")
		self.stringsAsBytes = dict()
		
		# Local
		self.localClasses = []
		self.localFunctions = []
		self.additionalCodePerLine = []
		self.includes = []
		
		# Increment id
		self.compiler.fileCounter += 1
		self.id = "file_" + str(self.compiler.fileCounter)
		
		# Current
		self.currentClass = self.compiler.mainClass
		self.currentClassImpl = self.currentClass.requestImplementation([], [])
		self.currentFunction = None
		self.currentFunctionImpl = None
		
		# State
		self.inExtern = 0
		self.inGetter = 0
		self.inSetter = 0
		self.inCastDefinition = 0
		self.inTemplate = 0
		self.inAssignment = 0
		self.inConst = 0
		self.inUnmanaged = 0
		self.inOperators = 0
		self.inIterators = 0
		self.inIterator = 0
		self.inCasts = 0
		self.inOperator = 0
		self.inTypeDeclaration = 0
		self.inFunction = 0
		self.inDefine = 0
		self.inExtends = 0
		self.inParallel = 0
		self.inShared = 0
		self.namespaceStack = []
		self.parallelBlockStack = []
		self.tuples = dict()
		self.tupleTypes = dict()
		self.parallelForFuncs = list()
		self.onVariable = ""
		
		# TODO: Read from module meta data
		# Speed / Correctness
		self.checkDivisionByZero = True#self.compiler.checkDivisionByZero
		
		# Inserted for mathematical expressions
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		# String class
		self.stringClassDefined = False
		
		# Element handlers
		self.directMapping = {
			"access" : self.handleAccess,
			"assign" : self.handleAssign,
			"call" : self.handleCall,
			"new" : self.handleNew,
			"else" : self.handleElse,
			"try" : self.handleTry,
			"catch" : self.handleCatch,
			"namespace" : self.handleNamespace,
			"target" : self.handleTarget,
			"return" : self.handleReturn,
			"yield" : self.handleYield,
			"for" : self.handleFor,
			"foreach" : self.handleForEach,
			"parallel-for" : self.handleFor,
			"parallel-foreach" : self.handleForEach,
			"flow-to" : self.handleFlowTo,
			"const" : self.handleConst,
			"continue" : self.buildContinue,
			"parallel" : self.handleParallel,
			"begin" : self.handleParallel,
			"shared" : self.handleShared,
			"in" : self.handleIn,
			"on" : self.handleOn,
			"unmanaged" : self.handleUnmanaged,
			"compiler-flag" : self.handleCompilerFlag,
			"template-call" : self.handleTemplateCall,
			
			# Ignored
			"class" : self.handleClass,
			"interface" : None,
			"function" : None,
			"operator" : None,
			"cast-definition" : None,
			"get" : None,
			"set" : None,
			"extern" : None,
			"operators" : None,
			"iterators" : None,
			"extern-function" : None,
			"extern-variable" : None,
			"template" : None,
			"require" : None,
			"ensure" : None,
			"define" : None,
		}
		
		# Syntax
		self.lineLimiter = ""
		self.myself = ""
		self.trySyntax = ""
		self.catchSyntax = ""
		self.throwSyntax = ""
		self.returnSyntax = ""
		self.memberAccessSyntax = ""
		self.singleParameterSyntax = ""
		self.parameterSyntax = ""
		self.newObjectSyntax = ""
		self.binaryOperatorSyntax = "%s%s%s%s%s"
		self.binaryOperatorDivideSyntax = "%s%s%s%s%s"
		self.pointerDerefAssignSyntax = ""
		self.assignSyntax = "%s = %s"
		self.assignFirstTimeSyntax = self.assignSyntax
		self.constAssignSyntax = ""
		self.callSyntax = "%s(%s)"
		self.externCallSyntax = self.callSyntax
		self.templateSyntax = ""
		
		# Callback
		self.perParseChilds = None
		
		# Memory management
		self.useGC = True
		
		# Debugging
		self.lastParsedNode = list()
		
	def handleClass(self, node):
		className = getElementByTagName(node, "name").firstChild.nodeValue
		classObj = self.getClass(className)
		
		# Check interface implementations
		for interface in classObj.extends:
			if interface.classObj.isInterface:
				checkInterfaceImplementation(classObj, interface.classObj)
	
	def compile(self):
		raise NotImplementedError()
	
	def createVariable(self, name, type, value, isConst, isPointer, isPublic):
		raise NotImplementedError()
	
	def castToNativeNumeric(self, variableType, value):
		return value
	
	def checkStringClass(self):
		# Implement operator = of the string class manually to enable assignments
		if self.compiler.needToInitStringClass:
			#self.implementFunction("UTF8String", correctOperators("="), ["~MemPointer<ConstChar>"])
			self.implementFunction("UTF8String", "init", [])
			self.implementFunction("UTF8String", "init", ["~MemPointer<Byte>"])
			self.compiler.needToInitStringClass = False
		
		if self.classExists("UTF8String") and self.stringClassDefined == False:
			self.compiler.needToInitStringClass = True
	
	def parseBinaryOperator(self, node, connector, checkPointer = False):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		if op2 == "my":
			op2 = self.myself
		
		if op1 == "my":
			op1 = self.myself
			#op2 = "_" + op2
		
		#if connector == self.ptrMemberAccessChar:
		#	op2 = "_" + op2
		
#		if checkPointer:
#			op1type = self.getExprDataType(node.childNodes[0].childNodes[0])
#			print("%s%s%s (%s)" % (op1, connector, op2, op1 + " is a '" + op1type + "'"))
#			if (not op1type in nonPointerClasses) and (not isUnmanaged(op1type)) and (not connector == " == "):
#				return self.exprPrefix + op1 + "->operator" + connector.replace(" ", "") + "(" + op2 + ")" + self.exprPostfix
		
		connector = self.transformBinaryOperator(connector)
		
		# Division by zero
		if self.checkDivisionByZero and (connector == " / " or connector == " \\ "):
			self.addDivisionByZeroCheck(op2)
		
		if connector in {" + ", " - ", " * ", " / ", " \\ ", " & ", " | ", " && ", " || ", " % "}:
			self.exprPrefix = "("
			self.exprPostfix = ")"
		else:
			self.exprPrefix = ""
			self.exprPostfix = ""
		
		# Float conversion if needed
		if connector != " / ":
			return self.binaryOperatorSyntax % (self.exprPrefix, op1, connector, op2, self.exprPostfix)
		else:
			return self.binaryOperatorDivideSyntax % (self.exprPrefix, op1, connector, op2, self.exprPostfix)
	
	def getNamespacePrefix(self):
		namespacePrefix = '_'.join(self.namespaceStack)
		if namespacePrefix:
			return namespacePrefix + "_"
		else:
			return ""
	
	def fixMemberName(self, memberName):
		if memberName and memberName[0] == "_":
			memberName = memberName[1:]
		
		#print("Fixing: " + memberName)
		
		pos = memberName.find(self.ptrMemberAccessChar)
		if pos != -1:
			#print("Fixed: " + memberName[:pos])
			return memberName[:pos]
		
		return memberName
	
	def getParameterDefinitions(self, pNode, types, defaultValueTypes):
		if pNode is None:
			return "", ""
		
		pList = ""
		funcStartCode = ""
		counter = 0
		typesLen = len(types)
		
		parseExpr = self.parseExpr
		
		for node in pNode.childNodes:
			#if isElemNode(node.childNodes[0]) and node.childNodes[0].tagName == "declare-type":
			#	name = node.childNodes[0].childNodes[0].childNodes[0].nodeValue
			#else:
			if node.firstChild.nodeType != Node.TEXT_NODE and node.firstChild.tagName == "parameter":
				name = parseExpr(node.firstChild.firstChild)
			else:
				name = parseExpr(node.firstChild)
			
			#print("Name: " + name)
			#print(node.toprettyxml())
			
			if name in replacedNodeValues:
				name = replacedNodeValues[name]
			
			# Not enough parameters
			if counter >= typesLen:
				# Default values?
				if counter < len(defaultValueTypes) and defaultValueTypes[counter]:
					defaultValueType = defaultValueTypes[counter]
					adjustedDefaultValueType = self.adjustDataType(defaultValueType)
					#print("Using default parameter of type %s translated to %s" % (defaultValueType, adjustedDefaultValueType))
					self.registerVariable(self.createVariable(name, adjustedDefaultValueType, "", False, not adjustedDefaultValueType in nonPointerClasses, False))
					pList += self.buildSingleParameter(adjustedDefaultValueType, name) + ", "
					continue
				
				raise CompilerException("You forgot to specify the parameter '%s' of the function '%s'" % (name, self.currentFunction.getName()))
			
			usedAs = types[counter]
			
			# Typedefs
			usedAs = self.prepareTypeName(usedAs)
			
			# TODO: ...
			if name.startswith(self.memberAccessSyntax):
				member = name[len(self.memberAccessSyntax):]
				member = self.fixMemberName(member)
				
				#pos = member.find(self.ptrMemberAccessChar)
				#if pos != -1:
				#	member = member[:pos]
				
				self.currentClassImpl.addMember(self.createVariable(member, usedAs, "", False, not usedAs in nonPointerClasses, False))
				name = "__" + member
				funcStartCode += "\t\t" + self.memberAccessSyntax + member + " = " + name + self.lineLimiter
			#else:
			#	print("Not a member: " + name)
			
			if node.firstChild and node.firstChild.firstChild and tagName(node.childNodes[0].firstChild.firstChild) == "declare-type":
				declNode = node.childNodes[0].firstChild.firstChild
				declaredInline = True
			else:
				declNode = node.childNodes[0]
				declaredInline = (tagName(declNode) == "declare-type")
			
			if not declaredInline:
				#print("Variable %s used as '%s'" % (name, usedAs))
				self.getCurrentScope().variables[name] = self.createVariable(name, usedAs, "", False, not usedAs in nonPointerClasses, False)
				pList += self.buildSingleParameter(self.adjustDataType(usedAs), name) + ", "
			else:
				#for member in self.currentClassImpl.members.values():
				#	print(member.name)
				#	print(member.type)
				
				definedAs = self.parseExpr(declNode.childNodes[1], True) #self.getVariableTypeAnywhere(name)
				
				# Typedefs
				definedAs = self.prepareTypeName(definedAs)
				
				definedAs = self.currentClassImpl.translateTemplateName(definedAs)
				definedAs = self.addMissingTemplateValues(definedAs)
				
				# Implement it
				#if not definedAs in nonPointerClasses:
				#	try:
				#		self.getClassImplementationByTypeName(definedAs)
				#	except:
				#		pass
				
				#print("Defined: " + definedAs)
				#print(name)
				#print("------------")
				
				pList += self.buildSingleParameter(self.adjustDataType(definedAs), name) + ", "
				
				if definedAs != usedAs:
					if definedAs in nonPointerClasses and usedAs in nonPointerClasses:
						heavier = getHeavierOperator(definedAs, usedAs)
						if usedAs == heavier:
							compilerWarning("Information might be lost by converting '%s' to '%s' for the parameter '%s' in the function '%s'" % (usedAs, definedAs, name, self.currentFunction.getName()))
					else:
						raise CompilerException("'%s' expects the type '%s' where you used the type '%s' for the parameter '%s'" % (self.currentFunction.getName(), definedAs, usedAs, name))
			
			counter += 1
		
		return pList[:len(pList)-2], funcStartCode
	
	def pushClass(self, classObj):
		self.currentClass.addClass(classObj)
		self.currentClass = classObj
		
	def popClass(self):
		self.currentClass = self.currentClass.parent
	
	def getLastParsedNode(self):
		if not self.lastParsedNode:
			return None
		
		return self.lastParsedNode[-1]
		
	def getLastParsedNodes(self):
		if not self.lastParsedNode:
			return None
		
		return self.lastParsedNode
	
	def getExprDataType(self, node):
		dataType = self.getExprDataTypeClean(node)
		dataType = self.addMissingTemplateValues(dataType)
		
		# Replace typedefs
		dataType = self.prepareTypeName(dataType)
		
		return dataType#self.currentClassImpl.translateTemplateName(dataType)
	
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		#if funcName == "distance":
		#	debugStop()
		#print(caller, callerType, funcName, "<<<<<<<<<<")
		if self.compiler.mainClass.hasExternFunction(funcName):
			#print("EXTERN USAGE: " + funcName)
			return self.compiler.mainClass.externFunctions[funcName]
		else:
			callerClassImpl = self.getClassImplementationByTypeName(callerType)
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			
			#raise CompilerException("Function '" + funcName + "' has not been defined  [Error code 4]")
			
			#debug("Return types: " + str(funcImpl.returnTypes))
			#debug(self.compiler.funcImplCache)
			#debug("Return type of '%s' is '%s' (callerType: '%s')" % (funcImpl.getName(), funcImpl.getReturnType(), callerType))
			
			return funcImpl.getReturnType()
	
	def addMissingTemplateValues(self, typeName):
		pos = typeName.find("<")
		
		if pos == -1:
			if typeName in self.compiler.mainClass.classes:
				classObj = self.getClass(typeName)
				if classObj.templateNames:
					typeName += "<"
					for dataType in classObj.templateDefaultValues:
						dataType = self.currentClassImpl.translateTemplateName(dataType)
						typeName += self.addMissingTemplateValues(dataType) + ", "
					typeName = typeName[:-2] + ">"
		else:
			pass
			#templateValues = typeName[pos+1:-1].split(",")
			#for templateValue in templateValues:
			#	templateValue = templateValue.strip()
			#	print(templateValue)
		return typeName
	
	def getExprDataTypeClean(self, node):
		if node.nodeType == Node.TEXT_NODE:
			if node.nodeValue.isdigit():
				num = int(node.nodeValue)
				if num > INT32_MAX or num < INT32_MIN:
					return "BigInt"
				else:
					return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("flua_string_"):
				if self.stringClassDefined: #or self.currentFunction.isIterator:
					if node.nodeValue in self.stringsAsBytes:
						return "Byte"
					else:
						# All modules that import UTF8String have it defined
						return "UTF8String"
				else:
					# Modules who are compiled before that have to live with CStrings
					return "~MemPointer<ConstChar>"
			elif node.nodeValue == "my":
				return self.currentClassImpl.getFullName()
			elif node.nodeValue == "true" or node.nodeValue == "false":
				return "Bool"
			elif node.nodeValue == "null":
				return "MemPointer<void>"
			elif node.nodeValue in {"_flua_slice_start", "_flua_slice_end"}:
				return "Size"
			elif node.nodeValue in self.compiler.mainClass.classes:
				return node.nodeValue
			elif node.nodeValue in self.compiler.mainClass.functions:
				return "Function"
			elif node.nodeValue.startswith("0x"):
				return "Int"
			else:
				nodeName = node.nodeValue
				
				if nodeName in replacedNodeValues:
					nodeName = replacedNodeValues[nodeName]
				
				if nodeName in self.tupleTypes:
					return self.tupleTypes[nodeName]
				
				# Catch extern funcs
				if nodeName in self.compiler.mainClass.externFunctions:
					pass
				# Catch extern vars
				elif nodeName in self.compiler.mainClass.externVariables:
					pass
				elif self.inIterator and self.currentFunction.isIterator and self.compiler.enableIterVarPrefixes and self.varInLocalScope(nodeName):
					#print("getExprDataType: " + nodeName)
					return self.getVariableTypeAnywhere("_flua_iter_" + nodeName)
				
				#translatedName = self.currentClassImpl.translateTemplateName(nodeName)
				#if translatedName != nodeName:
				#	return "Size"
				
				return self.getVariableTypeAnywhere(nodeName)
		else:
			# Binary operators
			if node.tagName == "new":
				typeNode = getElementByTagName(node, "type").childNodes[0]
				
				if typeNode.nodeType == Node.TEXT_NODE:
					typeName = typeNode.nodeValue
				else:
					# Template parameters
					typeName = self.parseExpr(typeNode, True)
					
				# Check defines
				typeName = self.prepareTypeName(typeName)
					
				return typeName
				#return typeNode.childNodes[0].childNodes[0].nodeValue
			elif node.tagName == "call":
				if self.inFunction:
					# Recursive functions: Try to guess
					if self.currentFunction and getElementByTagName(node, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunctionImpl.returnTypes:
							return self.currentFunctionImpl.getReturnType()
						else:
							raise CompilerException("Unknown data type for recursive call: " + self.currentFunction.getName())
				
				return self.getCallDataType(node)
			elif node.tagName == "assign":
				op1 = node.childNodes[0].childNodes[0]
				
				if tagName(op1) == "declare-type":
					return self.parseExpr(op1.childNodes[1].firstChild)
				
				op2 = node.childNodes[1].childNodes[0]
				# TODO: Check for declare-type in op1
				return self.getExprDataType(op2)
			elif node.tagName == "access":
				caller = node.childNodes[0].childNodes[0]
				
				if caller.nodeType == Node.TEXT_NODE:
					if caller.nodeValue in self.compiler.mainClass.namespaces:
						varName = caller.nodeValue + "_" + node.childNodes[1].childNodes[0].nodeValue
						
						try:
							# Variables
							return self.getVariableTypeAnywhere(varName)
						except:
							# Functions
							virtualCall = self.makeXMLCall(varName)
							return self.getCallDataType(virtualCall)
					#elif caller.nodeValue in self.compiler.mainClass.classes:
					#	print(caller)
				
				callerType = self.getExprDataType(caller)
				
				callerClassName = extractClassName(callerType)
				memberName = node.childNodes[1].childNodes[0].nodeValue
				memberName = self.fixMemberName(memberName)
				
				callerClass = self.getClass(callerClassName)
				
#				templateParams = self.getTemplateParams(removeUnmanaged(callerType), callerClassName, callerClass)
				#print("getExprDataTypeClean:")
				#print("Member: %s" % (memberName))
				#print("callerType: " + callerType)
				#print("callerClassName: " + callerClassName)
				#print("templateParams: " + str(templateParams))
#				callerClassImpl = callerClass.implementations["_".join(templateParams.values())]
				#print("Class implementations: " + str(callerClass.implementations))
				
#				print("Picking implementation '" + callerClassImpl.getParamString() + "'")
				callerClassImpl = self.getClassImplementationByTypeName(callerType)
				
				# Check public members
				if memberName in callerClass.publicMembers:
					memberType = callerClass.publicMembers[memberName]
					
					#debug("Public member %s of type %s found for class %s" % (memberName, memberType, callerClassName))
					
					memberType = callerClassImpl.translateTemplateName(memberType)
					#debug("Translated: %s" % memberType)
					
					return memberType
				
				found, baseImpl = findPublicMemberInBaseClasses(callerClassImpl.classObj, memberName)
				if found:
					#debug("Switching %s to %s!" % (callerClassImpl.getFullName(), baseImpl.getFullName()))
					
					callerType = baseImpl.getFullName()
					callerClassImpl = baseImpl
				#else:
				#	print("%s not found in base classes of %s" % (memberName, callerType))
				
				if not callerClassImpl.hasConstructorImplementation(): #and not callerClass.isExtern:
					#print("XML:", node.toxml())
					#print("Implementing init default for '%s'" % (callerType))
					allFuncs = callerClassImpl.classObj.functions
					
					if "init" in allFuncs:
						initVariants = allFuncs["init"]
						paramTypes = initVariants[0].paramTypesByDefinition
						#print("paramTypes:", paramTypes)
						#callerClassImpl.requestFuncImplementation("init", paramTypes)
						
						self.implementFunction(callerType, "init", paramTypes)
						#print("Implemented.")
					else:
						raise CompilerException("'%s' is missing an 'init' constructor" % callerType)
				
				#debug("Member list:")
				#for member in callerClassImpl.members.keys():
				#	#debug(" * " + member)
				
				#	memberName = "_" + memberName
					
					#print("impl.members:", callerClassImpl.members)
					#print("class.properties:", callerClassImpl.classObj.properties)
					#print("class.publicMembers:", callerClassImpl.classObj.publicMembers)
					#print("<<")
				
				if memberName in callerClassImpl.members:
					#debug("Member '" + memberName + "' does exist")
					memberType = callerClassImpl.members[memberName].type
					#print(memberName)
					#print(memberType)
					#print(callerType)
					#print(callerClassName)
					#print(templateParams)
					#print("-----")
					return callerClassImpl.translateTemplateName(memberType)
				#elif findMemberInBaseClasses()
				else:
					#debug("Member '" + memberName + "' doesn't exist")
					
					# data access from a pointer
					#print(callerClassName, memberName)
					if callerClassName == "MemPointer" and memberName == "data":
						return callerType[callerType.find('<')+1:-1]
					
					memberFunc = "get" + capitalize(memberName)
					
					if not callerClassImpl.classObj.hasFunction(memberFunc):
						# Check base classes!
						func, impl = findFunctionInBaseClasses(callerClassImpl, memberFunc)
						
						if func:
							baseClassName = impl.getFullName()
							#print(baseClassName, memberFunc)
							
							funcImpl = self.implementFunction(baseClassName, memberFunc, [])
							#print(funcImpl.getReturnType())
							
							return funcImpl.getReturnType()
					
					virtualGetCall = self.makeXMLObjectCall(node.childNodes[0].childNodes[0].toxml(), memberFunc) 	
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
			elif node.tagName == "parameters":
				return "Tuple<%s>" % ', '.join([self.getExprDataType(x.firstChild) for x in node.childNodes])
			elif node.tagName == "slice":
				#           slice.value       .range        .from/to
				sliceFrom = node.childNodes[1].childNodes[0].childNodes[0].firstChild.toxml()
				sliceTo =   node.childNodes[1].childNodes[0].childNodes[1].firstChild.toxml()
				memberFunc = "operatorSlice"
				
				xmlCode = "<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom, sliceTo)
				return self.getCallDataType(self.cachedParseString(xmlCode).documentElement)
			elif node.tagName == "not":
				return "Bool"
				#return self.getExprDataType(node.childNodes[0].childNodes[0])
			elif node.tagName == "unmanaged":
				self.inUnmanaged += 1
				expr = self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
				self.inUnmanaged -= 1
				return "~" + expr
			elif node.tagName == "negative":
				return self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
			elif node.tagName == "exists-in":
				return "Bool"
			elif len(node.childNodes) == 2: # Any binary operation
				op1 = node.childNodes[0].childNodes[0]
				op2 = node.childNodes[1].childNodes[0]
				#op1Type = self.getExprDataType(op1)
				#op2Type = self.getExprDataType(op2)
				
				# Recursive functions: Try to guess
				if self.inFunction and self.currentFunction:
					# Is the second operator the recursive call?
					if tagName(op2) == "call" and getElementByTagName(op2, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						op1Type = self.getExprDataType(op1)
						self.currentFunctionImpl.returnTypes.append(op1Type)
						return getHeavierOperator(op1Type, self.currentFunctionImpl.getReturnType())
						#if self.currentFunctionImpl.returnTypes:
						#	return self.currentFunctionImpl.getReturnType()
						#else:
						#	return op1Type
					# Is the first operator the recursive call?
					elif tagName(op1) == "call" and getElementByTagName(op1, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						op2Type = self.getExprDataType(op2)
						self.currentFunctionImpl.returnTypes.append(op2Type)
						return getHeavierOperator(op2Type, self.currentFunctionImpl.getReturnType())
						#if self.currentFunctionImpl.returnTypes:
						#	return self.currentFunctionImpl.getReturnType()
						#else:
						#	return self.getExprDataType(op2)
				
				op1Type = self.getExprDataType(op1)
				op2Type = self.getExprDataType(op2)
				
				#if op1Type == "UTF8String" and op2Type in nonPointerClasses:
				#	return "UTF8String"
				
				# Subtraction should lead to a signed version
				if node.tagName == "subtract" and op1Type in nonPointerClasses and op2Type in nonPointerClasses:
					return self.getSignedVersion(op1Type)
				
				return self.getCombinationResult(node.tagName, op1Type, op2Type)
			
		raise CompilerException("Unknown data type for: " + node.toxml())
	
	def makeXMLCall(self, memberFunc, params = "<parameters/>"):
		xmlCode = "<call><function>%s</function>%s</call>" % (memberFunc, params)
		return self.cachedParseString(xmlCode).documentElement
	
	def makeXMLObjectCall(self, caller, memberFunc, params = "<parameters/>"):
		xmlCode = "<call><function><access><value>%s</value><value>%s</value></access></function>%s</call>" % (caller, memberFunc, params)
		return self.cachedParseString(xmlCode).documentElement
		
	def makeXMLAssign(self, op1, op2):
		xmlCode = "<assign><value>%s</value><value>%s</value></assign>" % (op1, op2)
		return self.cachedParseString(xmlCode).documentElement
		
	def makeXMLAccess(self, op1, op2):
		xmlCode = "<access><value>%s</value><value>%s</value></access>" % (op1, op2)
		return self.cachedParseString(xmlCode).documentElement
	
	def getSignedVersion(self, typeName):
		if typeName in {"Float", "Float32", "Float64"}:
			return "Float"
		elif typeName in {"BigInt"}:
			return "BigInt"
		else:
			return "Int"
	
	#def cachedCallType(self, xmlCode):
	#	if xmlCode in self.compiler.virtualCallDataType:
	#		print("USING CALL TYPE CACHE")
	#		return self.compiler.virtualCallDataType[xmlCode]
	#	else:
	#		virtualCall = parseString(xmlCode).documentElement
	#		typeName = self.getCallDataType(virtualCall)
	#		self.compiler.virtualCallDataType[xmlCode] = typeName
	#		return typeName
	
	def cachedParseString(self, xmlCode):
		if xmlCode in self.compiler.parseStringCache:
			return self.compiler.parseStringCache[xmlCode]
		else:
			tmpDoc = parseString(xmlCode)
			self.compiler.parseStringCache[xmlCode] = tmpDoc
			return tmpDoc
	
	def getFunctionCallInfo(self, node):
		funcNameNode = getFuncNameNode(node)
		
		caller = ""
		callerType = ""
		if funcNameNode.nodeType == Node.TEXT_NODE: #and funcNameNode.tagName == "access":
			funcName = funcNameNode.nodeValue
		else:
			#print("XML: " + funcNameNode.childNodes[0].childNodes[0].toxml())
			callerNode = funcNameNode.childNodes[0].childNodes[0]
			
			if callerNode.nodeValue in self.compiler.mainClass.namespaces:
				funcName = callerNode.nodeValue + "_" + funcNameNode.childNodes[1].childNodes[0].nodeValue
			#elif callerNode.nodeType == Node.ELEMENT_NODE and callerNode.tagName == "access" and callerNode.firstChild.firstChild.nodeValue in self.compiler.mainClass.classes:
			#	print(node.toprettyxml())
			else:
				callerType = self.getExprDataType(callerNode)
				caller = self.parseExpr(callerNode)
				funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
				#print(callerType + "::" + funcName)
		
		return caller, callerType, correctOperators(funcName)
	
	def getCombinationResult(self, operation, operatorType1, operatorType2):
		if operatorType1 in dataTypeWeights and operatorType2 in dataTypeWeights:
			if operation == "divide":
				dataType = getHeavierOperator(operatorType1, operatorType2)
				
				if dataType == "Double":
					return dataType
				else:
					return "Float"
			elif operation == "less" or operation == "greater" or operation == "less-or-equal" or operation == "greater-or-equal" or operation == "equal" or operation == "not-equal" or operation == "almost-equal" or operation == "and" or operation == "or":
				return "Bool"
			else:
				return getHeavierOperator(operatorType1, operatorType2)
		else:
			operatorType1 = removeUnmanaged(operatorType1)
			operatorType2 = removeUnmanaged(operatorType2)
			
			if operatorType1.startswith("MemPointer"):
				if operation == "index":
					return operatorType1[len("MemPointer<"):-1]
				if operatorType2.startswith("MemPointer"):
					if operation == "subtract":
						return "Size"
				if operation == "add" or operation == "subtract":
					return operatorType1
				return self.getCombinationResult(operation, "Size", operatorType2)
			if operatorType2.startswith("MemPointer"):
				return self.getCombinationResult(operation, operatorType1, "Size")
			
			# TODO: Remove temporary fix
			if operation == "index":
				#if operatorType1.startswith("Array<"):
				#	return operatorType1[len("Array<"):-1]
				impl = self.implementFunction(operatorType1, "[]", [operatorType2])
				return impl.getReturnType()
			
			custom = self.implementFunction(operatorType1, correctOperatorsTagName(operation), [operatorType2])
			if custom:
				return custom.getReturnType()
			
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
	
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		raise CompilerException("Unknown variable: %s" % name)
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			#if var.type in self.currentTemplateParams:
			#	return self.currentTemplateParams[var.type]
			return var.type
		
		if name in self.currentClassImpl.members:
			return self.currentClassImpl.members[name].type
		
		if name in self.compiler.mainClassImpl.members:
			return self.compiler.mainClassImpl.members[name].type
		
		if name in self.compiler.mainClass.externVariables:
			return self.compiler.mainClass.externVariables[name]
		
		#print(self.getTopLevelScope().variables)
		if name in self.compiler.mainClass.classes:
			raise CompilerException("You forgot to create an instance of the class '" + name + "' by using brackets")
		
		if name in self.compiler.mainClass.functions:
			raise CompilerException("A function call can only return a value if you use parentheses: '" + name + "()'")
		
		raise CompilerException("Unknown variable: " + name)
	
	def variableExistsAnywhere(self, name):
		if name in self.compiler.mainClassImpl.members:
			return 3
		
		if self.variableExists(name):
			return 1
		
		if name in self.currentClassImpl.members:
			return 2
		
		#print(name + " doesn't exist")
		return 0
	
	def classExists(self, className):
		if className == "":
			return True
		elif className in self.compiler.mainClass.classes:
			return True
		else:
			return False
	
	def isMemberAccessFromOutside(self, op1, op2):
		op1Type = self.getExprDataType(op1)
		op1ClassName = extractClassName(op1Type)
		
		#print(op1Type, op1ClassName)
		#debug(("get" + op2.nodeValue.capitalize()) + " -> " + str(self.compiler.mainClass.classes[op1Type].functions.keys()))
		
		# Are we accessing a member of a class that's not even defined?
		if not op1ClassName in self.compiler.mainClass.classes:
			#debug("Jump 1")
			return False, False
		
		if not op2.nodeValue:
			#debug("Jump 2")
			return False, False
		
		#if 1:#op2.nodeValue == "vertices":
		#	#debug("-" * 80)
		#	#debug(op1Type)
		#	#debug(op1ClassName)
		#	#debug("OP1:")
		#	#debug(op1.toprettyxml())
		#	#debug("OP2:")
		#	#debug(op2.toprettyxml())
		
		classObj = self.getClass(op1ClassName)
		
		funcs = classObj.functions
		prop = capitalize(op2.nodeValue)
		
		isPublicMember = classObj.hasPublicMember(op2.nodeValue)
		
		#debug(classObj.name)
		#debug(classObj.publicMembers)
		#debug(classObj.properties)
		#debug(op2.nodeValue)
		#debug(prop)
		#debug(isPublicMember)
		
		if isPublicMember:
			#debug("Jump 3")
			return False, True
		
		accessingGetter = ("get" + prop) in funcs
		accessingSetter = ("set" + prop) in funcs
		
		# Check base classes!
		func, impl = findFunctionInBaseClasses(classObj, "get" + prop)
		
		if func:
			#debug("Jump 3.5")
			return impl, False
		
		# TODO: Does that always work? -- Seems to work fine so far.
		if not op2.nodeValue in classObj.properties:
			#debug("Jump 4")
			return False, False
		
		if op2.nodeType == Node.TEXT_NODE and (accessingGetter or accessingSetter or (op2.nodeValue in self.getClassImplementationByTypeName(op1Type).members)):
			#print(self.currentFunction.getName() + " -> " + "get" + capitalize(op2.nodeValue))
			#print(self.currentFunction.getName() == "get" + capitalize(op2.nodeValue))
			
			#primaryObject = op1
			#while primaryObject.nodeType != Node.TEXT_NODE:
			#	primaryObject = primaryObject.firstChild
			
			if not (op1.nodeType == Node.TEXT_NODE and (op1.nodeValue == "my")):
				# Make a virtual call
				#print("so true")
				return True, False
		
		#print("so false")
		return False, False
	
	def registerVariable(self, var):
		if self.inShared:
			var.isShared = True
		
		#var.name = self.getNamespacePrefix() + var.name
		#debug("Registered variable '" + var.name + "' of type '" + var.type + "'")
		self.getCurrentScope().variables[var.name] = var
		
		# Enable GMP when BigInt is used
		if var.type == "BigInt":
			self.compiler.gmpEnabled = True
		
		if self.getCurrentScope() == self.getTopLevelScope():# and not self.currentFunctionImpl:
			self.compiler.mainClassImpl.members[var.name] = var
		
		#self.currentClassImpl.addMember(var)
		
	def registerVariableFuncScope(self, var):
		#debug("Registered variable '" + var.name + "' of type '" + var.type + "' in function scope")
		self.currentFunctionImpl.scope.variables[var.name] = var
		self.currentFunctionImpl.declareVariableAtStart(var)
	
	def pushNamespace(self, name):
		self.namespaceStack.append(name)
		
		if not name in self.currentClass.namespaces:
			#debug("Adding new namespace to '%s': '%s'" % (self.currentClass.name, name))
			self.currentClass.namespaces[name] = self.createNamespace(name)
		else:
			pass#print("Namespace '%s' already exists!" % name)
		
	def popNamespace(self):
		self.namespaceStack.pop()
	
	def getClass(self, className):
		if className == "":
			return self.compiler.mainClass
		elif className in self.compiler.specializedClasses:
			return self.compiler.specializedClasses[className]
		elif className in self.compiler.mainClass.classes:
			return self.compiler.mainClass.classes[className]
		else:
			#if not self.compiler.background:
			#	print("The following first class classes were defined:")
			#	for x in self.compiler.mainClass.classes.keys():
			#		print(x)
			#	print("-" * 80)
			
			raise CompilerException("Class '%s' has not been defined  [Error code 3]" % (className))
		
	def getClassImplementationByTypeName(self, typeName, initTypes = []):
		# === START Non-Inlined version === #
		# className = extractClassName(typeName)
		# templateValues = extractTemplateValues(typeName)
		# === END Non-Inlined version === #
		
		# === START inlined version === #
		pos = typeName.find('<')
		
		if pos != -1:
			className = typeName[:pos].replace("~", "")
			templateValues = typeName[pos + 1:-1]
		else:
			className = typeName.replace("~", "")
			templateValues = ""
		# === END inlined version === #
		
		return self.getClass(className).requestImplementation(initTypes, splitParams(templateValues))
		
	def getParameterList(self, pNode):
		if pNode is None:
			return [], [], [], []
		
		pList = []
		pTypes = []
		pDefault = []
		pDefaultTypes = []
		
		# Faster lookups
		pListAppend = pList.append
		pTypesAppend = pTypes.append
		pDefaultAppend = pDefault.append
		pDefaultTypesAppend = pDefaultTypes.append
		textNodeType = Node.TEXT_NODE
		translateTemplateName = self.currentClassImpl.translateTemplateName
		addMissingTemplateValues = self.addMissingTemplateValues
		prepareTypeName = self.prepareTypeName
		implementFunction = self.implementFunction
		addDefaultParameters = self.addDefaultParameters
		parseExpr = self.parseExpr
		
		for node in pNode.childNodes:
			name = ""
			type = ""
			defaultValue = ""
			defaultValueType = ""
			
			exprNode = node.childNodes[0]
			
			if exprNode.nodeType == textNodeType:
				name = exprNode.nodeValue
			elif exprNode.tagName == "name":
				name = exprNode.childNodes[0].nodeValue
				defaultValue = self.parseExpr(node.childNodes[1].childNodes[0])
			elif exprNode.tagName == "access":
				name = "__" + exprNode.childNodes[1].childNodes[0].nodeValue
			elif exprNode.tagName == "assign":
				if tagName(exprNode.childNodes[0].childNodes[0]) == "declare-type":
					name2 = self.parseExpr(exprNode.childNodes[0].childNodes[0].firstChild.firstChild)
					name, type = self.getTypeDeclInfo(exprNode.childNodes[0].childNodes[0])
					#print(name, name2, name == name2)
				else:
					name = self.parseExpr(exprNode.childNodes[0].childNodes[0])
				
				if name.startswith(self.memberAccessSyntax):
					member = name[len(self.memberAccessSyntax):]
					#self.currentClassImpl.addMember(self.createVariable(member, usedAs, "", False, not usedAs in nonPointerClasses, False))
					name = "__" + member
				
				defaultValue = self.parseExpr(exprNode.childNodes[1].childNodes[0])
				defaultValueType = self.getExprDataType(exprNode)
				
				#if declTypeFlag:
				#	exprNode = exprNode.childNodes[0].childNodes[0]
				
				# TODO: declare-type
				#type = defaultValueType
			elif exprNode.tagName == "declare-type":
				name, type = self.getTypeDeclInfo(exprNode)
				
				# Typedefs
				#type = prepareTypeName(type)
				
				#if typeNode.childNodes and isElemNode(typeNode) and typeNode.tagName == "unmanaged":
				#	type = "~" + type
			else:
				raise CompilerException("Invalid parameter %s" % (exprNode.toxml()))
			
			if name in replacedNodeValues:
				name = replacedNodeValues[name]
			
			pListAppend(name)
			
			type = translateTemplateName(type)
			type = addMissingTemplateValues(type)
			type = prepareTypeName(type)
			
			# Use default value type if not set
			#if not type and defaultValueType:
			#	type = defaultValueType
			
			# Implement it
			if not type in nonPointerClasses:
				try:
					#classImpl = self.getClassImplementationByTypeName(type)
					#classImpl.requestFuncImplementation("init", [])
					
					# Default parameters for init
					paramTypes, paramsString = addDefaultParameters(type, "init", [], "")
					funcImpl = implementFunction(type, "init", paramTypes)
				except:
					pass
			
			pTypesAppend(type)
			pDefaultAppend(defaultValue)
			pDefaultTypesAppend(defaultValueType)
		
		return pList, pTypes, pDefault, pDefaultTypes
	
	def varInLocalScope(self, name):
		return (name in self.getCurrentScope().variables or not name in self.getTopLevelScope().variables)
	
	def getTypeDeclInfo(self, exprNode):
		op1 = exprNode.childNodes[0].childNodes[0]
		if op1.nodeType == Node.ELEMENT_NODE and op1.tagName == "access":
			accessingObject = self.parseExpr(op1.childNodes[0].childNodes[0])
			accessingMember = self.parseExpr(op1.childNodes[1].childNodes[0])
			if accessingObject == self.myself:
				name = "__" + accessingMember
			else:
				raise CompilerException("'%s.%s' may not be used as a function parameter" % (accessingObject, accessingMember))
		else:
			name = self.parseExpr(op1)
		
		typeNode = exprNode.childNodes[1].childNodes[0]
		type = self.parseExpr(typeNode, True)
		
		return name, type
	
	def parseChilds(self, parent, prefix = "", postfix = ""):
		lines = []
		parseExpr = self.parseExpr
		
		for node in parent.childNodes:
			line = parseExpr(node)
			
			self.lastParsedNode.pop()
			
			if self.additionalCodePerLine:
				line = "%s%s%s%s" % ((postfix + prefix).join(self.additionalCodePerLine), postfix, prefix, line)
				self.additionalCodePerLine = []
				
			if line:
				lines.append(prefix)
				lines.append(line)
				lines.append(postfix)
		
		# Save scope for the IDE
		#if parent.tagName == "code":
		#self.saveScopesForNode(parent)
		
		# GUI responsiveness
		if self.perParseChilds:
			self.perParseChilds()
		
		return ''.join(lines)
	
	def parseExpr(self, node, keepUnmanagedSign = True):
		# Set last node for debugging purposes
		self.lastParsedNode.append(node)
		
		if not keepUnmanagedSign:
			expr = self.parseExpr(node, True)
			# Remove unmanaged sign
			if len(expr) and expr[0] == "~":
				return expr[1:]
			return expr
		
		# Return text nodes directly (if it is not a string)
		if node.nodeType == Node.TEXT_NODE:
			nodeName = node.nodeValue
			if nodeName.startswith("flua_string_"):
				return self.id + "_" + nodeName
			else:
				if nodeName == "my":
					if self.useGC:
						return self.myself
					# TODO: Make sure the algorithm to find out whether 'self' is being used solely works 100%
					#opNode = node.parentNode.parentNode
					#numChildNodes = len(opNode.childNodes)
					#if numChildNodes > 1:
					#	return self.myself
					#else:
						# TODO: Unmanaged object initiations need to return 'this'
					#	return "shared_from_this()"
				#elif nodeName == "null":
				#	return "NULL"
				# BigInt support
				elif nodeName.isdigit():
					num = int(nodeName)
					if num > INT32_MAX or num < INT32_MIN:
						return "(BigInt)(\"" + str(num) + "\")"
					else:
						return str(num)
				elif "." in nodeName:
					return self.buildFloat(nodeName)
				elif nodeName == "true":
					return self.buildTrue()
				elif nodeName == "false":
					return self.buildFalse()
				elif nodeName == "null":
					return self.buildNull()
				#elif nodeName == "_flua_slice_end":
				#	declTypeNode = node.parentNode.parentNode
				#	sliceNode = declTypeNode.parentNode.parentNode
				#	sliceOn	
				elif nodeName in replacedNodeValues:
					nodeName = nodeName
					nodeName = replacedNodeValues[nodeName]
					return nodeName
				# Catch member variables
				elif nodeName in self.currentClassImpl.members:
					return nodeName
				# Catch normal types
				elif nodeName in nonPointerClasses:
					return nodeName
				# Catch template types
				elif nodeName in self.currentClass.templateNames:
					return nodeName
				# Catch public
				elif nodeName in self.currentClass.publicMembers:
					return nodeName
				# Catch class names
				elif nodeName in self.compiler.mainClass.classes:
					return nodeName
				# Catch extern funcs
				elif nodeName in self.compiler.mainClass.externFunctions:
					return nodeName
				# Catch extern vars
				elif nodeName in self.compiler.mainClass.externVariables:
					return nodeName
				# Now we should only have variables left
				else:
					if self.inIterator and self.currentFunction.isIterator and self.compiler.enableIterVarPrefixes and self.varInLocalScope(nodeName) and isNot2ndAccessNode(node):
						#print("parseExpr: " + nodeName)
						#print(self.currentClassImpl.members)
						return "_flua_iter_" + nodeName
					
					return nodeName
		
		tagName = node.tagName
		
		# Check which kind of tag it is
		if tagName in self.directMapping:
			func = self.directMapping[tagName]
			
			if func:
				return func(node)
			else:
				return ""
		elif tagName == "value":
			return self.parseExpr(node.childNodes[0])
		elif tagName == "if-block" or tagName == "try-block":
			return self.parseChilds(node, "", "")
		# exists-in
		elif tagName == "exists-in":
			op1 = node.childNodes[0].firstChild
			op2 = node.childNodes[1].firstChild
			
			memberFunc = "contains"
			virtualCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (op2.toxml(), memberFunc, op1.toxml())).documentElement
			
			return self.handleCall(virtualCall)
		elif tagName == "parameters":
			return self.parseChilds(node, "", ", ")[:-2]
		elif tagName == "parameter":
			if getElementByTagName(node, "default-value"):
				return self.parseExpr(node.childNodes[0].childNodes[0])
			return self.parseExpr(node.childNodes[0])
		# Assign-add for Strings
		elif tagName == "assign-add":
			# So damn hardcoded...
			op1 = node.childNodes[0].firstChild
			op2 = node.childNodes[1].firstChild
			dataType = self.getExprDataType(op1)
			
			# TODO: Check whether the class has a += operator and if not, use this:
			if (not dataType in nonPointerClasses) and (not removeUnmanaged(dataType).startswith("MemPointer<")) and not self.getClass(extractClassName(dataType)).hasOperator("+="):
				lValue = self.parseExpr(op1)
				#rValue = self.parseExpr(op2)
				#return "%s = %s->operatorAdd__UTF8String(%s)" % (lValue, lValue, rValue)
				memberFunc = "+"
				virtualAddCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (op1.toxml(), memberFunc, op2.toxml())).documentElement
				
				return "%s = %s" % (lValue, self.handleCall(virtualAddCall))
		elif tagName in enableOperatorOverloading:
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
			callerClassName = extractClassName(callerType)
			#valueType = self.getExprDataType(node.childNodes[1].childNodes[0])
			
			if callerClassName == "void":
				funcName = node.childNodes[0].childNodes[0].childNodes[0].childNodes[0].nodeValue
				raise CompilerException("Function '%s' has no return value" % funcName)
			
			if callerClassName in nonPointerClasses:
				pass#return "(%s+%s)" % (caller, op2)
			elif callerClassName == "MemPointer": #and isUnmanaged(callerType):
				pass#return "(%s + %s)" % (caller, op2)
			else:#if correctOperators(tagName) in self.getClassImplementationByTypeName(callerType).funcImplementations:
				memberFunc = correctOperatorsTagName(tagName)
				if (not callerType in nonPointerClasses) and self.getClass(callerClassName).hasFunction(memberFunc):
					virtualIndexCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
					
					call = self.handleCall(virtualIndexCall)
					return call
				 
		#elif tagName == "not":
		#	return "!" + self.parseChilds(node)
		elif tagName == "index":
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
			index = self.parseExpr(node.childNodes[1].childNodes[0])
			callerClassName = extractClassName(callerType)
			
			if callerClassName == "MemPointer": #and isUnmanaged(callerType):
				return "%s[static_cast<size_t>(%s)]" % (caller, index)
			
			memberFunc = "[]"
			virtualIndexCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
			
			return self.handleCall(virtualIndexCall)
		elif tagName == "test":
			if self.isMainFile and node.parentNode.parentNode.tagName == "module":
				return self.parseChilds(node.firstChild, "\t" * self.currentTabLevel, self.lineLimiter)
			return ""
		elif tagName == "not":
			return self.buildNegation(self.parseExpr(node.firstChild))
		elif tagName == "throw":
			return self.throwSyntax % self.parseExpr(node.firstChild)
		elif tagName == "include":
			fileName = node.childNodes[0].nodeValue
			incFile = (self.dir + fileName)[len(self.compiler.modDir):]
			ifndef = normalizeModPath(incFile).replace(".", "_")
			self.includes.append((incFile, ifndef)) #+= "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			self.compiler.includes.append((incFile, ifndef))
			return ""
		elif node.tagName == "declare-type":
			if node.parentNode.tagName == "code":
				self.handleTypeDeclaration(node)
				return ""
			
			name = self.handleTypeDeclaration(node, insertTypeName = True)
			#print(name)
			return name
		elif node.tagName == "slice":
			#           slice.value       .range        .from/to
			sliceFrom = node.childNodes[1].childNodes[0].childNodes[0].firstChild.toxml()
			sliceTo =   node.childNodes[1].childNodes[0].childNodes[1].firstChild.toxml()
			
			memberFunc = "operatorSlice"
			
			if sliceFrom == "_flua_slice_start":
				sliceFrom = "0"
			
			if sliceTo == "_flua_slice_end":
				virtualSliceCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom)).documentElement
			else:
				# Call with 2 parameters
				virtualSliceCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom, sliceTo)).documentElement
			
			return self.handleCall(virtualSliceCall)
		elif node.tagName == "compiler-flags":
			return self.parseChilds(node, "", "")
		elif tagName == "break":
			return "break"
		elif tagName == "noop":
			return self.buildNOOP()
		
		# Check parameterized blocks
		if tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			#if isElemNode(getElementByTagName(node, paramTagName)):
			#	print(getElementByTagName(node, paramTagName).childNodes[0].toprettyxml())
			
			condition = self.parseExpr(getElementByTagName(node, paramTagName).childNodes[0])
			
			self.pushScope()
			code = self.parseChilds(getElementByTagName(node, codeTagName), "\t" * self.currentTabLevel, self.lineLimiter)
			self.popScope()
			
			return self.buildParamBlock(keywordName, condition, code, "\t" * self.currentTabLevel)
		
		# Check operators
		if tagName in self.compiler.operators:
			op = self.compiler.operators[tagName]
			
			if op.type == Operator.BINARY:
				if op.text == "\\":
					return self.parseBinaryOperator(node, " / ", True)
				return self.parseBinaryOperator(node, " %s " % op.text, True)
			elif op.type == Operator.UNARY:
				return "%s(%s)" % (op.text, self.parseExpr(node.childNodes[0]))
		
		return ""
	
	def isDerivedClass(self, typeA, typeB):
		try:
			typeAClassImpl = self.getClassImplementationByTypeName(typeA)
			typeAClass = typeAClassImpl.classObj
			
			typeBClassImpl = self.getClassImplementationByTypeName(typeB)
		except:
			# Classes are not defined yet
			return False
		
		#print(typeAClass.extends)
		#print(">>>", typeAClass.name, typeBClassImpl.getName(), "->", typeBClassImpl in typeAClass.extends)
		
		if typeBClassImpl in typeAClass.extends:
			return True
		else:
			return False
	
	def prepareTypeName(self, typeName):
		#if typeName is None:
		#	return typeName
		
		#print("PREPARE: " + typeName)
		while typeName in self.compiler.defines:
			typeName = self.compiler.defines[typeName]
		
		pos = typeName.find("<")
		if pos != -1:
			templateParts = []
			for param in splitParams(typeName[pos + 1:-1]):
				templateParts.append(self.prepareTypeName(param))
			
			typeName = typeName[:pos]
			templatePart = "<" + ", ".join(templateParts) + ">"
		else:
			templatePart = ""
		
		if typeName in self.compiler.specializedClasses:
			#if not typeName in nonPointerClasses:
			
			if not templatePart:
				classObj = self.getClass(extractClassName(typeName))
				if classObj.hasUndefinedTemplateParams():
					raise CompilerException("Class '%s' expects you to specify the following template parameters: '%s'" % (classObj.name, ", ".join(classObj.templateNames)))
			
			typeName = self.compiler.specializedClasses[typeName].name
		
		#print("PREPARED: " + typeName + templatePart)
		fullName = typeName + templatePart
		
		return fullName
	
	def implementFunction(self, typeName, funcName, paramTypes):
		#if funcName == "init":
		#	print("%s.%s(%s)" % (typeName, funcName, ", ".join(paramTypes)))
			#classImpl = self.getClassImplementationByTypeName(typeName)
			#classImpl.initCallTypes = paramTypes
		funcName = correctOperators(funcName)
		
		# For casts
		#while funcName in self.compiler.defines:
		#	funcName = self.compiler.defines[funcName]
		
		key = typeName + "." + funcName + "(" + ", ".join(paramTypes) + ")"
		
		if key in self.compiler.funcImplCache:
			return self.compiler.funcImplCache[key]
		
		className = extractClassName(typeName)
		if className in nonPointerClasses:
			raise CompilerException("'%s' has not been defined (maybe another function returns the wrong value?)" % (key))
		
		#print(funcName, "|", className, "|", key)
		if not funcName in self.getClass(className).functions:
			classImpl = self.getClassImplementationByTypeName(typeName)
			tmpFunc, baseClassImpl = findFunctionInBaseClasses(classImpl, funcName)
			
			if not tmpFunc:
				if not self.compiler.background:
					print(className + " contains the following functions:")
					print(" * " + "\n * ".join(self.getClass(className).functions.keys()))
					
				# TODO: Check for an iterator used in the wrong place and show another exception
				raise CompilerException("The '%s' function of class '%s' has not been defined" % (funcName, className))
		
		func = self.getClassImplementationByTypeName(typeName).getMatchingFunction(funcName, paramTypes)
		definedInFile = func.cppFile
		
		# Default parameters
		#paramTypesLen = len(paramTypes)
		#paramDefaultValueTypes = func.getParamDefaultValueTypes()
		#paramDefaultValueTypesLen = len(paramDefaultValueTypes)
		#if paramTypesLen < paramDefaultValueTypesLen:
		#	paramTypes += paramDefaultValueTypes[paramTypesLen:paramDefaultValueTypesLen]
		
		# Push
		oldFunc = definedInFile.currentFunction
		
		# Implement
		definedInFile.currentFunction = func
		if func.isIterator:
			definedInFile.stringClassDefined = True
		funcImpl = definedInFile.implementLocalFunction(typeName, funcName, paramTypes)
		
		# Pop
		definedInFile.currentFunction = oldFunc
		
		if className == "":
			prototype = funcImpl.getPrototype()
			self.prototypesHeader += prototype
			self.compiler.prototypes.append(prototype)
		
		#if func and funcImpl and funcImpl.getReturnType() != "void":
		self.compiler.funcImplCache[key] = funcImpl
		
		return funcImpl
	
	def implementLocalFunction(self, typeName, funcName, paramTypes):
		className = extractClassName(typeName)
		
		# Save values
		oldGetter = self.inGetter
		oldSetter = self.inSetter
		oldOperator = self.inOperator
		oldIterator = self.inIterator
		oldCastDefinition = self.inCastDefinition
		oldImpl = self.currentClassImpl
		oldClass = self.currentClass
		oldFunction = self.currentFunction
		oldFunctionImpl = self.currentFunctionImpl
		self.inFunction += 1
		
		# Set new values
		self.currentClass = self.getClass(className)
		self.currentClassImpl = self.getClassImplementationByTypeName(typeName)
		
		# TODO: This isn't really being used anymore, do we need this?
		node = self.currentFunction.node
		if node.tagName == "getter":
			self.inGetter += 1
		elif node.tagName == "setter":
			self.inSetter += 1
		elif node.tagName == "operator":
			self.inOperator += 1
		elif node.tagName == "iterator-type":
			self.inIterator += 1
		elif node.tagName == "cast-definition":
			self.inCastDefinition += 1
		
		if self.inCastDefinition:
			# For casts
			funcName = self.prepareTypeName(funcName)
		
		# Implement it
		funcImpl, codeExists = self.currentClassImpl.requestFuncImplementation(funcName, paramTypes)
		self.currentFunctionImpl = funcImpl
		
		if not codeExists:
			funcNode = funcImpl.func.node
			codeNode = getElementByTagName(funcNode, "code")
			
			#debug("Before:")
			#self.debugScopes()
			#debugPush()
			
			self.saveScopes()
			self.scopes = self.scopes[:1]
			
			self.pushScope()
			
			if typeName: #and not self.variableExistsAnywhere("my"):
				# TODO: removeUnmanaged(typeName) ? yes/no?
				self.registerVariable(self.createVariable("my", typeName, "", False, True, False))
			
			defaultValueTypes = funcImpl.func.getParamDefaultValueTypes()
			
			#print(defaultValueTypes)
			#defaultValueTypes = [self.currentClassImpl.translateTemplateName(x) for x in defaultValueTypes]
			#print("after: ")
			#print(defaultValueTypes)
			#print("---")
			
			parameters, funcStartCode = self.getParameterDefinitions(getElementByTagName(funcNode, "parameters"), paramTypes, defaultValueTypes) #[self.currentClassImpl.translateTemplateName(x) for x in funcImpl.func.getParamDefaultValueTypes()]
			
			#  * self.currentTabLevel
			oldTabLevel = self.currentTabLevel
			if typeName:
				self.currentTabLevel = 2
			else:
				self.currentTabLevel = 1
			
			# Set scope
			funcImpl.setScope(self.getCurrentScope())
			
			# Here we parse the actual code node
			funcImplCode = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
			
			# Variables used in deeper scopes need to be initialized at the beginning
			varsAtStart = []
			for var in funcImpl.variablesAtStart:
				varsAtStart.append("\t" * self.currentTabLevel)
				varsAtStart.append(var.getPrototype())
				varsAtStart.append(";\n")
			varsAtStartCode = ''.join(varsAtStart)
			#print(varsAtStartCode)
			
			# Set code
			funcImpl.setCode(funcStartCode + varsAtStartCode + funcImplCode)
			
			self.currentTabLevel = oldTabLevel - 1
			
			self.restoreScopes()
			
			#debugPop()
			#debug("After:")
			#self.debugScopes()
		
		# Load previous values
		self.inFunction -= 1
		self.currentFunction = oldFunction
		self.currentFunctionImpl = oldFunctionImpl
		self.inGetter = oldGetter
		self.inSetter = oldSetter
		self.inOperator = oldOperator
		self.inIterator = oldIterator
		self.inCastDefinition = oldCastDefinition
		self.currentClass = oldClass
		self.currentClassImpl = oldImpl
		
		return funcImpl
	
	def addDefaultParameters(self, typeName, funcName, paramTypes, paramsString):
		func = self.getClassImplementationByTypeName(typeName).getMatchingFunction(funcName, paramTypes)
		#if not func:
		#	raise CompilerException("Couldn't")
		
		paramTypesLen = len(paramTypes)
		paramDefaultValues = func.getParamDefaultValues()
		paramDefaultValueTypes = func.getParamDefaultValueTypes()
		paramDefaultValuesLen = len(paramDefaultValues)
		if paramTypesLen < paramDefaultValuesLen:
			if paramsString:
				paramsString += ", "
			paramTypes += paramDefaultValueTypes[paramTypesLen:paramDefaultValuesLen]
			paramsString += ", ".join(paramDefaultValues[paramTypesLen:paramDefaultValuesLen])
		
		return paramTypes, paramsString
	
	def isInvalidType(self, typeNode):
		return (typeNode.nodeType != Node.TEXT_NODE) and (not typeNode.tagName in {"template-call", "unmanaged"})
	
	def getFunction(self, name):
		return self.compiler.mainClass.functions[name]
	
	def buildVarDeclaration(self, typeName, name):
		return self.buildSingleParameter(typeName, name)
	
	def addDivisionByZeroCheck(self, op):
		if isNumeric(op):
			if op != "0" and op != "0.0":
				return
			else:
				self.additionalCodePerLine.append(self.buildDivByZeroThrow(op))
				return
		
		self.additionalCodePerLine.append(self.buildDivByZeroCheck(op))
	
	def waitCustomThreadsCode(self, block):
		joinCodes = []
		tabs = "\t" * self.currentTabLevel
		for threadID in block:
			joinCodes.append(self.buildThreadJoin(threadID, tabs))
		return ''.join(joinCodes)
	
	def pushScope(self):
		self.currentTabLevel += 1
		ScopeController.pushScope(self)
		
	def popScope(self):
		self.currentTabLevel -= 1
		ScopeController.popScope(self)
	
	def debugScopes(self):
		counter = 0
		for scope in self.scopes:
			print("[Scope " + str(counter) + "]")
			for name, variable in scope.variables.items():
				print(" => " + variable.name.ljust(40) + " : " + variable.type)
			counter += 1
	
	def implementCasts(self):
		# Implement casts BEFORE class functions are written
		for classObj in self.localClasses:
			if not classObj.isExtern:
				for classImplId, classImpl in classObj.implementations.items():
					for funcList in classObj.functions.values():
						if funcList:
							func = funcList[0]
							if func.isCast:
								#print("===> " + classImpl.getName() + "." + func.getName())
								self.implementFunction(classImpl.getName(), func.getName(), [])
	
	def writeFunctions(self):
		for func in self.localFunctions:
			for funcImpl in func.implementations.values():
				self.functionsHeader += "%s\n" % (funcImpl.getFullCode())
	
	def getRootNode(self):
		return self.root
		
	def getCodeNode(self):
		return self.codeNode
		
	def getHeaderNode(self):
		return self.headerNode
		
	def getDependenciesNode(self):
		return self.dependencies
	
	def getFilePath(self):
		return self.file
	
	def getFileName(self):
		return self.file[len(self.dir):]
	
	def getDirectory(self):
		return self.dir
	
	def getCode(self):
		return NotImplementedError()

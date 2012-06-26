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
from bp.Compiler.Output.cpp.CPPNamespace import *
from bp.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Classes
####################################################################
class CPPOutputFile(BaseOutputFile):
	
	def __init__(self, compiler, file, root):
		self.currentTabLevel = 0
		
		BaseOutputFile.__init__(self, compiler, file, root)
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"],
		}
		
		# Codes
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.body = ""
		self.footer = "#endif\n"
		
		# Other code types
		self.stringsHeader = "\t// Strings\n"
		self.varsHeader = "\n// Variables\n\n"
		self.dataFlowHeader = "\n// DataFlow variables\n\n"
		self.functionsHeader = "\n// Functions\n\n"
		self.classesHeader = "\n// Classes\n\n"
		#self.actorClassesHeader = ""
		self.prototypesHeader = "\n// Prototypes\n\n"
		self.includesHeader = "\n// Includes\n\n"
		
		# Syntax
		self.lineLimiter = ";\n"
		self.myself = "this"
		self.trySyntax = "try {\n%s\n\t}"
		self.catchSyntax = " catch (%s) {\n%s\n\t}"
		self.throwSyntax = "throw %s"
		self.returnSyntax = "return %s"
		self.memberAccessSyntax = "this->"
		self.singleParameterSyntax = "%s %s"
		self.newObjectSyntax = "(new %s(%s))"
		self.binaryOperatorDivideSyntax = "%sfloat(%s)%s%s%s"
		self.pointerDerefAssignSyntax = "*%s = %s"
		self.declareUnmanagedSyntax = "%s(%s)"
		self.constAssignSyntax = "const %s = %s"
		self.elseSyntax = " else {\n%s%s}"
		self.ptrMemberAccessChar = "->"
		self.yieldSyntax = "__bp_yield_var = %s;\n__bp_yield_code"
		self.templateSyntax = "%s<%s>"
		
	def compile(self):
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
		self.body += self.parseChilds(self.codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		self.body += "}\n"
		
		# Includes
		incls = ["#ifndef %s\n#define %s\n#include <%s>\n#endif\n" % (ifndef, ifndef, incl) for incl, ifndef in self.includes]
		self.includesHeader += "".join(incls)
		
		# Variables
		for var in self.getTopLevelScope().variables.values():
			if var.isShared:
				prefix = "volatile "
			else:
				prefix = ""
			
			if var.isConst:
				self.varsHeader += prefix + "const " + var.getPrototype() + " = " + var.value + ";\n";
			elif var.type == self.compiler.stringDataType:
				self.compiler.strings.append(var.getPrototype())
				self.compiler.strings.append(";\n")
			elif not isUnmanaged(var.type):
				self.varsHeader += prefix + var.getPrototype() + ";\n"
				
		#self.varsHeader += "\n"
		
		self.structsHeader = "\n// Tuples\n\n%s" % '\n'.join(self.tuples.values())
	
	def createVariable(self, name, type, value, isConst, isPointer, isPublic):
		return CPPVariable(name, type, value, isConst, isPointer, isPublic)
	
	def createNamespace(self, name):
		return CPPNamespace(name)
		
	def createClass(self, name, node):
		return CPPClass(name, node)
	
	def createFunction(self, node):
		return CPPFunction(self, node)
		
	def buildThreadFunc(self, funcName, paramTypes):
		if funcName in self.compiler.customThreads:
			return
		
		if self.compiler.tinySTMEnabled:
			initCode = "stm_init_thread();"
			exitCode = "stm_exit_thread();"
		else:
			initCode = ""
			exitCode = ""
		
		paramNames, struct = self.buildStruct("bp_thread_args_%s" % funcName, paramTypes)
		
		func = """%s

// Thread function for '%s'
void* bp_thread_func_%s(void *bp_arg_struct_void) {
	%s
	
	bp_thread_args_%s *args = reinterpret_cast<bp_thread_args_%s*>(bp_arg_struct_void);
	%s(%s);
	if(args)
		delete args;
		
	%s
	return NULL;
}
""" % (struct, funcName, funcName, initCode, funcName, funcName, funcName, ', '.join(paramNames), exitCode)
		self.compiler.customThreads[funcName] = func
		
	def buildFloat(self, value):
		return value + "f"
		
	def buildStruct(self, structName, paramTypes, isClass = False):
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
		
		if isClass:
			blockStart = "class"
			blockEnd = ""
			publicDecl = "public:"
			constructorName = structName#[:structName.find("<")]
		else:
			blockStart = "typedef struct"
			blockEnd = structName
			publicDecl = ""
			constructorName = structName
		
		return paramNames, """
// Struct '%s'
%s %s {
%s
	%s
	inline %s(%s) %s {}
} %s;""" % (structName, blockStart, structName, publicDecl, ''.join(params), constructorName, ', '.join(constructorList), initParams, blockEnd)
		
	def adjustDataType(self, typeName, adjustOuterAsWell = True):
		return adjustDataTypeCPP(typeName, adjustOuterAsWell)
	
	def buildThreadJoin(self, threadID, tabs):
		return "\n%spthread_join(bp_threadHandle_%d, NULL);" % (tabs, threadID)
	
	def buildForLoop(self, varDefs, typeInit, iterExpr, fromExpr, operator, toExpr, code, tabs):
		return "%sfor(%s%s = %s; %s %s %s; ++%s) {\n%s%s}" % (varDefs, typeInit, iterExpr, fromExpr, iterExpr, operator, toExpr, iterExpr, code, tabs)
	
	def buildForEachLoop(self, var, typeInit, iterExpr, collExpr, collExprType, iterImplCode, code, tabs, counterVarName, counterTypeInit):
		# Fix tabs
		numTabs = countTabs(iterImplCode) - len(tabs)
		
		if numTabs:
			lines = []
			for x in iterImplCode.split('\n'):
				if not x:
					continue
				counter = numTabs
				while counter > 0 and x[0] == '\t':
					x = x[1:]
					counter -= 1
				lines.append(x)
			iterImplCode = '\n'.join(lines)
		
		# Get class impl
		classImpl = self.getClassImplementationByTypeName(collExprType)
		
		# Performance optimization:
		# Do we need a temporary variable to hold the collExpr value?
		# TODO: We might ignore this for "this", "self", "my" etc.
		if collExpr.find("->") != -1:
			newCollExpr = "_bp_tmp_coll_%d" % self.compiler.forVarCounter
			collInitCode = self.buildLine("%s %s = %s" % (self.adjustDataType(collExprType), newCollExpr, collExpr))
			collExpr = newCollExpr
		else:
			collInitCode = ""
		
		# Do this BEFORE fixing member names
		iterImplCode = iterImplCode.replace("this->", collExpr + "->")
		
		# Fix member names
		for member in classImpl.members.values():
			old = "%s->%s" % (collExpr, member.name)
			new = "%s->_%s" % (collExpr, member.name)
			
			#debug("Replacing '%s' with '%s'" % (old, new))
			iterImplCode = iterImplCode.replace(old, new)
		
		# Because we love hardcoding. We're removing the '\n' and ';' here.
		code = code[:-2]
		
		# loop.counter
		if counterVarName:
			initCode = self.buildLine("%s\t%s%s = 0" % (tabs, counterTypeInit, counterVarName))
			perIterationCode = ";" + self.buildLine("\n\t%s%s++" % (tabs, counterVarName))
		else:
			initCode = ""
			perIterationCode = ""
		
		continueJump = ";\n_continue_point_%d:\n" % self.compiler.forVarCounter
		
		resultingCode = iterImplCode.replace("__bp_yield_var", iterExpr).replace("__bp_yield_code", code + continueJump + perIterationCode)
		
		return "{\n%s%s%s%s%s;\n%s\n%s}" % (initCode, tabs, collInitCode, typeInit, iterExpr, resultingCode, tabs)
		#return initCode + "{\n" + tabs + typeInit + iterExpr + ";\n" + resultingCode + "\n" + tabs + "}"
	
	def buildContinue(self, node):
		# Are we in a for or foreach loop?
		parent = node.parentNode
		while not parent.tagName in {"for", "while", "foreach", "module"}:
			parent = parent.parentNode
		
		if parent.tagName in {"for", "while"}:
			return "continue"
		elif parent.tagName == "foreach":
			return "goto _continue_point_%d" % self.compiler.forVarCounter
		else:
			raise CompilerException("Can't determine loop type in 'continue' statement")
	
	def buildTypeDeclaration(self, typeName, varName):
		return self.adjustDataType(typeName) + " " + varName
		
	def buildTypeDeclarationNameOnly(self, varName):
		return varName
	
	def buildTemplateCall(self, op1, op2):
		return op1 + "<" + op2 + ">"
	
	def buildDivByZeroCheck(self, op):
		return 'if((%s) == 0) throw new BPDivisionByZeroException()' % op
	
	def buildDivByZeroThrow(self, op):
		return 'throw new BPDivisionByZeroException()'
	
	def buildString(self, id, value):
		return id + " = new BPUTF8String(const_cast<Byte*>(\"" + value + "\"));\n"
	
	def buildStringAsByte(self, id, value):
		return id + " = " + str(ord(value)) + ";\n"
	
	def buildUndefinedString(self, id, value):
		return id + " = const_cast<Byte*>(\"" + value + "\");\n"
	
	def buildModuleImport(self, importedModule):
		return "#include <" + extractDir(importedModule) + "C++/" + stripAll(importedModule) + ".hpp>\n"
	
	def buildDeleteMemPointer(self, caller):
		return "delete [] %s" % (caller)
	
	def buildThreadCreation(self, threadID, threadFuncID, paramTypes, paramsString, tabs):
		threadCreation =  "pthread_t bp_threadHandle_%d;\n%s" % (threadID, tabs)
		
		if paramTypes:
			threadCreation += "bp_thread_args_%s* bp_threadArgs_%d = new (NoGC) bp_thread_args_%s(%s);\n%s" % (threadFuncID, threadID, threadFuncID, paramsString, tabs)
			threadCreation += "pthread_create(&bp_threadHandle_%d, NULL, &bp_thread_func_%s, bp_threadArgs_%d);\n%s" % (threadID, threadFuncID, threadID, tabs)
		else:
			threadCreation += "pthread_create(&bp_threadHandle_%d, NULL, &bp_thread_func_%s, reinterpret_cast<void*>(NULL));\n%s" % (threadID, threadFuncID, tabs)
		
		return threadCreation
	
	def buildNonPointerCall(self, caller, fullName, paramsString):
		return "%s%s%s%s%s" % (["::", caller + "."][caller != ""], fullName, "(", paramsString, ")")
	
	def buildCall(self, caller, fullName, paramsString):
		return "%s%s%s%s%s" % (["::", caller + "->"][caller != ""], fullName, "(", paramsString, ")")
	
	def buildSingleParameter(self, typeName, name):
		return self.singleParameterSyntax % (typeName, name)
	
	def buildUnmanagedMemPtrWithoutGC(self, ptrType, paramsString):
		return "new %s[%s]" % (ptrType, paramsString)
	
	def buildUnmanagedMemPtrWithGC(self, ptrType, paramsString):
		return "new (UseGC) %s[%s]" % (ptrType, paramsString)
	
	def buildNewObject(self, finalTypeName, funcImpl, paramsString):
		return self.newObjectSyntax % (finalTypeName, paramsString)
	
	def buildParamBlock(self, keywordName, condition, code, tabs):
		return "%s(%s) {\n%s%s}" % (keywordName, condition, code, tabs)
	
	def buildTrue(self):
		return "true"
		
	def buildFalse(self):
		return "false"
	
	def buildNegation(self, expr):
		return "(!(%s))" % expr
	
	def buildInBlock(self, exprNode, expr, exprType, code, tabs):
		exprType = self.adjustDataType(exprType)
		
		hasVar = (isElemNode(exprNode.firstChild) and exprNode.firstChild.tagName == "assign")
		if hasVar:
			# Left operator = Tmp variable
			c = self.parseExpr(exprNode.firstChild.firstChild)
			return "//in {\n%s\t%s;\n%s\t%s->enter();\n%s%s\t%s->exit();\n%s//}" % (tabs, expr, tabs, c, code, tabs, c, tabs)
		else:
			c = self.compiler.inVarCounter
			self.compiler.inVarCounter += 1
			return "//in {\n%s\t%s _tmp_var_%d = (%s);\n%s\t_tmp_var_%d->enter();\n%s%s\t_tmp_var_%d->exit();\n%s//}" % (tabs, exprType, c, expr, tabs, c, code, tabs, c, tabs)
	
	def buildCatchVar(self, varName, typeName):
		return self.singleParameterSyntax % (typeName, varName)
	
	def buildEmptyCatchVar(self):
		return "..."
	
	def buildNOOP(self):
		return ""
		
	def buildNull(self):
		return "NULL"
		
	def buildMemberTypeDeclInConstructor(self, varName):
		return varName
	
	def buildConstAssignment(self, var, value):
		if self.getCurrentScope() == self.getTopLevelScope():
			return ""
		else:
			return self.constAssignSyntax % (var.getFullPrototype(), value)
	
	def buildFunctionDataFlowOnReturn(self, node, expr, funcImpl):
		funcImplName = funcImpl.getName()
		varName = funcImplName + "_return_value"
		returnType = funcImpl.getReturnType()
		
		#self.getClassImplementationByTypeName("MutableVector<>")
		
		code = "{%s" % (self.buildLine(self.assignSyntax % (self.adjustDataType(returnType) + " " + varName, expr)))
		code += self.buildDataFlowListenerIteration(funcImplName, varName)
		code += self.returnSyntax % varName + ";}"
		return code
		
	def buildLine(self, line):
		return line + ";\n" + "\t" * self.currentTabLevel
		
	def buildDataFlowListenerIteration(self, listenersForObject, params):
		paramType = "Int"
		iterExpr = "_currentListener"
		iterType = "std::vector<%s_listener_type>::iterator" % (listenersForObject)
		collExpr = listenersForObject + "_listeners"
		tabs = "\t" * self.currentTabLevel
		code = self.buildLine("for(%s %s = %s.begin(); %s != %s.end(); ++%s ) {\n%s\t(*%s)(%s);\n%s}" % (
			# Init
			iterType,
			iterExpr,
			collExpr,
			
			# Condition
			iterExpr,
			collExpr,
			
			# Increment
			iterExpr,
			
			# Tabs
			tabs,
			
			# Execute
			iterExpr,
			params,
			
			# Tabs
			tabs,
		))
		
		return code
	
	def transformBinaryOperator(self, operator):
		return operator
	
	def castToNativeNumeric(self, variableType, value):
		return "static_cast< %s >( BigInt(%s).get_si() )" % (variableType, value)
		
	def handleCompilerFlag(self, node):
		flag = node.childNodes[0].nodeValue
		if flag.startswith("-l"):
			self.compiler.customLinkerFlags.insert(0, flag)
		else:
			self.compiler.customCompilerFlags.insert(0, flag)
		return ""
	
	def writeClasses(self):
		prefix = "BP"
		
		for classObj in self.localClasses:
			if not classObj.isExtern:
				for classImplId, classImpl in classObj.implementations.items():
					destructorWritten = False
					code = ""
					
					# Functions
					for funcImpl in classImpl.funcImplementations.values():
						if funcImpl.getFuncName() == "init":
							code += "\t" + funcImpl.getConstructorCode() + "\n"
						elif funcImpl.getFuncName() == "finalize":
							code += "\t" + funcImpl.getDestructorCode() + "\n"
							destructorWritten = True
						elif funcImpl.func.isIterator:
							continue
						else:
							code += "\t" + funcImpl.getFullCode() + "\n"
					
					# Virtual destructor
					if classObj.hasOverwrittenFunctions and not destructorWritten:
						code += "\tvirtual ~BP%s() {};\n" % classObj.name
					
					# Private members
					# TODO: SET IT BACK TO PRIVATE AFTER FIXING FORCE INCLUSION
					code += "public:\n"
					for member in classImpl.members.values():
						#print(member.name + " is of type " + member.type)
						code = code.replace("this->" + member.name, "this->_" + member.name) + "\t" + adjustDataTypeCPP(member.type, True) + " _" + member.name + ";\n"
					
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
					
					# Inheritance
					extends = "public "
					classes = ""
					if classObj.extends:
						classes = ', public '.join(self.adjustDataType(c.classObj.name).replace("*", "") for c in classObj.extends)
						extends += classes
					
					# Memory management
					if self.useGC:
						# Ensure destructor call?
						if not classes:
							if classObj.ensureDestructorCall:
								extends += "gc_cleanup"
							else:
								extends += "gc"
						self.classesHeader += "class %s: %s" % (finalClassName, extends)
					#elif self.useReferenceCounting:
					#	self.classesHeader += "class %s: public boost::enable_shared_from_this< %s >" % (finalClassName, finalClassName)
					#else:
					#	self.classesHeader += "class %s" % (finalClassName)
					
					# For debugging the GC add this commented line to the string:
					# ~%s(){std::cout << \"Destroying %s\" << std::endl;}\n
					self.classesHeader += " {\npublic:\n" + code + "};\n\n"
			#else:
			#	print("Extern: " + classObj.name)
	
	def getCode(self):
		self.writeFunctions()
		self.writeClasses()
		
		return "%s%s%s%s%s%s%s%s%s%s" % (
			self.header,
			self.prototypesHeader,
			self.includesHeader,
			self.structsHeader,
			self.varsHeader,
			self.dataFlowHeader,
			self.classesHeader,
			#self.customThreadsString,
			self.functionsHeader,
			#self.actorClassesHeader,
			self.body,
			self.footer
		)

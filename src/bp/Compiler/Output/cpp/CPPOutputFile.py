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
		
		self.customThreads = dict()
		self.customThreadsString = ""
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"]
		}
		
		# String class
		self.stringClassDefined = False
		
		# Codes
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.body = ""
		self.footer = "#endif\n"
		
		# Other code types
		self.stringsHeader = "\t// Strings\n"
		self.varsHeader = "\n// Variables\n"
		self.functionsHeader = "// Functions\n"
		self.classesHeader = ""
		self.actorClassesHeader = ""
		self.prototypesHeader = "\n// Prototypes\n"
		
		# Syntax
		self.lineLimiter = ";\n"
		self.myself = "this"
		self.trySyntax = "try {\n%s\n\t}"
		self.catchSyntax = " catch (%s) {\n%s\n\t}"
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
		
	def compile(self):
		print("Compiling: " + self.file)
		
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
	
	def createNamespace(self, name):
		return CPPNamespace(name)
		
	def createClass(self, name, node):
		return CPPClass(name, node)
	
	def createFunction(self, node):
		return CPPFunction(self, node)
		
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
		
	def adjustDataType(self, typeName, adjustOuterAsWell = True):
		return adjustDataTypeCPP(typeName, adjustOuterAsWell)
	
	def buildThreadJoin(self, threadID, tabs):
		return "\n%spthread_join(bp_threadHandle_%d, NULL);" % (tabs, threadID)
	
	def buildForLoop(self, varDefs, typeInit, iterExpr, fromExpr, operator, toExpr, code, tabs):
		return "%sfor(%s%s = %s; %s %s %s; ++%s) {\n%s%s}" % (varDefs, typeInit, iterExpr, fromExpr, iterExpr, operator, toExpr, iterExpr, code, tabs)
	
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

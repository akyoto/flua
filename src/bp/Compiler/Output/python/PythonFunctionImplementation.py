from bp.Compiler.Utils import *
from bp.Compiler.Output import *
from bp.Compiler.Output.python.PythonDataTypes import *

class PythonFunctionImplementation(BaseFunctionImplementation):
	
	def __init__(self, classImpl, func, paramTypes):
		super().__init__(classImpl, func, paramTypes)
		
	def getParamString(self):
		if self.classImpl.classObj.name:
			stri = "self, "
		else:
			stri = ""
		
		paramNames = self.func.getParamNames()
		paramTypesLen = len(self.paramTypes)
		
		for i in range(len(paramNames)):
			if i < paramTypesLen:
				paramType = self.paramTypes[i]
			else:
				# Default values
				paramType = self.func.paramDefaultValueTypes[i]
			stri += "%s, " % (paramNames[i])
		return stri[:-2]
		
	def getParamTypeString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		paramTypesLen = len(self.paramTypes)
		#print(paramNames)
		#print(self.paramTypes)
		for i in range(len(paramNames)):
			if i < paramTypesLen:
				paramType = self.paramTypes[i]
			else:
				# Default values
				paramType = self.func.paramDefaultValueTypes[i]
			stri += "%s, " % (adjustDataTypePY(paramType))
		return stri[:-2]
		
	def getReferenceString(self):
		# TODO: Remove hardcoded stuff
		if self.getFuncName() == "operatorIndex":
			return "&"
		return ""
		
	def getPrototype(self):
		return ""#"inline %s %s(%s);\n" % (adjustDataTypePY(self.getReturnType()) + self.getReferenceString(), self.getName(), self.getParamTypeString())
		
	def getFullCode(self):
		# TODO: Add parameters
		if self.func.isCast:
			#castType = ""
			#if self.func.castToUnmanaged:
			#	castType = adjustDataTypePY("~" + self.name)
			#else:
			#	castType = adjustDataTypePY(self.name)
			
			funcIntern = "# BP Cast: %s\n\tdef to%s(%s):\n%s" % (self.func.name, normalizeName(self.func.name), self.getParamString(), self.code)
			return funcIntern + "\n\t"
		
		# TODO: Remove hardcoded stuff (here: Operator = for ~MemPointer<ConstChar> is directly used by C++ and therefore needs no name change)
		if self.getFuncName() == "operatorAssign" and self.classImpl.getName() == "UTF8String" and self.paramTypes[0] == "~MemPointer<ConstChar>":
			funcName = "operator="
		else:
			funcName = self.getName()
		
		if self.classImpl.getName():
			tabs = "\t"
		else:
			tabs = ""
		
		return "# %s\n%sdef %s(%s):\n%s" % (funcName, tabs, funcName, self.getParamString(), self.code, tabs)
	
	# Constructor
	def getConstructorCode(self):
		# TODO: Add parameters
		return "# %s\n\tdef %s(%s):\n%s" % (self.getFuncName(), "__init__", self.getParamString(), self.code)
	
	# Destructor
	def getDestructorCode(self):
		return "# %s\n\tdef %s(%s) {\n%s" % (self.getFuncName(), "__del__", self.getParamString(), self.code)

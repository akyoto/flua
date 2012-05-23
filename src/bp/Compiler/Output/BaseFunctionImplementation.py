from bp.Compiler.Utils import *
from bp.Compiler.Output.DataTypes import *

class BaseFunctionImplementation:
	
	def __init__(self, classImpl, func, paramTypes):
		self.classImpl = classImpl
		self.func = func
		self.paramTypes = paramTypes
		
		for i in range(len(self.func.paramTypesByDefinition)):
			byDef = self.func.paramTypesByDefinition[i]
			if byDef:
				self.paramTypes[i] = self.classImpl.translateTemplateName(byDef)
		
		# Extern methods
		if self.classImpl.classObj.isExtern:
			self.name = self.func.getName()
		else:
			self.name = self.func.getName() + self.buildPostfix()
		
		self.code = ""
		self.returnTypes = []
		self.func.implementations[self.name] = self
		
	def getReturnType(self):
		heaviest = None
		
		for type in self.returnTypes:
			if type in dataTypeWeights:
				heaviest = getHeavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def buildPostfix(self):
		return buildPostfix(self.paramTypes)
	
	def setCode(self, newCode):
		self.code = newCode
		
	def getName(self):
		# main -> _bp_custom_main
		if self.name == "main":
			return "_bp_custom_main"
		return self.name
	
	def getFuncName(self):
		return self.func.getName()
		
	def getParamString(self):
		return NotImplementedError()
		
	def getParamTypeString(self):
		return NotImplementedError()
		
	def getReferenceString(self):
		return NotImplementedError()
		
	def getPrototype(self):
		return NotImplementedError()
		
	def getFullCode(self):
		return NotImplementedError()
		
	# Constructor
	def getConstructorCode(self):
		return NotImplementedError()
		
	# Destructor
	def getDestructorCode(self):
		return NotImplementedError()

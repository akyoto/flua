from flua.Compiler.Utils import *
from flua.Compiler.Output.DataTypes import *

class BaseFunctionImplementation:
	
	def __init__(self, classImpl, func, paramTypes):
		self.classImpl = classImpl
		self.func = func
		self.paramTypes = paramTypes
		
		# This impl adds these classImpl members
		#self.introducesMembers = dict()
		
		# Cache relevant variables
		self.cacheEnabled = True
		self.globalStateAccessCount = 0
		self.sideEffects = 0
		
		for i in range(len(paramTypes)): #self.func.paramTypesByDefinition
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
		self.yieldType = None
		self.yieldValue = None
		self.scope = None
		self.variablesAtStart = []
		self.func.implementations[self.name] = self
		
	# Functions with side effects
	def addSideEffect(self, num = 1):
		#print(self.classImpl.getFullName() + " :: " + self.getName() + " -> has side effects")
		self.sideEffects += num
		
	# Public member, global variables
	def addGlobalStateAccess(self):
		#print(self.classImpl.getFullName() + " :: " + self.getName() + " -> accesses global state")
		self.globalStateAccessCount += 1
		
	def disableCaching(self):
		#print(self.classImpl.getFullName() + " :: " + self.getName() + " -> has caching disabled")
		self.cacheEnabled = False
		
	def canBeCached(self):
		return self.cacheEnabled
		
	def isPureFunction(self):
		return self.sideEffects == 0 and self.globalStateAccessCount == 0
		
	def hasSideEffects(self):
		return self.sideEffects > 0
		
	def declareVariableAtStart(self, var):
		self.variablesAtStart.append(var)
		
	def setScope(self, nScope):
		self.scope = nScope
		
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
		
	def getCode(self):
		return self.code
		
	def getName(self):
		# main -> _flua_custom_main
		if self.name == "main":
			return "_flua_custom_main"
		return self.name
	
	def getFuncName(self):
		return self.func.getName()
		
	def getYieldType(self):
		return self.yieldType
		
	def getYieldValue(self):
		return self.yieldValue
		
	def getParamString(self):
		return NotImplementedError()
		
	def getParamTypeString(self):
		return NotImplementedError()
		
	def getReferenceString(self):
		return NotImplementedError()
		
	def getPrototype(self):
		return NotImplementedError()
		
	def getFullCode(self, noPostfix = False):
		return NotImplementedError()
		
	# Constructor
	def getConstructorCode(self):
		return NotImplementedError()
		
	# Destructor
	def getDestructorCode(self):
		return NotImplementedError()

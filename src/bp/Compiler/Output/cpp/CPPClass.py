from Output.cpp.CPPFunction import *
from Output.cpp.CPPVariable import *
from Output.cpp.CPPClassImplementation import *

class CPPClass:
	
	def __init__(self, name):
		self.name = name
		self.classes = {}
		self.functions = {}
		self.externFunctions = {}
		self.implementations = {}
		self.templateNames = []
		self.parent = None
		self.isExtern = False
		self.usesActorModel = False
		
	def requestImplementation(self, templateValues):
		key = ", ".join(templateValues)
		if not key in self.implementations:
			self.implementations[key] = CPPClassImplementation(self, templateValues)
		return self.implementations[key]
		
	def addClass(self, classObj):
		debug("'%s' added class '%s'" % (self.name, classObj.name))
		classObj.parent = self
		self.classes[classObj.name] = classObj
		
	def addFunction(self, func):
		debug("'%s' added function '%s'" % (self.name, func.name))
		func.classObj = self
		if not func.name in self.functions:
			self.functions[func.name] = []
		else:
			for iterFunc in self.functions[func.name]:
				if func.paramTypesByDefinition == iterFunc.paramTypesByDefinition:
					raise CompilerException("The function '%s.%s' accepting parameters of the types %s has already been defined." % (self.name, func.name, func.paramTypesByDefinition))
		self.functions[func.name].append(func)
		
	def addExternFunction(self, name, type):
		debug("'%s' added extern function '%s'" % (self.name, name))
		self.externFunctions[name] = type
	
	def setTemplateNames(self, names):
		debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
		
	def getMatchingFunction(self, funcName, paramTypes):
		#debug("Function '%s' has been called with types %s (%s to choose from)" % (funcName, paramTypes, len(self.functions[funcName])))
		candidates = self.functions[funcName]
		winner = None
		winnerScore = 0
		for func in candidates:
			score = func.getMatchingScore(paramTypes)
			#debug("Candidate: %s with score '%s'" % (func.paramTypesByDefinition, score))
			if score > winnerScore:
				winner = func
				winnerScore = score
		
		if winner is None:
			raise CompilerException("No matching function found for the call '%s.%s' with the parameter types '%s'" % (self.name, funcName, paramTypes))
		
		return winner
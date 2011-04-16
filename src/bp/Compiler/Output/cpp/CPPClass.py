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
		self.functions[func.name] = func
		
	def addExternFunction(self, name, type):
		debug("'%s' added extern function '%s'" % (self.name, name))
		self.externFunctions[name] = type
	
	def setTemplateNames(self, names):
		debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
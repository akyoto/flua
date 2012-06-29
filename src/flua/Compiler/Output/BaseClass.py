####################################################################
# Header
####################################################################
# File:		Base class
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
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
from flua.Compiler.Output.BaseNamespace import *
from flua.Compiler.Output.DataTypes import *
#from flua.Compiler.Output.BaseClassImplementation import *

####################################################################
# Functions
####################################################################
def findPublicMemberInBaseClasses(callerClass, funcName):
	for classImpl in callerClass.extends:
		classObj = classImpl.classObj
		
		#debug("Checking base class '%s' for public member '%s'" % (classObj.name, funcName))
		if classObj.hasPublicMember(funcName):
			#debug("Found public member '%s' in base class '%s'" % (funcName, classObj.name))
			return classObj.publicMembers[funcName], classImpl
		
		if classObj.extends:
			func, impl = findPublicMemberInBaseClasses(classObj, funcName)
			
			if func:
				return func, impl
	
	return None, None

####################################################################
# Classes
####################################################################
class BaseClass(BaseNamespace):
	
	def __init__(self, name, node):
		super().__init__(name)
		self.implementations = {}
		self.templateNames = []
		self.templateDefaultValues = []
		#self.defaultGetters = dict()
		#self.defaultSetters = dict()
		self.publicMembers = dict()
		self.parent = None
		self.isExtern = False
		self.usesActorModel = False
		self.isInterface = False
		self.extends = []
		self.node = node
		self.hasOverwrittenFunctions = False
		
		if self.node:
			self.ensureDestructorCall = isMetaDataTrueByTag(node, "ensure-destructor-call")
			self.forceImplementation = isMetaDataTrueByTag(node, "force-implementation")
			self.isDefaultVersion = isMetaDataTrueByTag(node, "default-class-version")
			
			if self.forceImplementation:
				self.requestDefaultImplementation()
			
			self.isExtern = self.node.parentNode.tagName == "extern"
		else:
			self.ensureDestructorCall = False
			self.forceImplementation = False
			self.isDefaultVersion = False
	
	def setOverwrittenFunctions(self, flag):
		self.hasOverwrittenFunctions = flag
		#self.ensureDestructorCall = True
	
	def hasUndefinedTemplateParams(self):
		if self.templateNames and not self.templateDefaultValues[-1]:
			return True
		else:
			return False
	
	def addPublicMember(self, name):
		self.publicMembers[name] = True
		
	def hasPublicMember(self, name):
		#debug("Checking '%s' for public member '%s'" % (self.getFinalName(), name))
		
		# Local list check
		exists = name in self.publicMembers
		
		# Check for '*' locally
		# TODO: Check if it really exists as a member
		if exists or "*" in self.publicMembers:
			return True
		
		# Check base classes
		exists, impl = findPublicMemberInBaseClasses(self, name)
		
		if exists:
			return True
		
		return False
		
	#def addDefaultGetter(self, propertyName):
	#	self.defaultGetters[propertyName] = True
		
	#def addDefaultSetter(self, propertyName):
	#	self.defaultSetters[propertyName] = True
		
	#def hasDefaultGetter(self, propertyName):
	#	return propertyName in self.defaultGetters
		
	#def hasDefaultSetter(self, propertyName):
	#	return propertyName in self.defaultSetters
		
	def getAutoCompleteList(self, private = False):
		publicMembers = list(self.publicMembers.keys())
		publicFunctions = list()
		publicIterators = list()
		
		for funcList in self.functions.values():
			func = funcList[0]
			
			if func.isGetter(): #len(func) >= 4 and func.startswith("get") and func[3].isupper(): # Members
				if not private:
					publicMembers.append(func.name)
			elif func.isIterator:
				publicIterators.append(func.name)
			elif func.isCast or func.isOperator() or func.isSetter():#len(func) >= 9 and func.startswith("operator") and func[8].isupper():# Operators
				continue
			elif not func.name in {"init", "finalize"}:
				publicFunctions.append(func.name)
		
		return publicFunctions, publicMembers, publicIterators
		
	def getFinalName(self):
		if self.name.startswith("Mutable"):
			return self.name[len("Mutable"):]
		elif self.name.startswith("Immutable"):
			return self.name[len("Immutable"):]
		
		return self.name
		
	def setExtends(self, extends):
		self.extends = extends
		
		if 0:
			cumulativeMembers = []
			for classImpl in extends:
				#print(classImpl.getFullName())
				#print(classImpl.members)
				#print(classImpl.classObj.publicMembers)
				#print(classImpl.classObj.properties)
				cumulativeMembers += list(classImpl.classObj.publicMembers.items())
				
			self.publicMembers = dict(list(self.publicMembers.items()) + cumulativeMembers)
			#print(self.publicMembers)
		
		# Also implement base classes
		#if self.forceImplementation:
		#	for classObj in self.extends:
		#		classObj.requestDefaultImplementation()
	
	def requestDefaultImplementation(self):
		self.requestImplementation([], [])
	
	def checkDefaultImplementation(self):
		for i in range(len(self.templateNames)):
			if not self.templateDefaultValues[i]:
				raise CompilerException("Can't force an implementation for a class which doesn't have default values for its template parameters")
	
	def requestImplementation(self, initTypes, templateValues):
		key = ", ".join(initTypes + templateValues)
		if not key in self.implementations:
			self.implementations[key] = self.createClassImplementation(templateValues)
		return self.implementations[key]
		
	def addClass(self, classObj):
		#debug("'%s' added class '%s'" % (self.name, classObj.name))
		classObj.parent = self
		self.classes[classObj.name] = classObj
		
	def addFunction(self, func):
		#debug("'%s' added function '%s'" % (self.name, func.getName()))
		func.classObj = self
		if not func.getName() in self.functions:
			self.functions[func.getName()] = []
		else:
			for iterFunc in self.functions[func.getName()]:
				if func.paramTypesByDefinition == iterFunc.paramTypesByDefinition:
					raise CompilerException("The function '%s.%s' accepting parameters of the types %s has already been defined." % (self.name, func.getName(), func.paramTypesByDefinition))
		
		self.functions[func.getName()].append(func)
		
		# Property setter/getter?
		if func.isGetter() or func.isSetter():
			self.properties[func.name] = func
		
	def hasFunction(self, name):
		return name in self.functions
		
	def hasOperator(self, name):
		return correctOperators(name) in self.functions
		
	def hasIterator(self, name):
		return ("iterator" + capitalize(name)) in self.functions
		
	def hasExternFunction(self, name):
		#debug(self.externFunctions)
		return name in self.externFunctions
		
	def hasCast(self, typeName):
		return typeName in self.functions
		
	def addExternFunction(self, name, type):
		#debug("'%s' added extern function '%s' of type '%s'" % (self.name, name, type))
		self.externFunctions[name] = type
		
	def addExternVariable(self, name, type):
		#debug("'%s' added extern variable '%s' of type '%s'" % (self.name, name, type))
		self.externVariables[name] = type
	
	def setTemplateNames(self, names, defaultValues):
		#debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
		self.templateDefaultValues = defaultValues

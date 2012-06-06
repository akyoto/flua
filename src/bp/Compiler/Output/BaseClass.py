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
from bp.Compiler.Utils import *
from bp.Compiler.Output.BaseNamespace import *
#from bp.Compiler.Output.BaseClassImplementation import *

####################################################################
# Classes
####################################################################
class BaseClass(BaseNamespace):
	
	def __init__(self, name, node):
		super().__init__(name)
		self.templateNames = []
		self.templateDefaultValues = []
		self.parent = None
		self.isExtern = False
		self.usesActorModel = False
		self.extends = []
		self.node = node
		
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
		
	def getPublicFunctionList(self):
		publicMembers = list()
		publicFunctions = list()
		for funcList in self.functions.values():
			func = funcList[0]
			
			if func.isGetter(): #len(func) >= 4 and func.startswith("get") and func[3].isupper(): # Members
				publicMembers.append(func.name)
			elif func.isCast or func.isOperator() or func.isSetter() or func.isIterator:#len(func) >= 9 and func.startswith("operator") and func[8].isupper():# Operators
				continue
			elif not func.name in {"init", "finalize"}:
				publicFunctions.append(func.name)
		return publicFunctions, publicMembers
		
	def getFinalName(self):
		if self.name.startswith("Mutable"):
			return self.name[len("Mutable"):]
		elif self.name.startswith("Immutable"):
			return self.name[len("Immutable"):]
		
		return self.name
		
	def setExtends(self, extends):
		self.extends = extends
		
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
		debug("'%s' added class '%s'" % (self.name, classObj.name))
		classObj.parent = self
		self.classes[classObj.name] = classObj
		
	def addFunction(self, func):
		debug("'%s' added function '%s'" % (self.name, func.getName()))
		func.classObj = self
		if not func.getName() in self.functions:
			self.functions[func.getName()] = []
		else:
			for iterFunc in self.functions[func.getName()]:
				if func.paramTypesByDefinition == iterFunc.paramTypesByDefinition:
					raise CompilerException("The function '%s.%s' accepting parameters of the types %s has already been defined." % (self.name, func.getName(), func.paramTypesByDefinition))
		self.functions[func.getName()].append(func)
		
	def hasFunction(self, name):
		return name in self.functions
		
	def hasExternFunction(self, name):
		debug(self.externFunctions)
		return name in self.externFunctions
		
	def hasCast(self, typeName):
		return typeName in self.functions
		
	def addExternFunction(self, name, type):
		debug("'%s' added extern function '%s' of type '%s'" % (self.name, name, type))
		self.externFunctions[name] = type
	
	def setTemplateNames(self, names, defaultValues):
		debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
		self.templateDefaultValues = defaultValues

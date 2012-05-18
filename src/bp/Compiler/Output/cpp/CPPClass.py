####################################################################
# Header
####################################################################
# Target:   C++ Code
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
from bp.Compiler.Output.cpp.CPPFunction import *
from bp.Compiler.Output.cpp.CPPVariable import *
from bp.Compiler.Output.cpp.CPPClassImplementation import *
from bp.Compiler.Output.cpp.CPPNamespace import *

####################################################################
# Classes
####################################################################
class CPPClass(CPPNamespace):
	
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
		else:
			self.ensureDestructorCall = False
		
	def setExtends(self, extends):
		self.extends = extends
		
	def requestImplementation(self, initTypes, templateValues):
		key = ", ".join(initTypes + templateValues)
		if not key in self.implementations:
			self.implementations[key] = CPPClassImplementation(self, templateValues)
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
		
	def addExternFunction(self, name, type):
		debug("'%s' added extern function '%s'" % (self.name, name))
		self.externFunctions[name] = type
	
	def setTemplateNames(self, names, defaultValues):
		debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
		self.templateDefaultValues = defaultValues

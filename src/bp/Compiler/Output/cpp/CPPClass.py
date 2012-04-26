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

####################################################################
# Classes
####################################################################
class CPPClass:
	
	def __init__(self, name):
		self.name = name
		self.classes = {}
		self.functions = {}
		self.externFunctions = {}
		self.implementations = {}
		self.templateNames = []
		self.templateDefaultValues = []
		self.parent = None
		self.isExtern = False
		self.usesActorModel = False
		
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
	
	def hasClassByName(self, name):
		return name in self.classes
	
	def setTemplateNames(self, names, defaultValues):
		debug("'%s' set the template names %s" % (self.name, names))
		self.templateNames = names
		self.templateDefaultValues = defaultValues
####################################################################
# Header
####################################################################
# File:		Scans for the base class
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
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
from bp.Compiler.Config import *
from bp.Compiler.Output import *
from bp.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Classes
####################################################################
class BaseOutputFileScan:
	
	def scanAhead(self, parent):
		for node in parent.childNodes:
			if isElemNode(node):
				if node.tagName == "class":
					self.scanClass(node)
				elif node.tagName == "function" or node.tagName == "operator" or node.tagName == "iterator-type":
					self.scanFunction(node)
				elif node.tagName == "getter":
					self.inGetter += 1
					result = self.scanFunction(node)
					self.inGetter -= 1
				elif node.tagName == "setter":
					self.inSetter += 1
					result = self.scanFunction(node)
					self.inSetter -= 1
				elif node.tagName == "cast-definition":
					self.inCastDefinition += 1
					result = self.scanFunction(node)
					self.inCastDefinition -= 1
				elif node.tagName == "public-member":
					self.scanPublicMember(node)
				elif node.tagName == "namespace":
					self.scanNamespace(node)
				elif node.tagName == "extern":
					self.inExtern += 1
					self.scanAhead(node)
					self.inExtern -= 1
				elif node.tagName == "operators":
					self.inOperators += 1
					self.scanAhead(node)
					self.inOperators -= 1
				elif node.tagName == "iterators":
					self.inIterators += 1
					self.scanAhead(node)
					self.inIterators -= 1
				elif node.tagName == "casts":
					self.inCasts += 1
					self.scanAhead(node)
					self.inCasts -= 1
				elif node.tagName == "define":
					self.inDefine += 1
					self.scanAhead(node)
					self.inDefine -= 1
				elif node.tagName == "public":
					self.scanAhead(node)
				#elif node.tagName == "default-get":
				#	self.scanDefaultGet(node)
				#elif node.tagName == "default-set":
				#	self.scanDefaultSet(node)
				elif node.tagName == "get" or node.tagName == "set":
					self.scanAhead(node)
				elif node.tagName == "template":
					self.inTemplate += 1
					self.scanTemplate(node)
					self.inTemplate -= 1
				elif node.tagName == "extends":
					self.inExtends += 1
					self.scanExtends(node)
					self.inExtends -= 1
				elif node.tagName == "extern-function":
					self.scanExternFunction(node)
				elif node.tagName == "extern-variable":
					self.scanExternVariable(node)
				elif node.tagName == "const":
					self.scanAhead(node)
				elif node.tagName == "assign" and self.inDefine > 0:
					self.scanDefine(node)
					
	def scanPublicMember(self, node):
		name = node.firstChild.nodeValue
		#self.currentClass.addDefaultGetter(name)
		#self.currentClass.addDefaultSetter(name)
		self.currentClass.addPublicMember(name)
	
	#def scanDefaultGet(self, node):
	#	for child in node.childNodes:
	#		propertyName = child.firstChild.nodeValue
	#		self.currentClass.addDefaultGetter(propertyName)
			
	#def scanDefaultSet(self, node):
	#	for child in node.childNodes:
	#		propertyName = child.firstChild.nodeValue
	#		self.currentClass.addDefaultSetter(propertyName)
	
	def scanTemplate(self, node):
		pNames, pTypes, pDefaultValues, pDefaultValueTypes = self.getParameterList(node)
		self.currentClass.setTemplateNames(pNames, pDefaultValues)
		if self.currentClass.forceImplementation:
			self.currentClass.checkDefaultImplementation()
	
	def scanExtends(self, node):
		pNames, pTypes, pDefaultValues, pDefaultValueTypes = self.getParameterList(node)
		self.currentClass.setExtends([self.getClassImplementationByTypeName(className) for className in pNames])
	
	def scanClass(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		extendingClass = False
		
		self.pushScope()
		
		if name in self.compiler.mainClass.classes:
			refClass = self.compiler.mainClass.classes[name]
			extendingClass = True
			oldClass = self.currentClass
			self.currentClass = refClass
		else:
			refClass = self.createClass(name, node)
			if refClass.isDefaultVersion:
				self.compiler.specializedClasses[refClass.getFinalName()] = refClass
			self.pushClass(refClass)
			self.localClasses.append(self.currentClass)
		
		self.scanAhead(getElementByTagName(node, "code"))
		
		if extendingClass:
			self.currentClass = oldClass
		else:
			self.popClass()
		self.popScope()
	
	# Namespaces
	def scanNamespace(self, node):
		name = getElementByTagName(node, "name").firstChild.nodeValue
		codeNode = getElementByTagName(node, "code")
		
		self.pushNamespace(name)
		self.scanAhead(codeNode)
		self.popNamespace()
	
	# Typedefs
	def scanDefine(self, node):
		defineWhat = self.parseExpr(node.firstChild.firstChild)
		defineAs = self.parseExpr(node.childNodes[1].firstChild)
		self.compiler.defines[defineWhat] = defineAs
	
	def scanFunction(self, node):
		if self.inCastDefinition:
			name = self.parseExpr(getElementByTagName(node, "to").childNodes[0], True)
			
			# Replace typedefs
			name = self.prepareTypeName(name)
		else:
			#print(node.toprettyxml())
			nameNode = getElementByTagName(node, "name")
			if nameNode.childNodes:
				name = nameNode.childNodes[0].nodeValue
			else:
				name = ""
		
		#if self.inGetter:
		#	getElementByTagName(node, "name").childNodes[0].nodeValue = name = "get" + capitalize(name)
		#elif self.inSetter:
		#	getElementByTagName(node, "name").childNodes[0].nodeValue = name = "set" + capitalize(name)
		# Index operator
		name = correctOperators(name)
		
		newFunc = self.createFunction(node)
		paramNames, paramTypesByDefinition, paramDefaultValues, paramDefaultValueTypes = self.getParameterList(getElementByTagName(node, "parameters"))
		newFunc.paramNames = paramNames
		newFunc.paramTypesByDefinition = paramTypesByDefinition
		newFunc.paramDefaultValues = paramDefaultValues
		newFunc.paramDefaultValueTypes = paramDefaultValueTypes
		#debug("Types:" + str(newFunc.paramTypesByDefinition))
		self.currentClass.addFunction(newFunc)
		
		if self.currentClass.name == "":
			self.localFunctions.append(newFunc)
		
		if isMetaDataTrue(getMetaData(node, "force-implementation")):
			newFunc.setForceImplementation(True)
		
		# Save variables for the IDE
		if self.compiler.background:
			self.tryGettingVariableTypes(newFunc)
		
		# TODO: Needs to handle declare-type as well
		#if name == "init":
		#	for x in newFunc.assignNodes:
		#		#print(x.toxml())
		#		accessNode = x.firstChild.firstChild
		#		if accessNode.nodeType == Node.ELEMENT_NODE and accessNode.tagName == "access":
		#			if accessNode.firstChild.firstChild.nodeValue == "my":
		#				memberName = accessNode.childNodes[1].firstChild.nodeValue
		#				self.currentClass.possibleMembers memberName
		
	def tryGettingVariableTypes(self, func):
		func.assignNodes = findNodes(func.node, "assign")
		
	def scanExternFunction(self, node):
		name = self.getNamespacePrefix() + getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		# TODO: Remove hardcoded
		if type == "CString":
			type = "~MemPointer<Byte>"
		
		# Typedefs
		type = self.prepareTypeName(type)
		
		self.compiler.mainClass.addExternFunction(name, type)
		
	def scanExternVariable(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		typeName = "Int"
		
		if types:
			typeName = types[0].childNodes[0].nodeValue
		
		# TODO: Remove hardcoded
		if typeName == "CString":
			typeName = "~MemPointer<Byte>"
		
		# Typedefs
		typeName = self.prepareTypeName(typeName)
		
		self.compiler.mainClass.addExternVariable(name, typeName)

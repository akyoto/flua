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
from flua.Compiler.Config import *
from flua.Compiler.Output import *
from flua.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Classes
####################################################################
class BaseOutputFileScan:
	
	def scanAhead(self, parent):
		for node in parent.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				if node.tagName in {"class", "interface"}:
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
				#elif node.tagName == "public-member":
				#	self.scanPublicMember(node)
				elif node.tagName == "namespace":
					self.scanNamespace(node)
				elif node.tagName == "extern":
					if (not self.compiler.hasExternCache) or self.isMainFile:
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
					self.scanPublic(node)
					#self.scanAhead(node)
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
				elif node.tagName in {"extends", "implements"}:
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
	
	def scanPublic(self, node):
		pNames, pTypes, pDefaultValues, pDefaultValueTypes = self.getParameterList(node)
		
		for i in range(len(pNames)):
			memberName = pNames[i]
			memberType = pTypes[i]
			
			if not memberType:
				# Last parsed node for debugging purposes
				self.compiler.lastParsedNodes.append(node.childNodes[i])
				
				raise CompilerException("The member variable declaration of „%s“ in a public block of class „%s“ must be given a type" % (memberName, self.currentClass.name))
			
			if memberName.startswith("__"):
				raise CompilerException("Don't use 'my', 'self' or 'this' in the member variable declaration of „%s“ in a public block of class „%s“" % (memberName[2:], self.currentClass.name))
			
			self.currentClass.addPublicMember(memberName, memberType)
		
		# Remove this node
		#self.lastParsedNode.pop()
		
	#def scanPublicMember(self, node):
	#	name = node.firstChild.nodeValue
		#self.currentClass.addDefaultGetter(name)
		#self.currentClass.addDefaultSetter(name)
	#	self.currentClass.addPublicMember(name)
	
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
		
		if node.tagName == "interface":
			refClass.isInterface = True
		
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
		#debug("Namespace scan: %s" % name)
		
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
		typeNode = getElementByTagName(node, "type")
		
		if typeNode:
			type = typeNode.firstChild.nodeValue
			
			# TODO: Remove hardcoded
			if type == "CString":
				type = "~MemPointer<Byte>"
		else:
			type = "void"
		
		# Typedefs
		type = self.prepareTypeName(type)
		
		self.compiler.mainClass.addExternFunction(name, type)
		
	def scanExternVariable(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		typeNode = getElementByTagName(node, "type")
		
		if typeNode:
			typeName = typeNode.firstChild.nodeValue
			
			# TODO: Remove hardcoded
			if typeName == "CString":
				typeName = "~MemPointer<Byte>"
		else:
			typeName = "Int"
		
		# Typedefs
		typeName = self.prepareTypeName(typeName)
		
		self.compiler.mainClass.addExternVariable(name, typeName)

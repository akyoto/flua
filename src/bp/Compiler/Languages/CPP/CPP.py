####################################################################
# Header
####################################################################
# Language: C++
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
from Languages.ProgrammingLanguage import *
from xml.etree.ElementTree import ElementTree

####################################################################
# Classes
####################################################################
class LanguageCPP(ProgrammingLanguage):
	
	def __init__(self):
		self.extensions = ["cpp"]
		self.classes = dict()
		#self.builtClasses = dict()
		
		self.classes[""] = CPPClass()
		self.classes["Int"] = CPPClass()
		
	def compileXML(self, root):
		headerNode = root.find("header")
		codeNode = root.find("code")
		
		self.scanElementChilds(codeNode)
		
		for type, typeObject in self.classes.items():
			print("Type: " + type)
			for meth in typeObject.methods.keys():
				print(" Method: " + meth)
			for func in typeObject.functions.keys():
				print(" Function: " + func)
		
		header = "//" + headerNode.find("title").text
		code = self.compileElementChilds(codeNode)
		
		for typeObject in self.classes.values():
			for cppFunc in typeObject.builtFunctions.values():
				code += "\n" + cppFunc
			for cppFunc in typeObject.builtMethods.values():
				code += "\n" + cppFunc
		
		for child in headerNode.find("dependencies").getchildren():
			header += "\n#include <" + child.text.replace(".", "/") + ">"
		
		return header + "\n" + code
	
	def scanElement(self, elem, parentClass = None):
		if elem.tag == "function":
			className = ""
			if parentClass:
				className = parentClass
			funcName = elem.get("name")
			print("Registering function " + className + "." + funcName)
			self.classes[className].functions[funcName] = elem
		if elem.tag == "method":
			className = ""
			if parentClass:
				className = parentClass
			funcName = elem.get("name")
			print("Registering method " + className + "." + funcName)
			self.classes[className].methods[funcName] = elem
		elif elem.tag == "class":
			className = elem.get("name")
			self.classes[className] = CPPClass()
			self.scanElementChilds(elem, className)
		elif elem.tag == "public":
			self.scanElementChilds(elem, parentClass)
		elif elem.tag == "private":
			self.scanElementChilds(elem, parentClass)
	
	def scanElementChilds(self, elem, parentClass = None):
		for child in elem.getchildren():
			self.scanElement(child, parentClass)
	
	def compileElement(self, elem):
		if elem.tag == "code":
			return self.compileElementChilds()
		elif elem.tag == "call":
			obj = self.getExprFromXML(elem.find("object"))
			callerType = self.getExprDataTypeFromXML(elem.find("object"))
			func = elem.get("function")
			
			if not self.classes.get(callerType).builtFunctions.get(func):
				caller = self.classes.get(callerType)
				
				if caller is None:
					raise CompileError("Unknown object '" + callerType + "'.")
				
				if callerType is not "" and callerType is not "DataType":
					funcElem = caller.methods.get(func)
					if not funcElem:
						compileWarning("Method " + callerType + "." + func + " could not be found.")
					else:
						self.classes.get(callerType).builtMethods[func] = self.buildFunction(funcElem, elem)
				else:
					funcElem = caller.functions.get(func)
					if not funcElem:
						compileWarning("Function " + obj + "." + func + " could not be found.")
					else:
						self.classes.get(obj).builtFunctions[func] = self.buildFunction(funcElem, elem)
			if obj:
				return obj + "->" + func + "(" + self.compileElementChilds(elem, ", ", "") + ")"
			else:
				return elem.get("function") + "(" + self.compileElementChilds(elem, ", ", "") + ")"
		elif elem.tag == "value" or elem.tag == "condition" or elem.tag == "parameter":
			return self.getExprFromXML(elem)
		elif elem.tag == "new":
			# TODO: If data type is "DataType" use it as a template parameter
			return "new " + elem.get("datatype") + "(" + self.compileElementChilds(elem, ", ", "") + ")"
		elif elem.tag == "compare":
			return self.compileElementChilds(elem, " == ", "")
		elif elem.tag == "add":
			return self.compileElementChilds(elem, " + ", "")
		elif elem.tag == "return":
			return "return " + self.getExprFromXML(elem)
		elif elem.tag == "var":
			value = self.getExprFromXML(elem)
			valueDataType = str(self.getExprDataTypeFromXML(elem))
			varDataType = elem.get("datatype")
			
			if not varDataType:
				varDataType = ""
			else:
				varDataType = str(varDataType)
			
			if not varDataType:
				varDataType = valueDataType
			
			if value:
				if varDataType is not valueDataType:
					raise CompileError("Variable type '" + varDataType + "' does not match value type '" + valueDataType + "'.")
				return varDataType + " " + elem.get("name") + " = " + value
			else:
				return varDataType + " " + elem.get("name")
		elif elem.tag == "function" or elem.tag == "method":
			# This is covered in the scan function
			return ""
		elif elem.tag == "while":
			return "while(" + self.compileElement(elem.find("condition")) + ") {\n" + self.compileElementChilds(elem.find("code")) + "\n}"
		elif elem.tag == "public":
			return "public:\n" + self.compileElementChilds(elem)
		elif elem.tag == "class":
			# Move this code to buildClass
			base = elem.get("base")
			extends = ""
			if base:
				extends = ": " + base
			return "class " + elem.get("name") + extends + " {\n" + self.compileElementChilds(elem) + "\n}"
		
		if elem:
			compileWarning("Unknown XML element '" + elem.tag + "'")
			return elem.text.strip()
		else:
			return ""
		
	# TODO: buildFunction with class parameter
	def buildFunction(self, elem, call):
		return self.getFunctionReturnType(elem) + " " + elem.get("name") + "(" + self.getFunctionParameters(elem, call) + ")" + " {\n" + self.compileElementChilds(elem.find("code")) + "\n}"
		
	# TODO: buildClass
		
	def getFunctionParameters(self, func, call = None):
		paras = ""
		
		callType = []
		if call:
			for parameter in call:
				callType.append(self.getExprDataTypeFromXML(parameter))
			pass
		
		counter = 0
		for parameter in func:
			if parameter.tag == "parameter":
				oldType = parameter.find("var").get("datatype")
				if oldType is None:
					parameter.find("var").set("datatype", callType[counter])
				paras += self.compileElement(parameter) + ", "
				parameter.find("var").set("datatype", oldType)
			counter += 1
		return paras[:-2]
		
	def getFunctionReturnType(self, elem):
		return "void"
	
	def canBeCastedTo(self, dataTypeFrom, dataTypeTo):
		return False
		
	def compileElementChilds(self, elem, separator = "\n", postfix = ";"):
		stri = ""
		instruction = ""
		for child in elem.getchildren():
			instruction = self.compileElement(child)
			if instruction:
				stri += instruction + postfix + separator
			
		if separator:
			return stri[:-len(separator)]
		else:
			return stri
		
	def getExprDataTypeFromXML(self, elem):
		if elem is None:
			return ""
		
		inner = elem.text.strip()
		if inner:
			if inner.isdigit():
				return "Int"
			else:
				return self.getVarType(inner)
		else:
			# TODO: Type combination
			return ""
			#for child in elem.getchildren():
			#	self.getExprDataTypeFromXML(child)
		
	def getVarType(self, name):
		# TODO: Get variable data type
		return name
		
	def getExprFromXML(self, elem):
		if elem == None:
			return ""
		
		inner = elem.text.strip()
		if inner:
			return inner
		else:
			return self.compileElementChilds(elem, "", "")
	
	def getExprFromCode(self, code):
		# TODO: Mathematical expression parser
		return ""
		
	def getName(self):
		return "C++"

class CPPClass:
	
	def __init__(self):
		self.methods = dict()
		self.functions = dict()
		self.builtMethods = dict()
		self.builtFunctions = dict()
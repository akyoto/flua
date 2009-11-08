####################################################################
# Header
####################################################################
# Language: Blitz Max
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
		
	def compileXML(self, root):
		headerNode = root.find("header")
		codeNode = root.find("code")
		header = "//" + headerNode.find("title").text
		code = self.compileElementChilds(codeNode)
		
		for child in headerNode.find("dependencies").getchildren():
			header += "\n#include <" + child.text.replace(".", "/") + ">"
		
		return header + "\n" + code
	
	def compileElement(self, elem):
		if elem.tag == "code":
			return self.compileElementChilds()
		elif elem.tag == "call":
			obj = elem.get("object")
			if obj:
				return obj + "->" + elem.get("function") + "(" + self.compileElementChilds(elem, ", ") + ")"
			else:
				return elem.get("function") + "(" + self.compileElementChilds(elem, ", ") + ")"
		elif elem.tag == "value" or elem.tag == "condition" or elem.tag == "parameter":
			return self.getExprFromXML(elem)
		elif elem.tag == "compare":
			return self.compileElementChilds(elem, " == ")
		elif elem.tag == "class":
			base = elem.get("base")
			extends = ""
			if base:
				extends = ": " + base
			return "class " + elem.get("name") + extends + " {\n" + self.compileElementChilds(elem) + "\n};"
		elif elem.tag == "while":
			return "while(" + self.compileElement(elem.find("condition")) + ") {\n" + self.compileElementChilds(elem.find("code")) + "\n}"
		return ""
		
	def compileElementChilds(self, elem, separator = "\n"):
		stri = ""
		for child in elem.getchildren():
			stri += self.compileElement(child) + separator
			
		if separator:
			return stri[:-len(separator)]
		else:
			return stri
		
	def getExprFromXML(self, elem):
		inner = elem.text.strip()
		if inner:
			return inner
		else:
			return self.compileElementChilds(elem)
	
	def getExprFromCode(self, code):
		# TODO: Mathematical expression parser
		return ""
		
	def getName(self):
		return "C++"
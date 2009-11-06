####################################################################
# Header
####################################################################
# Language: Console BASIC
# Author:   coolo

####################################################################
# License
####################################################################
# (C) 2009  coolo
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
from ProgrammingLanguage import *
from xml.etree.ElementTree import ElementTree, Element, SubElement

####################################################################
# Classes
####################################################################
class LanguageCB(ProgrammingLanguage):
	
	def __init__(self):
		self.extensions = ["cb"]
		
	def compileXML(self, root):
		return ""
		
	def compileCodeToXML(self, code):
		root = Element("root")
		header = SubElement(root, "header")
		code = SubElement(root, "code")
		
		tree = ElementTree(root)
		return tree
		
	def getName(self):
		return "Console BASIC"
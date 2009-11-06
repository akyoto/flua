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
	codeText="" # der Text von der Klasse
	tokens=[] # Die Liste der Tokens
	
	def __init__(self): # Konstruktor
		self.extensions = ["cb"]
		print("Hallo")
	def compileXML(self, root): # kompiliert aus der XML Datei Code
		return ""
		
	def compileCodeToXML(self, code): # erzeugt XML Code aus cb (console BASIC) dateien
		root = Element("module")
		headerNode = SubElement(root, "header")
		codeNode = SubElement(root, "code")
		
		
		tree = ElementTree(root)
		return tree
	#def startLexer(self):
	#	# zerlege alles in Tokens
	#	for char in self.codeText:
	#		if char=='+' or char=='-' or char=='+' or char=='*' or char=='/':
			
	#def startAnalyser(self):
	# Analysiert die Tokens (welche Primitive Typen es sind)
	
		
	#def startAnalyser2(self):
	# genauerers analysieren  (welcher Datentyp wo steht, wie viele Parameter eine Funktion hat, etc.)

	#def startSyntaxTree(self):
	# erzeugt den Syntaxbaum

	#def startGenerator(self):
	# erzeugt die XML Datei
	def getName(self):
		return "Console BASIC"
class Token:
	text="" # der Text vom Token
	primitiveType="" # der Primtive Type (Zahl, String,...)
	
	def __init__(self): # Konstruktor
		text=""
		primtiveType=""
		
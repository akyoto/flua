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
	# Konstruktor
	def __init__(self):
		# der Text von der Klasse
		self.codeText = ""
		
		# Die Liste der Tokens
		self.tokens = []
		
		# File extensions
		self.extensions = ["cb"]
		print("Hallo")
		
	# kompiliert aus der XML Datei Code
	def compileXML(self, root):
		return ""
	
	# erzeugt XML Code aus cb (console BASIC) dateien
	def compileCodeToXML(self, code):
		root = Element("module")
		headerNode = SubElement(root, "header")
		codeNode = SubElement(root, "code")
		
		
		tree = ElementTree(root)
		return tree
	def startLexer(self):
		# zerlege alles in Tokens
		
		# Ob der Lexer sich gerade in einem String befindet
		inString = false
		
		# Ob der Lexer sich gerade in einem Kommentar befindet
		inComment = false
		
		# Der Text der durchgegangen wurde seit dem letzen mal
		lastText = ""
		
		for char in self.codeText:
			# Schauen ob ein String ist
			if char == '"':
				if inString == false:
					inString = true
				elif inString == true:
					inString = true
			# Fuehre das nur aus wenn der Lexer nicht gerade in einem String/Kommentar ist
			if inString == false and inComment == false:
				# Mathematik Operatoren
				if char == '+' or char == '-' or char == '+' or char == '*' or char == '/':
					# Erzeuge den Text davor Token
					self.tokens.append(Token(lastText))
					# Erzeuge das Operator Token
					self.tokens.append(Token(char))
					# Setze lastText wieder auf nichts
					lastText = ''
				# Sonderzeichen
				elif char == ' ' or char == ':' or char == '\n':
					# Erzeuge den Text davor Token
					self.tokens.append(Token(lastText))
					# Erzeuge das Operator Token
					self.tokens.append(Token(char))
					# Setze lastText wieder auf nichts
					lastText = ''
				# Kommentare
				elif char == '//' or char == "'":
					inComment = true
				# Wenn nichts gefunden wurde fuege es dem lastText hinzu
				else:
					lastText = lastText + char
			else:
				lastText = ''
			# Wenn neue Zeile ist, setze die Kommentare wieder zurueck
			if char == '\n' and inComment == true:
				inComment=false

		#curText = ''
		for curText in self.tokens:
			pass
			
	# Analysiert die Tokens (welche Primitive Typen es sind)
	def startAnalyzer(self):
		pass
	
	# genauerers analysieren  (welcher Datentyp wo steht, wie viele Parameter eine Funktion hat, etc.)
	def startAnalyzer2(self):
		pass
		
	# erzeugt den Syntaxbaum
	def startSyntaxTree(self):
		pass
		
	# erzeugt die XML Datei
	def startGenerator(self):

		pass

	def getName(self):
		return "Console BASIC"
	
class Token:
	
	# Konstruktor
	def __init__(self, text):
		# der Text vom Token
		self.text = ""
		
		# der Primtive Type (Zahl, String,...)
		self.primtiveType = ""
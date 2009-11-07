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
		
		# Datentypen (dazu zaehlen auch vom User definierte Klassen) - darum ist es auch eine Liste
		# smallint=2byte
		# int=4 byte
		# bigint=8byte
		# usw.
		dataTypes = ["int","smallint","bigint","float","bigfloat","smallfloat","string"]
	# kompiliert aus der XML Datei Code
	def compileXML(self, root):
		return ""
	
	# erzeugt XML Code aus cb (console BASIC) dateien
	def compileCodeToXML(self, code):
		root = Element("module")
		headerNode = SubElement(root, "header")
		codeNode = SubElement(root, "code")
		
		# Setze den Text von der Datei
		self.codeText = code
		
		# Lexe die Datei
		self.startLexer()
		
		# Nun analysiere den Code im ersten Durchlauf
		self.startAnalyzer()
		
		tree = ElementTree(root)
		return tree
	# Zerteilt den Code in Tokens, soweit es geht
	def startLexer(self):
		# zerlege alles in Tokens
		
		# Ob der Lexer sich gerade in einem String befindet
		inString = False
		
		# Ob der Lexer sich gerade in einem Kommentar befindet
		inComment = False
		
		# Der Text der durchgegangen wurde seit dem letzen mal
		lastText = ""
		
		for char in self.codeText:
			# Schauen ob ein String ist
			if char == '"':
				if inString == False:
					inString = True
				elif inString == True:
					inString = True
			# Fuehre das nur aus wenn der Lexer nicht gerade in einem String/Kommentar ist
			if inString == False and inComment == False:
				# Mathematik Operatoren
				if Token.isOperator(char):
					# Erzeuge den Text davor Token
					self.tokens.append(Token(self,lastText))
					# Erzeuge das Operator Token
					self.tokens.append(Token(self,char))
					# Setze lastText wieder auf nichts
					lastText = ''
				# Sonderzeichen
				elif char == ':':# or char == '\n':
					# Erzeuge den Text davor Token
					self.tokens.append(Token(self,lastText))
					# Erzeuge das Operator Token
					self.tokens.append(Token(self,char))
					# Setze lastText wieder auf nichts
					lastText = ''
				# Kommentare
				elif char == '//' or char == "'":
					inComment = True
				# Bei Leerzeichen einfach ignorieren
				elif char == ' ' or char == '	':
					self.tokens.append(Token(self,lastText))
					lastText = ""
				# Wenn nichts einfach ignorieren
				elif char == '':
					lastText = ''
				# Wenn nichts gefunden wurde fuege es dem lastText hinzu
				else:
					lastText = lastText + char
			else:
				lastText = ''
			# Wenn neue Zeile ist, setze die Kommentare wieder zurueck
			if char == '\n' and inComment == True:
				inComment=false
				
	# Analysiert die Tokens (welche Primitive Typen es sind)
	# Erkennt die Funktionen/Variablen/Konstanten
	def startAnalyzer(self):
		for token in self.tokens:
			token.analyze()
	
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

# Ein Token, dies ist die zerlegte Datei
class Token:
	# So sieht ein Operator aus
	operators = ("+", "-", "*", "/", "^", "or", "and", "xor", "=", "<", ">", "<=", ">=")
	# Der & Operator ist zum verketten von Strings gedacht, der wird gesondert gemanaget, da er anders als diese Operatoren
	# Keine Zahl (Float/Int) verlangt
	
	# Die Schluesselwoerter
	# Schleifen
	loopKeyword = ("exit", "continue", "repeat", "until", "while", "wend", "for", "to", "next")
	
	# Abfragen
	checkKeyword = ("if", "then", "else", "elseif", "endif", "select", "case", "default", "endselect")
	
	# Code (Function, Sub,...)
	codeKeyword = ("function", "endfunction", "return", "sub", "endsub")
	
	# Variablen deklarationen,...
	variableKeyword = ("local", "global", "const", "static", "dim", "localdim", "globaldim", "staticdim")
	
	# Die Primitiven TokenTypen (Die die schon im ersten durchlauf erkannt werden koennen, anhand einfacher Syntax Regeln)
	# Ob dieser Token eine Variable ist (von der Syntax Regel her)
	primIsVariable = 1
	# Ob dieser Token eine Literale (=Konstanter Wert) ist
	primIsLiteral = 2
	# Ob dieser Token ein Keyword ist
	primIsKeyword = 3
	# Ob dieser Token ein Operator ist
	primIsOperator = 4
	# Ein unbekanntes Token (wird spaeter ueberprueft)
	primIsUnknown = 5
	
	# Konstruktor
	def __init__(self, compiler, text = str):
		# Setzt den Zeiger auf den Compiler
		self.compiler = compiler
		
		# der Text vom Token
		self.text = text
		
		# der Primtive Type (Zahl, String,...)
		self.primtiveType = ""
	def analyze(self):
		
		# Wenn der Token leer ist, lösche ihn
		if self.getText == "":
			self.compiler.tokens.remove(self)
		# Ist der Token ein Operator?
		if Token.isOperator(self.getText()):
			self.primtiveType = Token.primIsOperator
		# Könnte der Token eine Variable sein?
		elif isValidVarName(self.getText()):
			self.primtiveType = Token.primIsVariable
	def getText(self):
		self.text = self.text.expandtabs().strip()
		return self.text
	def isOperator(text):
		operatorText = ""
		
		for operatorText in Token.operators:
			if operatorText == text:
				return True
		return False

# Eine Variable/Funktion
class Identifier:
	# Ob dieser Identifier eine Variable ist
	isVariable = 1
	# Ob dieser Identifier eine Funktion ist
	isFunction = 2
	
	def __init__(self, text, token):
		# Der Text vom Idetifier
		self.text = text
		# Der Token zu dem es gehört
		self.owner = token
		self.typ = Idenifier.isVariable
class Scope
	def __init__(self, compiler):
		self.compiler = compiler

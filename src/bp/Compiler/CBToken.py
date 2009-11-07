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

# Ein Token, dies ist die zerlegte Datei
class Token:
	# So sieht ein Operator aus
	operators = ("+", "-", "*", "/", "^", "or", "and", "xor", "=", "<", ">", "<=", ">=","(",")",",")
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
	# localdim = dim = deklariert ein lokales Array
	# globaldim = deklariert ein globales Array
	# staticdim = deklariert ein statisches Array
	
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
		self.setText(text)
		
		# der Primtive Type (Zahl, String,...)
		self.primtiveType = ""
		
		# der Konkrete Type
		self.concretType = ""
	def setText(self, text):
		self.text=text
	def getText(self):
		if self.text.find('"') == -1:
			self.text = self.text.expandtabs().strip().lower()
		return self.text

def isOperator(text):
	operatorText = ""
	
	for operatorText in Token.operators:
		if operatorText == text:
			return True
	return False
def isKeyword(text):
	keywordText = ""
	
	# Schauen ob es eine Schleife ist
	for keywordText in Token.loopKeyword:
		if keywordText == text:
			return True
	
	# Schauen ob es eine Abfrage ist
	for keywordText in Token.checkKeyword:
		if keywordText == text:
			return True
	
	# Schauen ob es ein code Keyword ist (Function, sub,...)
	for keywordText in Token.codeKeyword:
		if keywordText == text:
			return True
	
	#schauen ob es ein Variablen Keyword isz
	for keywordText in Token.variableKeyword:
		if keywordText == text:
			return True
	return False
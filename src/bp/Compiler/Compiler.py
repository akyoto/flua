####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
# Website: www.blitzprog.de
# Started: 19.07.2008 (Sat, Jul 19 2008)

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
from Languages import *
from Utils import *
from xml.etree.ElementTree import ElementTree
import time

####################################################################
# Classes
####################################################################
class Compiler:
	
	def __init__(self):
		self.languages = []
		
	def invoke(self, args):
		for arg in args:
			print(arg)
		
	def addLanguage(self, language):
		self.languages.append(language)
		
	def compileXML(self, xmlRoot, language):
		return language.compileXML(xmlRoot)
		
	def compileCodeToXML(self, code, language):
		return language.compileCodeToXML(code)
		
	def compileXMLFile(self, inFile, outFile):
		ext = extractExt(outFile)
		
		for lang in self.languages:
			try:
				if lang.extensions.index(ext) != -1:
					print("Lang: " + lang.getName())
					
					root = ElementTree()
					root.parse(inFile)
					code = self.compileXML(root, lang)
					with open(outFile, "w") as out:
						out.write(code)
					print(code)
			except ValueError:
				pass
		
	def compileCodeToXMLFile(self, inFile, outFile):
		ext = extractExt(inFile)
		
		for lang in self.languages:
			try:
				if lang.extensions.index(ext) != -1:
					print("Lang: " + lang.getName())
					
					with open(inFile, "r") as inStream:
						code = inStream.read()
					root = self.compileCodeToXML(code, lang)
					root.write(outFile)
			except ValueError:
				pass

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		compiler = Compiler()
		
		compiler.addLanguage(CB.LanguageCB())
		compiler.addLanguage(CPP.LanguageCPP())
		
		print("---------")
		print("CB to XML")
		print("---------")
		start = time.clock()
		
		compiler.compileCodeToXMLFile("coolo-test.cb", "coolo-test.xml")
		
		elapsedTime1 = time.clock() - start
		
		print("---------")
		print("XML to C++")
		print("---------")
		start = time.clock()
		
		compiler.compileXMLFile("Test.xml", "Test.cpp")
		
		elapsedTime2 = time.clock() - start
		
		print("Time[1]:    " + str(elapsedTime1 * 1000) + " ms")
		print("Time[2]:    " + str(elapsedTime2 * 1000) + " ms")
		
		if 0:
			import subprocess
			subprocess.call(["L:\\home\\eduard\\Apps\\BlitzMax\\bin\\bmk.exe", "makeapp", "L:\\home\\eduard\\Projects\\blitzprog\\src\\bp\\Compiler\\Test.bmx"])
	except:
		printTraceback()
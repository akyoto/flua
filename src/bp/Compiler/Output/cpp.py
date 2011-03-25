####################################################################
# Header
####################################################################
# Target:   C++ Code
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
from Utils import *
import codecs

####################################################################
# Classes
####################################################################
class CPPOutputCompiler:
	
	def __init__(self, inpCompiler):
		self.inputCompiler = inpCompiler
		self.inputFiles = inpCompiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.projectDir = self.inputCompiler.projectDir
		self.modDir = inpCompiler.modDir
		self.stringCounter = 0;
		self.fileCounter = 0;
		self.outputDir = ""
	
	def compile(self):
		for inpFile in self.inputFiles:
			cppOut = CPPOutputFile(self, inpFile)
			cppOut.compile()
			self.compiledFiles[inpFile] = cppOut
			self.compiledFilesList.insert(0, cppOut)
	
	def writeToFS(self, dirOut):
		dirOut = fixPath(os.path.abspath(dirOut)) + "/"
		self.outputDir = dirOut
		
		for cppFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + ".hpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				outStream.write(cppFile.getCode())
			
			# CPP main file
			if cppFile.isMainFile:
				hppFile = os.path.basename(fileOut)
				fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + ".cpp"
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
	def build(self):
		os.chdir(self.outputDir)
		os.system("g++ main.cpp -o main -I/home/eduard/Projects/bp/src/bp/Compiler/Test/Output")
		return "/home/eduard/Projects/bp/src/bp/Compiler/Test/Output/main"
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.compiledFilesList:
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
class CPPOutputFile:
	
	def __init__(self, compiler, inpFile):
		self.compiler = compiler
		self.file = inpFile.file
		self.root = inpFile.getRoot()
		self.isMainFile = inpFile.isMainFile
		self.dir = inpFile.dir
		self.codeNode = self.root.getElementsByTagName("code")[0]
		self.headerNode = self.root.getElementsByTagName("header")[0]
		self.dependencies = self.headerNode.getElementsByTagName("dependencies")[0]
		self.strings = self.headerNode.getElementsByTagName("strings")[0]
		
		#self.id = self.file.replace("/", "_").replace(".", "_")
		self.id = "file_" + str(self.compiler.fileCounter)
		self.compiler.fileCounter += 1
		
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.topLevel = ""
		self.footer = "#endif\n"
		
	def compile(self):
		print("Output: " + self.file)
		
		# Header
		self.header += "// Includes\n";
		self.header += "#include <cstdio>\n"
		for node in self.dependencies.childNodes:
			self.header += self.handleImport(node)
		
		self.header += "\n"
		
		# Strings
		self.header += "// Strings\nnamespace " + self.id + "_strings" + " {\n";
		for node in self.strings.childNodes:
			self.header += self.handleString(node)
		self.header += "};\n"
		
		# Code
		self.topLevel += "// Code\n";
		self.topLevel += "void exec_" + self.id + "() {\n"
		for node in self.codeNode.childNodes:
			if isTextNode(node):
				self.topLevel += node.nodeValue
			else:
				self.topLevel += self.parseExpr(node) + ";\n";
		self.topLevel += "}\n"
		
		#print(self.getCode())
		
	def parseExpr(self, node):
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_strings::" + node.nodeValue
			else:
				return node.nodeValue
		elif node.tagName == "call":
			funcName = node.getElementsByTagName("function")[0].childNodes[0]
			params = node.getElementsByTagName("parameters")[0]
			return self.parseExpr(funcName) + "(" + self.parseExpr(params) + ")"
		elif node.tagName == "parameters":
			return self.handleParameters(node)
		
		return "";
		
	def handleString(self, node):
		id = node.getAttribute("id")
		value = node.childNodes[0].nodeValue
		line = "	const char *" + id + " = \"" + value + "\";\n"
		self.compiler.stringCounter += 1
		return line
		
	def handleParameters(self, pNode):
		pList = ""
		for node in pNode.childNodes:
			pList += self.parseExpr(node.childNodes[0]) + ", "
		
		return pList[:len(pList)-2]
	
	def handleImport(self, node):
		importedModulePath = node.childNodes[0].nodeValue.replace(".", "/")
		
		# Local
		importedFile = self.dir + importedModulePath + ".bpc"
		
		importedInFolder = self.dir + importedModulePath
		importedInFolder += "/" + stripAll(importedInFolder) + ".bpc"
		
		# Project
		pImportedFile = self.compiler.projectDir + importedModulePath + ".bpc"
		
		pImportedInFolder = self.compiler.projectDir + importedModulePath
		pImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		# Global
		gImportedFile = self.compiler.modDir + importedModulePath + ".bpc"
		
		gImportedInFolder = self.compiler.modDir + importedModulePath
		gImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		modPath = ""
		
		if os.path.isfile(importedFile):
			modPath = importedFile
		elif os.path.isfile(importedInFolder):
			modPath = importedInFolder
		elif os.path.isfile(pImportedFile):
			modPath = pImportedFile
		elif os.path.isfile(pImportedInFolder):
			modPath = pImportedInFolder
		elif os.path.isfile(gImportedFile):
			modPath = pImportedFile
		elif os.path.isfile(gImportedInFolder):
			modPath = pImportedInFolder
		
		modPath = modPath[len(self.compiler.projectDir):]
		
		return "#include <" + stripExt(modPath) + ".hpp>\n"
		
	def getCode(self):
		return self.header + "\n" + self.topLevel + "\n" + self.footer
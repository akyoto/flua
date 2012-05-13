####################################################################
# Header
####################################################################
# Syntax:   Blitzprog Code
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
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
from bp.Compiler.Input.bpc.BPCUtils import *
from bp.Compiler.Input.bpc.BPCFile import *

####################################################################
# Classes
####################################################################
class BPCCompiler:
	
	def __init__(self, modDir, importExtension = ".bpc"):
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.projectDir = ""
		self.importExtension = importExtension
		self.modDir = fixPath(os.path.abspath(modDir)) + "/"
		self.initExprParser()
	
	def getProjectDir(self):
		return self.projectDir
	
	def getCompiledFiles(self):
		return self.compiledFilesList
	
	def getFileInstanceByPath(self, path):
		return self.compiledFiles[path]
	
	def initExprParser(self):
		self.parser = getBPCExpressionParser()
	
	def compile(self, mainFile):
		fileIn = fixPath(os.path.abspath(mainFile))
		
		# Emptiness check
		isMainFile = not self.compiledFiles
		
		if isMainFile:
			self.projectDir = os.path.dirname(fileIn) + "/"
		
		bpcFile = self.spawnFileCompiler(fileIn, isMainFile)
		
		self.compiledFiles[fileIn] = bpcFile
		self.compiledFilesList.append(bpcFile)
		
		for file in bpcFile.importedFiles:
			if not file in self.compiledFiles:
				# TODO: Change directory
				self.compile(file)
		
	def spawnFileCompiler(self, fileIn, isMainFile, codeText = "", perLineFunc = None):
		try:
			myFile = BPCFile(self, fileIn, isMainFile)
			myFile.compile(codeText, perLineFunc)
		except CompilerException as e:
			raise InputCompilerException(str(e), myFile)
		return myFile
	
	# TODO: Remove dirOut
	def writeToFS(self, dirOut):
		dirOut = os.path.abspath(dirOut) + "/"
		
		for bpcFile in self.compiledFiles.values():
			bpcFile.writeToFS()

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		print("Starting:")
		start = time.clock()
		
		modDir = "../../../"
		compileFile = "../Test/Input/main.bpc"
		
		bpc = BPCCompiler(modDir)
		bpc.compile(compileFile)
		bpc.writeToFS("../Test/Output/")
		
		elapsedTime = time.clock() - start
		print("Time:    " + str(elapsedTime * 1000) + " ms")
		print("Done.")
	except:
		printTraceback()

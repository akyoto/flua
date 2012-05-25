####################################################################
# Header
####################################################################
# File:		Base class for output compilers
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
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

####################################################################
# Classes
####################################################################
class BaseOutputCompiler(Benchmarkable):
	
	def __init__(self, inpCompiler):
		if inpCompiler:
			self.inputCompiler = inpCompiler
			self.inputFiles = inpCompiler.getCompiledFiles()
			self.projectDir = self.inputCompiler.getProjectDir()
		else:
			self.projectDir = ""
			
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.modDir = getModuleDir()
		self.bpRoot = fixPath(os.path.abspath(self.modDir + "../"))
		
		self.stringDataType = "UTF8String"
		self.defines = dict()
		self.includes = list()
		self.specializedClasses = dict()
		self.funcImplCache = dict()
		self.needToInitStringClass = False
		
		# Counter
		self.stringCounter = 0
		self.fileCounter = 0
		self.forVarCounter = 0
		
		# Main class
		self.mainClass = self.createClass("", None)
		self.mainClassImpl = self.mainClass.requestImplementation([], [])
		
		# Optimization
		self.enableOptimization()
		
		# Expression parser
		self.initExprParser()
	
	# Abstract
	def build(self, compilerFlags, fhOut, fhErr):
		raise NotImplementedError("build")
	
	def getTargetName(self):
		raise NotImplementedError("Target name not specified")
	
	def getExePath(self):
		raise NotImplementedError()
	
	def writeToFS(self):
		raise NotImplementedError()
		
	def compile(self, inpFile):
		raise NotImplementedError()
		
	def getCompiledFiles(self):
		return self.compiledFiles
	
	# Other stuff
	def initExprParser(self):
		self.parser = getBPCExpressionParser()
	
	def getProjectDir(self):
		return self.projectDir
		
	def getCompiledFilesList(self):
		return self.compiledFilesList
		
	# Optimization
	def enableOptimization(self):
		self.optimize = True
		self.updateOptimizationFlags()
		
	def disableOptimization(self):
		self.optimize = False
		self.updateOptimizationFlags()
		
	def updateOptimizationFlags(self):
		# TODO: Module dependant setting
		self.checkDivisionByZero = True
		self.optimizeStringConcatenation = self.optimize
	
	# Building and executing
	def genericCompile(self, inpFile, cppOut):
		if len(self.compiledFiles) == 0:
			self.mainFile = cppOut
			self.projectDir = extractDir(self.mainFile.getFilePath())
		
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		
		# Compile imported files first
		for imp in inpFile.getImportedFiles():
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		# This needs to be executed AFTER the imported files have been compiled
		# It'll make sure the files are called in the correct (recursive) order
		self.compiledFilesList.append(cppOut)
		
		# After the dependencies have been compiled, compile itself
		try:
			# Check whether string class has been defined or not
			# NOTE: This has to be called before self.scanAhead is executed.
			cppOut.stringClassDefined = cppOut.classExists("UTF8String")
			
			# Find classes, functions, operators and external stuff
			cppOut.scanAhead(cppOut.codeNode)
			
			# Compile it
			cppOut.compile()
		except CompilerException as e:
			raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
		
		# Change string class
		#if self.mainClass.hasClassByName("UTF8String"):
		#	self.stringDataType = "~UTF8String"
	
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		cmd = [exe]
		
		try:
			startProcess(cmd, fhOut, fhErr)
		except OSError:
			print("Can't execute '%s'" % exe)
	
	def getFileExecList(self):
		return NotImplementedError()

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
	
	def __init__(self, inpCompiler, background = False):
		if inpCompiler:
			self.inputCompiler = inpCompiler
			self.inputFiles = inpCompiler.getCompiledFiles()
			self.projectDir = self.inputCompiler.getProjectDir()
		else:
			self.projectDir = ""
		
		# TODO: Remove redundant data
		self.outFiles = dict()
		self.outFilesList = list()
		self.compiledFiles = dict()
		self.compiledFilesList = list()
		
		self.modDir = getModuleDir()
		self.bpRoot = fixPath(os.path.abspath(self.modDir + "../"))
		
		self.stringDataType = "UTF8String"
		self.defines = dict()
		self.includes = list()
		self.specializedClasses = dict()
		self.funcImplCache = dict()
		self.parseStringCache = dict()
		self.needToInitStringClass = False
		self.assignNodes = list()
		
		# Main class
		self.mainClass = self.createClass("", None)
		self.mainClassImpl = self.mainClass.requestImplementation([], [])
		
		# Background compiler?
		self.reset(background)
		
		# Expression parser
		self.initExprParser()
	
	# Take cache from another compiler instance - BE CAREFUL, THIS COULD LEAD TO MEMORY LEAKS
	def takeOverCache(self, o):
		self.parseStringCache = o.parseStringCache
		
	def reset(self, background):
		# Background compiler?
		self.background = background
		
		# Counter
		self.stringCounter = 0
		self.fileCounter = 0
		self.forVarCounter = 0
		self.forEachVarCounter = 0
		self.inVarCounter = 0
		
		# Optimization
		if self.background:
			self.disableOptimization()
		else:
			self.enableOptimization()
	
	# Abstract
	def build(self, compilerFlags, fhOut, fhErr):
		raise NotImplementedError("build")
	
	def getTargetName(self):
		raise NotImplementedError("Target name not specified")
	
	def getExePath(self):
		raise NotImplementedError()
	
	def writeToFS(self):
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
	
	def getMainFile(self):
		return self.mainFile
	
	def tryGettingVariableTypesInUnimplementedFunctions(self):
		for funcList in self.mainClass.functions.values():
			func = funcList[0]
			
			# TODO: if not func.implementations ?
			
			assignNodes = func.assignNodes
			
			self.mainFile.pushScope()
			for node in assignNodes:
				try:
					self.mainFile.handleAssign(node)
					#print("It worked: %s" % node.toxml())
				except:
					continue
			self.mainFile.saveScopesForNode(func.node)
			self.mainFile.popScope()
	
	def scan(self, inpFile, silent = False):
		cppOut = self.createOutputFile(inpFile)
		
		if len(self.outFiles) == 0:
			self.mainFile = cppOut
			self.projectDir = extractDir(self.mainFile.getFilePath())
			cppOut.isMainFile = True
		else:
			cppOut.isMainFile = False
		
		self.outFiles[inpFile] = cppOut
		
		# Scan imported files
		for imp in inpFile.getImportedFiles():
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.outFiles):
				self.scan(inFile)
				
		# This needs to be executed AFTER the imported files have been compiled
		# It'll make sure the files are called in the correct (recursive) order
		self.outFilesList.append((inpFile, cppOut))
		
		# Scanning the file itself
		#if not silent:
		#	print("Scanning: %s" % cppOut.file)
				
		# Check whether string class has been defined or not
		# NOTE: This has to be called before self.scanAhead is executed.
		cppOut.stringClassDefined = cppOut.classExists("UTF8String")
		
		# Find classes, functions, operators and external stuff
		# UTF8String module will find UTF8String class e.g.
		cppOut.scanAhead(cppOut.codeNode)
		
	def compile(self, inpFile, silent = False):
		self.scan(inpFile, silent)
		
		for inpFile, outFile in self.outFilesList:
			#print("Compiling: %s" % outFile.file)
			self.genericCompile(inpFile, outFile, silent)
		
	# Building and executing
	def genericCompile(self, inpFile, cppOut, silent = False):
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		
		# Compile imported files first
		#for imp in inpFile.getImportedFiles():
		#	inFile = self.inputCompiler.getFileInstanceByPath(imp)
		#	if (not inFile in self.compiledFiles):
		#		self.compile(inFile)
		
		self.compiledFilesList.append(cppOut)
		
		# Kinda hardcoded, yeah...we want to prevent the UTF8String module
		# from thinking UTF8String has already been defined.
		#if stripAll(cppOut.getFilePath()) != "UTF8String":
		#	cppOut.stringClassDefined = cppOut.classExists("UTF8String")
		
		# After the dependencies have been compiled, compile itself
		try:
			# String class init
			cppOut.checkStringClass()
			
			if not silent:
				print("Compiling: " + cppOut.file)
			
			# Compile it
			cppOut.compile()
		except CompilerException as e:
			raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
		
		# Change string class
		#if self.mainClass.hasClassByName("UTF8String"):
		#	self.stringDataType = "~UTF8String"
	
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write, thread = None):
		cmd = [exe]
		
		try:
			return startProcess(cmd, fhOut, fhErr, thread)
		except OSError:
			print("Can't execute '%s'" % exe)
			
		return -1
	
	def getFileExecList(self):
		return NotImplementedError()

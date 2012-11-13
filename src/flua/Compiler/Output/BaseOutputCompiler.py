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
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from flua.Compiler.Utils import *
from flua.Compiler.Config import *

####################################################################
# Functions
####################################################################
def checkInterfaceImplementation(classObj, interface):
	#debug("Checking „%s“ for implementation of interface „%s“" % (classObj.name, interface.name))
	
	for method in interface.functions:
		if not classObj.hasFunction(method):
			raise CompilerException("Class „%s“ does not define the „%s“ method of interface „%s“" % (classObj.name, method, interface.name))

####################################################################
# Classes
####################################################################
class BaseOutputCompiler(Benchmarkable):
	
	def __init__(self, inpCompiler, background = False, guiCallBack = None):
		Benchmarkable.__init__(self)
		
		if inpCompiler:
			self.inputCompiler = inpCompiler
			self.inputFiles = inpCompiler.getCompiledFiles() #inputFiles
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
		self.funcImplCacheStarted = dict()
		self.parseStringCache = dict()
		self.needToInitStringClass = False
		self.assignNodes = list()
		self.funcDataFlowRequests = list()
		self.prototypes = list()
		self.strings = list()
		self.operators = dict()
		self.tuples = dict()
		self.customThreads = dict()
		self.functionsAsPointers = dict()
		self.functionPointerCalls = dict()
		self.loopStack = list()
		self.lastParsedNodes = list()
		
		self.lastParsedFile = None
		self.guiCallBack = guiCallBack
		self.hasExternCache = False
		
		# Options
		self.enableIterVarPrefixes = True
		self.checkDoubleVarDefinition = True
		
		# Main class
		self.mainClass = self.createClass("", None)
		self.mainClassImpl = self.mainClass.requestImplementation([], [])
		
		# Background compiler?
		self.reset(background)
		
		# Expression parser
		self.initExprParser()
	
	def getLastParsedNode(self):
		if not self.lastParsedNodes:
			return None
		
		return self.lastParsedNodes[-1]
		
	def getLastParsedNodes(self):
		if not self.lastParsedNodes:
			return None
		
		return self.lastParsedNodes
	
	def getFunctionCount(self):
		count = len(self.mainClass.functions)
		
		for classObj in self.mainClass.classes.values():
			count += len(classObj.functions)
			
		#for namespaceObj in self.mainClass.namespaces.values():
		#	count += len(namespaceObj.functions)
			
		return count
	
	# Take cache from another compiler instance - BE CAREFUL, THIS COULD LEAD TO MEMORY LEAKS
	def takeOverCache(self, o):
		self.parseStringCache = o.parseStringCache
		
		#print(o.funcImplCache)
		
		#self.funcImplCache = o.funcImplCache
		
		#self.mainClass = o.mainClass
		#self.mainClassImpl = o.mainClassImpl
		
		#self.mainClass.classes.pop("UTF8String")
		
		#self.stringClassDefined = o.stringClassDefined
		
		#for key, funcImpl in o.funcImplCache.items():
		#	if funcImpl.canBeCached():
		#		print("CACHE:    " + key)
		#	else:
		#		print("NO CACHE: " + key)
		
		self.mainClass.externFunctions = o.mainClass.externFunctions
		self.mainClass.externVariables = o.mainClass.externVariables
		self.mainClass.namespaces = o.mainClass.namespaces
		
		for className, classObj in o.mainClass.classes.items():
			if classObj.isExtern:
				self.mainClass.classes[className] = classObj
		
		self.hasExternCache = True
		
	def reset(self, background):
		# Background compiler?
		self.background = background
		
		# Counter
		self.stringCounter = 0
		self.fileCounter = 0
		self.forVarCounter = 0
		self.inVarCounter = 0
		self.onVarCounter = 0
		self.structCounter = 0
		self.tupleUnbindCounter = 0
		
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
		
		# Build a dictionary
		for opLevel in self.parser.operatorLevels:
			for op in opLevel.operators:
				self.operators[op.name] = op
	
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
		# TODO: This ain't really working...
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
			
			# Clear the cache from the entries for the current file
			if self.hasExternCache:
				newClassesDict = dict()
				
				for className, classObj in self.mainClass.classes.items():
					if classObj.getFilePath() != inpFile.getFilePath():
						newClassesDict[className] = classObj
				
				self.mainClass.classes = newClassesDict
				
			#	self.mainClass.externVariables
			#	self.mainClass.namespaces
		else:
			cppOut.isMainFile = False
		
		# Set callback
		cppOut.perParseChilds = self.guiCallBack
		
		self.outFiles[inpFile] = cppOut
		
		# Scan imported files
		try:
			for imp in inpFile.getImportedFiles():
				# Don't compile core inside core
				if isPartOfCore(self.mainFile.getFilePath()) and isCore(imp):
					continue
				
				inFile = self.inputCompiler.getFileInstanceByPath(imp)
				if (not inFile in self.outFiles):
					self.scan(inFile)
		except OutputCompilerException:
			raise
		except CompilerException as e:
			raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
					
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
		try:
			cppOut.scanAhead(cppOut.codeNode)
		except OutputCompilerException:
			raise
		except CompilerException as e:
			raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
		
	def compile(self, inpFile, silent = False):
		#self.startBenchmark("Scanning")
		self.scan(inpFile, silent)
		#self.endBenchmark()
		
		# 330 ms for flua.Compiler.Benchmark on my Core 2 Duo.
		# Can we do this faster?
		self.startBenchmark("Compiling")
		for inpFile, outFile in self.outFilesList:
			#print("Compiling: %s" % outFile.file)
			self.genericCompile(inpFile, outFile, silent)
		self.endBenchmark()
		
	# Building and executing
	def genericCompile(self, inpFile, cppOut, silent = False):
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		cppOut.inpFile = inpFile
		
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
		except OutputCompilerException:
			raise
		except CompilerException as e:
			if self.lastParsedFile:
				raise OutputCompilerException(e.getMsg(), self.lastParsedFile, self.lastParsedFile.inpFile)
			else:
				raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
		
		# Change string class
		#if self.mainClass.hasClassByName("UTF8String"):
		#	self.stringDataType = "~UTF8String"
	
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write, thread = None):
		cmd = [exe]
		
		try:
			return startProcess(cmd, fhOut, fhErr, thread)
		except OSError:
			print("Can't execute „%s“" % exe)
			
		return -1
	
	def getFileExecList(self):
		return NotImplementedError()

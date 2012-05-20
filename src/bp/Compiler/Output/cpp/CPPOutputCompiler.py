####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2011  Eduard Urbach
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
from bp.Compiler.Output.cpp.CPPOutputFile import *
from bp.Compiler.Utils import *
from bp.Compiler.Config import *
import codecs
import subprocess
import os
import sys

####################################################################
# Classes
####################################################################
class CPPOutputCompiler(Benchmarkable):
	
	def __init__(self, inpCompiler = None):
		
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
		
		# OS and architecture
		if os.name == "nt":
			platform = "windows"
		else:#elif os.name == "posix":
			platform = "linux"
		
		architecture = "x86"
		
		self.libsDir = fixPath(os.path.abspath("%s../libs/cpp/%s/%s/" % (self.modDir, platform, architecture)))
		self.stringCounter = 0
		self.fileCounter = 0
		self.forVarCounter = 0
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.customCompilerFlags = []
		self.customLinkerFlags = []
		self.funcImplCache = {}
		self.includes = []
		self.stringDataType = "UTF8String"
		self.needToInitStringClass = False
		self.customThreadsCount = 0
		self.defines = dict()
		self.specializedClasses = dict()
		
		self.mainClass = CPPClass("", None)
		self.mainClassImpl = self.mainClass.requestImplementation([], [])
		
		if os.name == "nt":
			self.staticStdcppLinking = True
		else:
			self.staticStdcppLinking = False
		
		self.boehmGCEnabled = True
		self.gmpEnabled = True
		
		# Optimization
		self.enableOptimization()
		
		# Expression parser
		self.initExprParser()
		
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
		
	def initExprParser(self):
		self.parser = getBPCExpressionParser()
		
	def getProjectDir(self):
		return self.projectDir
		
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile.getFilePath(), inpFile.getRoot())
		
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
			cppOut.compile()
		except CompilerException as e:
			raise OutputCompilerException(e.getMsg(), cppOut, inpFile)
		
		# Change string class
		#if self.mainClass.hasClassByName("UTF8String"):
		#	self.stringDataType = "~UTF8String"
	
	def writeToFS(self):
		#dirOut = fixPath(os.path.abspath(dirOut))
		#self.outputDir = dirOut
		cppFiles = self.compiledFiles.values()
		
		# Implement all casts
		for cppFile in cppFiles:
			cppFile.implementCasts()
		
		# Write to files
		for cppFile in cppFiles:
			#fileOut = dirOut + stripExt(os.path.relpath(cppFile.file, self.projectDir)) + "-out.hpp"
			#fileOut = stripExt(cppFile.file) + "-out.hpp"
			fileOut = extractDir(cppFile.file) + self.getTargetName() + "/" + stripAll(cppFile.file) + ".hpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			#print(fileOut)
			with codecs.open(fileOut, "w", encoding="utf-8") as outStream:
				outStream.write(cppFile.getCode())
			
			# Write CPP main file (main-out.cpp)
			if cppFile.isMainFile:
				hppFile = os.path.basename(fileOut)
				
				#fileOut = stripExt(cppFile.file[len(self.projectDir):]) + "-out.cpp"
				#fileOut = stripExt(cppFile.file) + "-out.cpp"
				fileOut = extractDir(cppFile.file) + self.getTargetName() + "/" + stripAll(cppFile.file) + ".cpp"
				self.mainCppFile = fileOut
				
				gcInit = ""
				if self.boehmGCEnabled:
					gcInit = "\tGC_INIT();\n"
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include <bp_decls.hpp>\n#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + gcInit + self.getFileExecList() + "\treturn 0;\n}\n")
		
		# Decls file
		self.outputDir = extractDir(os.path.abspath(self.mainCppFile))
		fileOut = self.outputDir + "bp_decls.hpp"
		with open(fileOut, "w") as outStream:
			outStream.write("#ifndef " + "bp__decls__hpp" + "\n#define " + "bp__decls__hpp" + "\n\n")
			
			if self.boehmGCEnabled:
				#outStream.write("#include <gc/gc.h>\n")
				outStream.write("#define BP_USE_BOEHM_GC\n")
			
			if self.gmpEnabled:
				outStream.write("#define BP_USE_GMP\n")
			
			# Module import helper
			#outStream.write("#define CPP_MODULE(x) <x.hpp>")
			#outStream.write("#define BP_MODULE(x) <x-out.hpp>")
			
			# Include precompiled header
			outStream.write("#include <precompiled/all.hpp>\n")
			
			for dataType, definition in dataTypeDefinitions.items():
				outStream.write("typedef %s %s;\n" % (definition, dataType))
			#outStream.write("typedef %s %s;\n" % ("CString", "String"))
			
			#outStream.write("#define %s %s\n" % ("Ptr", "boost::shared_ptr"))
			#outStream.write("#define %s %s\n" % ("BP_PTR_DECL(x)", "Ptr< x >"))
			outStream.write("#define %s %s\n" % ("BP_PTR_DECL(x)", "x*"))
			
			outStream.write("\n")
			
			# Classes
			for className, classObj in self.mainClass.classes.items():
				if classObj.templateNames:
					outStream.write("template <typename %s> " % (", typename ".join(classObj.templateNames)))
				outStream.write("class BP%s;\n" % (className))
			
			#for implName, impl in self.mainClass.implementations[""].funcImplementations:
			#	outStream.write("// func %s;\n" % (implName))
			
			# Extern functions
			for externFunc in self.mainClass.externFunctions:
				outStream.write("// extern func %s;\n" % (externFunc))
			
			# Includes
			for incl in self.includes:
				outStream.write("#include <%s>\n" % (incl))
			
			outStream.write("\n#endif\n")
	
	def getExePath(self):
		exe = stripExt(self.mainCppFile)
		
		#if os.name == "nt":
		#	exe += ".exe"
		
		return exe
	
	def build(self, compilerFlags = [], fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		exe = self.getExePath()
		
		compilerName = getGCCCompilerName()
		
		compilerPath = getGCCCompilerPath()
		currentPath = os.path.abspath("./")
		
		if os.name == "nt":
			os.chdir(compilerPath)
		
		if self.boehmGCEnabled:
			if os.name == "posix":
				self.customCompilerFlags.append("-DGC_LINUX_THREADS")
		
		# Compiler
		ccCmd = [
			compilerName,
			"-c",
			fixPath(self.mainCppFile),
			"-o%s" % fixPath(exe + ".o"),
			"-I" + fixPath(self.outputDir),
			"-I" + fixPath(self.modDir),
			"-I" + fixPath("%sinclude/cpp/" % (self.bpRoot)),
			"-I" + fixPath("%sinclude/cpp/gmp/" % (self.bpRoot)),
			#"-L" + self.libsDir,
		] + self.customCompilerFlags + compilerFlags + [
			#"-pipe",
			
			#"-frerun-cse-after-loop",
			#"-frerun-loop-opt",
			#"-ffast-math",
			#"-O3",
			#"-march=native",
			#"-mtune=native",
			
			"-pthread",
			"-Wno-div-by-zero",
			"-Wall",
			"-std=c++0x",
			"-m32",
		]
		
		# Linker options
		additionalLibs = []
		
		# Use GMP?
		if self.gmpEnabled:
			additionalLibs += [
				"-lgmpxx",
				"-lgmp",
			]
		
		# Boehm GC
		if self.boehmGCEnabled:
			additionalLibs += [
				"-lgccpp",
				"-lgc",
				"-lpthread",
			]
		
		if self.staticStdcppLinking:
			staticRuntime = [
				"-static-libgcc",
				"-static-libstdc++",
			]
		else:
			# Dynamic linking seems to be faster on Linux
			staticRuntime = []
		
		# Linker
		linkCmd = [
			compilerName,
			"-o%s" % fixPath(exe),
			fixPath(exe + ".o"),
			"-L" + fixPath(self.libsDir),
			#"-ltheron",
			#"-lboost_thread",
			#"-lpthread"
		] + staticRuntime + additionalLibs + self.customLinkerFlags
		
		try:
			self.startBenchmark()
			print("\nStarting compiler:")
			print(" \\\n ".join(ccCmd))
			
			exitCode = startProcess(ccCmd, fhOut, fhErr)
			self.endBenchmark()
			
			if exitCode:
				fhOut("C++ compiler exception")
				return exitCode
			
			self.startBenchmark()
			print("\nStarting linker:")
			print("\n ".join(linkCmd))
			
			startProcess(linkCmd, fhOut, fhErr)
			self.endBenchmark()
			
			if exitCode:
				return exitCode
			
		except OSError:
			print("Couldn't start " + compilerName)
		finally:
			if os.name == "nt":
				os.chdir(currentPath)
		
		return 0
	
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		cmd = [exe]
		
		try:
			startProcess(cmd, fhOut, fhErr)
		except OSError:
			print("Can't execute '%s'" % exe)
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.compiledFilesList:
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"

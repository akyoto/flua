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
from bp.Compiler.Output.BaseOutputCompiler import *
from bp.Compiler.Output.cpp.CPPOutputFile import *
import codecs
import subprocess
import os
import sys

####################################################################
# Classes
####################################################################
class CPPOutputCompiler(BaseOutputCompiler):
	
	def __init__(self, inpCompiler = None):
		super().__init__(inpCompiler)
		
		# OS and architecture
		if os.name == "nt":
			platform = "windows"
		else:#elif os.name == "posix":
			platform = "linux"
		
		architecture = "x86"
		
		self.libsDir = fixPath(os.path.abspath("%s../libs/cpp/%s/%s/" % (self.modDir, platform, architecture)))
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.customCompilerFlags = []
		self.customLinkerFlags = []
		self.includes = []
		self.customThreadsCount = 0
		
		if os.name == "nt":
			self.staticStdcppLinking = True
		else:
			self.staticStdcppLinking = False
		
		self.boehmGCEnabled = True
		self.gmpEnabled = True
	
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile.getFilePath(), inpFile.getRoot())
		self.genericCompile(inpFile, cppOut)
	
	def createClass(self, name, node):
		return CPPClass(name, node)
	
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
				self.customCompilerFlags.append("-pthread")
		
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
	
	def getCompiledFiles(self):
		return self.compiledFiles
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.getCompiledFilesList():
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"

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
from flua.Compiler.Output.BaseOutputCompiler import *
from flua.Compiler.Output.cpp.CPPOutputFile import *
import codecs
import subprocess
import os
import sys
import platform

####################################################################
# Classes
####################################################################
class CPPOutputCompiler(BaseOutputCompiler):
	
	def __init__(self, inpCompiler = None, background = False):
		super().__init__(inpCompiler, background)
		
		# OS and architecture
		if os.name == "nt":
			self.operatingSystem = "windows"
		else:#elif os.name == "posix":
			self.operatingSystem = "linux"
		

		self.is64Bit = ("64" in platform.architecture()[0])
		
		if os.name == "nt":
			# No support for 64 bit Windows atm
			self.is64Bit = False
		
		if self.is64Bit:
			self.architecture = "x64"
		else:
			self.architecture = "x86"
		
		self.libsDir = fixPath(os.path.abspath("%s../libs/cpp/%s/%s" % (self.modDir, self.operatingSystem, self.architecture)))
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.customCompilerFlags = []
		self.customLinkerFlags = []
		self.customThreadsCount = 0
		
		if os.name == "nt":
			self.staticStdcppLinking = False#True
		else:
			self.staticStdcppLinking = False
		
		self.boehmGCEnabled = True
		self.gmpEnabled = False # will be enabled if BigInt is used
		self.tinySTMEnabled = False
	
	def createOutputFile(self, inpFile):
		return CPPOutputFile(self, inpFile.getFilePath(), inpFile.getRoot())
	
	def createClass(self, name, node):
		return CPPClass(name, node)
	
	def writeToFS(self):
		#dirOut = fixPath(os.path.abspath(dirOut))
		#self.outputDir = dirOut
		cppFiles = self.compiledFiles.values()
		
		# Implement all casts
		for cppFile in cppFiles:
			try:
				cppFile.implementCasts()
			except CompilerException as e:
				raise OutputCompilerException(e.getMsg(), cppFile, None)
		
		# Implement all used data flow functions BEFORE we call getCode() on all files
		for func, flowToFuncName in self.funcDataFlowRequests:
			for funcImpl in func.implementations.values():
				returnType = funcImpl.getReturnType()
				
				# Find the matching function for the return type
				flowToFuncImpl = self.mainFile.implementFunction("", flowToFuncName, [returnType])
		
		# Write to files
		for cppFile in cppFiles:
			#fileOut = dirOut + stripExt(os.path.relpath(cppFile.file, self.projectDir)) + "-out.hpp"
			#fileOut = stripExt(cppFile.file) + "-out.hpp"
			dirName = fixPath(extractDir(cppFile.file))
			if dirName[-1] != "/":
				dirName += "/"
			
			fileOut = dirName + self.getTargetName() + "/" + stripAll(cppFile.file) + ".hpp"
			
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
				
				fileOut = dirName + self.getTargetName() + "/" + stripAll(cppFile.file) + ".cpp"
				self.mainCppFile = fileOut
				
				initCode = ""
				exitCode = ""
				
				if self.boehmGCEnabled:
					initCode += "\tGC_INIT();\n"
				
				if self.tinySTMEnabled:
					initCode += "\tstm_init();\n"
					exitCode += "\tstm_exit();\n"
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include <flua_decls.hpp>\n#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + initCode + self.getFileExecList() + exitCode + "\treturn 0;\n}\n")
		
		# Decls file
		self.outputDir = extractDir(os.path.abspath(self.mainCppFile))
		fileOut = self.outputDir + "flua_decls.hpp"
		with open(fileOut, "w") as outStream:
			outStream.write("#ifndef " + "flua__decls__hpp" + "\n#define " + "flua__decls__hpp" + "\n\n")
			
			if self.boehmGCEnabled:
				#outStream.write("#include <gc/gc.h>\n")
				outStream.write("#define BP_USE_BOEHM_GC\n")
			
			if self.tinySTMEnabled:
				outStream.write("#define BP_USE_TINYSTM\n")
			
			# Module import helper
			#outStream.write("#define CPP_MODULE(x) <x.hpp>")
			#outStream.write("#define BP_MODULE(x) <x-out.hpp>")
			
			# Include precompiled header
			outStream.write("#include <precompiled/all.hpp>\n")
			
			# AFTER the precompiled header
			if self.gmpEnabled:
				outStream.write("#define BP_USE_GMP\n")
				outStream.write("#include <gmpxx.h>\n")
				outStream.write("#include <gmp.h>\n")
			
			for dataType, definition in dataTypeDefinitions.items():
				if dataType == "BigInt" and not self.gmpEnabled:
					continue
				
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
			
			# Tuples
			for typeId in self.tuples.keys():
				outStream.write("class BPTuple_%s_;\n" % typeId)
			
			# Prototypes
			outStream.write("\n// Strings\n")
			outStream.write(''.join(self.strings))
			
			# Prototypes
			outStream.write("\n// Prototypes\n")
			outStream.write(''.join(self.prototypes))
			
			# Extern functions
			for externFunc in self.mainClass.externFunctions:
				outStream.write("// extern func %s;\n" % (externFunc))
			
			# Custom Threads
			outStream.write('\n// Threads\n' + '\n'.join(self.customThreads.values()) + '\n')
			
			# Includes
			for incl, ifndef in self.includes:
				outStream.write("#ifndef %s\n\t#define   %s\n\t#include <%s>\n#endif\n\n" % (ifndef, ifndef, incl))
				
			# TODO: Change std::vector to BPVector
			outStream.write("#include <vector>\n")
			
			# Data flow for functions
			flowType = "void"
			for func, flowToFuncName in self.funcDataFlowRequests:
				activateFlowCode = []
				for funcImpl in func.implementations.values():
					funcImplName = funcImpl.getName()
					returnType = funcImpl.getReturnType()
					
					# Find the matching function for the return type
					flowToFuncImpl = self.mainFile.implementFunction("", flowToFuncName, [returnType])
					flowToFuncImplName = flowToFuncImpl.getName()
					
#					outStream.write("""inline void %s_dataflow_wrapper(%s _ret) {
#	%s(_ret);
#}""" % (flowToFuncImplName, adjustDataTypeCPP(returnType), flowToFuncImplName))
					outStream.write("typedef void (*%s)(%s);\n" % (funcImplName + "_listener_type", adjustDataTypeCPP(returnType)))
					outStream.write("std::vector<%s_listener_type> %s_listeners;\n" % (funcImplName, funcImplName))
					
					activateFlowCode.append("%s_listeners.push_back(reinterpret_cast<%s_listener_type>(%s));\n" % (funcImplName, funcImplName, flowToFuncImplName))
				
				outStream.write("""inline %s %s__flow_to__%s() {
	%s
}
""" % (flowType, func.getName(), flowToFuncName, ''.join(activateFlowCode)))
			
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
		
		#if os.name == "nt":
		#	os.chdir(compilerPath)
		
		if self.boehmGCEnabled:
			if os.name == "posix":
				#self.customCompilerFlags.append("-I" + fixPath("%sinclude/cpp/musl/" % (self.bpRoot)))
				#self.customCompilerFlags.append("-specs")
				#self.customCompilerFlags.append(fixPath(self.libsDir) + "musl-gcc.specs")
				#self.customCompilerFlags.append("-DGC_LINUX_THREADS")
				self.customCompilerFlags.append("-pthread")
		
		# Compiler
		ccCmd = [
			compilerPath + compilerName,
			"-c",
			fixPath(self.mainCppFile),
			"-o%s" % fixPath(exe + ".o"),
			"-I" + fixPath(self.outputDir),
			"-I" + fixPath(self.modDir),
			"-I" + fixPath("%sinclude/cpp/" % (self.bpRoot)),
			"-I" + fixPath("%sinclude/cpp/gmp/" % (self.bpRoot)),
			"-I" + fixPath("%sinclude/cpp/atomic_ops/" % (self.bpRoot)),
			#"-L" + self.libsDir,
		] + self.customCompilerFlags + compilerFlags + [
			#"-pipe",
			
			#"-frerun-cse-after-loop",
			#"-frerun-loop-opt",
			#"-ffast-math",
			#"-O3",
			#"-march=native",
			#"-mtune=native",
			
			"-Wall",
			"-Wno-div-by-zero", # We check for div by zero
			"-Wno-sign-compare", # Weird stuff
			"-Wno-parentheses", # TODO: Check
			"-Wno-unused-label", # We create unused labels in loops but that's fine
			
			"-std=c++0x",
			["-m32", "-m64"][self.is64Bit],
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
			if os.name == "nt":
				additionalLibs += [
					"-lgccpp.dll",
					"-lgc.dll",
					"-lpthread",
				]
			else:
				additionalLibs += [
					"-lgccpp",
					"-lgc",
					"-lpthread",
				]
		
		# TinySTM?
		if self.tinySTMEnabled:
			additionalLibs += [
				"-lstm",
			]
		
		# Static linking?
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
			compilerPath + compilerName,
			"-o%s" % fixPath(exe),
			fixPath(exe + ".o"),
			"-L" + fixPath(self.libsDir),
			#"-ltheron",
			#"-lboost_thread",
		] + staticRuntime + additionalLibs + self.customLinkerFlags
		
		try:
			self.startBenchmark()
			print("\nStarting compiler:")
			print(" \\\n ".join(ccCmd))
			
			exitCode = startProcess(ccCmd, fhOut, fhErr)
			
			if exitCode:
				#fhOut("C++ compiler exception")
				return exitCode
			
			self.endBenchmark()
			
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
	
	def debug(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write, thread = None):
		cmd = [getGCCCompilerPath() + "gdb", exe]
		
		try:
			fhOut(str(cmd))
			return startProcess(cmd, fhOut, fhErr, thread, bytewise = True)
		except OSError:
			print("Can't execute '%s'" % exe)
			
		return -1
	
	def getCompiledFiles(self):
		return self.compiledFiles
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.getCompiledFilesList():
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"

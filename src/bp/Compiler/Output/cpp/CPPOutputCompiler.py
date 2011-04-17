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
from Output.cpp.CPPOutputFile import *
from Utils import *
import codecs
import subprocess

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
		self.bpRoot = fixPath(os.path.abspath(self.modDir + "../")) + "/"
		self.libsDir = fixPath(os.path.abspath(inpCompiler.modDir + "../libs/cpp/"))
		self.stringCounter = 0
		self.fileCounter = 0
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.customCompilerFlags = []
		self.funcImplCache = {}
		self.includes = []
		
		self.mainClass = CPPClass("")
		self.mainClassImpl = self.mainClass.requestImplementation([])
		
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile)
		
		if len(self.compiledFiles) == 0:
			self.mainFile = cppOut
		
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		
		# Import files
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		# This needs to be executed AFTER the imported files have been compiled
		# It'll make sure the files are called in the correct (recursive) order
		self.compiledFilesList.append(cppOut)
		
		# After the dependencies have been compiled, compile itself
		cppOut.compile()
	
	def writeToFS(self, dirOut):
		dirOut = fixPath(os.path.abspath(dirOut)) + "/"
		self.outputDir = dirOut
		
		for cppFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(os.path.relpath(cppFile.file, self.projectDir)) + "-out.hpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				outStream.write(cppFile.getCode())
			
			# Write CPP main file (main-out.cpp)
			if cppFile.isMainFile:
				hppFile = os.path.basename(fileOut)
				
				fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + "-out.cpp"
				self.mainCppFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include <bp_decls.hpp>\n#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
		# Decls file
		fileOut = dirOut + "bp_decls.hpp"
		with open(fileOut, "w") as outStream:
			outStream.write("#ifndef " + "bp__decls__hpp" + "\n#define " + "bp__decls__hpp" + "\n\n")
			
			# Basic data types
			outStream.write("#include <cstdint>\n")
			outStream.write("#include <cstdlib>\n")
			for dataType, definition in dataTypeDefinitions.items():
				outStream.write("typedef %s %s;\n" % (definition, dataType))
			outStream.write("typedef %s %s;\n" % ("CString", "String"))
			outStream.write("#define %s %s\n" % ("Ptr", "boost::shared_ptr"))
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
	
	def build(self):
		exe = stripExt(self.mainCppFile)
		if os.path.isfile(exe):
			os.unlink(exe)
		
		compilerName = "g++"
		
		# Compiler
		ccCmd = [
			compilerName,
			"-c",
			self.mainCppFile,
			"-o%s" % (exe + ".o"),
			"-I" + self.outputDir,
			"-I" + self.modDir,
			"-I" + self.bpRoot + "include/cpp/",
			#"-L" + self.libsDir,
			"-std=c++0x",
			"-pipe",
			"-Wall",
			#"-frerun-cse-after-loop",
			#"-frerun-loop-opt",
			#"-ffast-math",
			#"-O3"
		]
		
		# Linker
		linkCmd = [
			compilerName,
			"-o%s" % (exe),
			exe + ".o",
			"-L" + self.libsDir,
			#"-ltheron",
			#"-lboost_thread",
			#"-lpthread"
		] + self.customCompilerFlags
		
		try:
			print("\nStarting compiler:")
			print(" \\\n ".join(ccCmd))
			
			procCompile = subprocess.Popen(ccCmd)
			procCompile.wait()
			
			print("\nStarting linker:")
			print("\n ".join(linkCmd))
			
			procLink = subprocess.Popen(linkCmd)
			procLink.wait()
		except OSError:
			print("Couldn't start g++")
		
		return exe
	
	def execute(self, exe):
		cmd = [exe]
		
		try:
			proc = subprocess.Popen(cmd)
			proc.wait()
		except OSError:
			print("Build process failed")
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.compiledFilesList:
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"
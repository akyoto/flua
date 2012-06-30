####################################################################
# Header
####################################################################
# Target:   Python 3 Code
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
from flua.Compiler.Output.BaseOutputCompiler import *
from flua.Compiler.Output.python.PythonClass import *
from flua.Compiler.Output.python.PythonOutputFile import *
import shutil

####################################################################
# Classes
####################################################################
class PythonOutputCompiler(BaseOutputCompiler):
	
	def __init__(self, inpCompiler, background = False, guiCallBack = None):
		super().__init__(inpCompiler, background, guiCallBack)
		
	def createOutputFile(self, inpFile):
		return PythonOutputFile(self, inpFile.getFilePath(), inpFile.getRoot())
		
	def createClass(self, name, node):
		return PythonClass(name, node)
		
	def writeToFS(self):
		cppFiles = self.compiledFiles.values()
		projectLocation = self.projectDir + self.getTargetName()
		includePostfix = "Include"
		
		# Write to files
		for cppFile in cppFiles:
			relPath = normalizeModName(stripExt(cppFile.file)[len(self.modDir):])
			fileOut = projectLocation + "/" + relPath + ".py"
			
			# Build all the stupid __init__.py files
			parts = relPath.split("/")
			initLocation = projectLocation + "/"
			for part in parts:
				initLocation += part + "/"
				if os.path.isdir(initLocation):
					with codecs.open(initLocation + "__init__.py", "w", encoding="utf-8") as initOutStream:
						initOutStream.write("\n")
						#initOutStream.flush()
						#initOutStream.close()
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			#print(fileOut)
			with codecs.open(fileOut, "w", encoding="utf-8") as outStream:
				outStream.write(cppFile.getCode())
			
			# Write Python main file
			if cppFile.isMainFile:
				hppFile = normalizeModPath(stripExt(cppFile.file)[len(self.modDir):])
				
				relPath = normalizeModName(stripAll(cppFile.file))
				fileOut = projectLocation + "/" + relPath + "_main.py"
				self.mainCppFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("""
import flua.decls
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import """ + hppFile + "\n" + self.getFileExecList() + "\n")
		
		# Decls file
		self.outputDir = extractDir(os.path.abspath(self.mainCppFile))
		fileOut = self.outputDir + "flua_decls.py"
		with open(fileOut, "w") as outStream:
			#outStream.write("print('Decls')\n")
			
			outStream.write("import ctypes\n")
			
			# Includes
			for incl, ifndef in self.includes:
				importPath = normalizeModPath(stripExt(incl)) + includePostfix
				
				copyFromPath = getModuleDir() + incl
				copyToPath = self.outputDir + stripExt(incl) + includePostfix + ".py"
				
				#shutil.copy2(copyFromPath, copyToPath)
				with open(copyToPath, "w") as copyToStream:
					with open(copyFromPath, "r") as copyFromStream:
						copyToStream.write(copyFromStream.read())
						copyToStream.flush()
						copyToStream.close()
				
				outStream.write("from %s import *\n" % (importPath))
			
			# Noop
			outStream.write("def flua_noop(): pass\n")
		
	def getExePath(self):
		return self.mainCppFile
		
	def build(self, compilerFlags = [], fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		return 0
		
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write, thread = None):
		pythonInterpreter = getPython3Path() + getPython3CompilerName()
		#print("Using %s" % pythonInterpreter)
		cmd = [pythonInterpreter, exe]
		
		try:
			return startProcess(cmd, fhOut, fhErr)
		except OSError:
			print("Can't execute '%s'" % exe)
		
	def getFileExecList(self):
		files = []
		#for cppFile in self.getCompiledFilesList():
		#	files.append("exec_" + cppFile.id + "()\n")
		return ''.join(files)
		
	def getTargetName(self):
		return "Python3"

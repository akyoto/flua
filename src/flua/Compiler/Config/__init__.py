from flua.Compiler.Utils import *

# Configuration
buildAndExecute = 1
buildGraphViz = 0
configScriptPath = extractDir(os.path.realpath(__file__))

def getMinGWDirs():
	if os.name == "nt":
		mp = fixPath(os.path.abspath(configScriptPath + "../../../../../mingw/"))
		return "%sbin/;%sinclude/;%slib/" % (mp, mp, mp)
	else:
		return ""

def getDLLDir():
	# TODO: 64 bit
	if os.name == "nt":
		return fixPath(os.path.abspath(configScriptPath + "../../../../libs/cpp/windows/x86/DLLs"))
	else:
		return fixPath(os.path.abspath(configScriptPath + "../../../../libs/cpp/linux/x86/DLLs"))

def getModuleDir():
	return fixPath(os.path.abspath(configScriptPath + "../../../"))
	#return extractDir(os.path.abspath("../../"))

def getGCCCompilerPath():
	if os.name == "nt":
		return fixPath(os.path.abspath(configScriptPath + "../../../../../mingw/bin/"))
	else:
		# Linux
		#if os.path.exists("/usr/bin/g++"):
		#	return "/usr/bin/"
		#else:
		return ""
	
def getGCCCompilerName():
	if os.name == "nt":
		# Windows
		return "g++"
	else:
		# Linux
		if os.path.exists("/usr/bin/g++-4.7"):
			return "g++-4.7"
		else:
			return "g++"
	
def getGCCCompilerVersion():
	# TODO: ...
	return ""
	
def getPython3Path():
	if os.name == "nt":
		return fixPath(os.path.abspath(configScriptPath + "../../../../../python/"))
	else:
		return ""
	
def getPython3CompilerName():
	if os.name == "nt":
		return "python.exe"
	else:
		return "python3"
	
def isCore(path):
	return path == getModuleDir() + "flua/Core/Core.flua"
	
def isPartOfCore(path):
	return getModuleDir() + "flua/Core/" in path
	
def getModulePath(importedModule, fileDir = "", projectDir = "", extension = ".flua"):
	# ########################### #
	# Priority for module search: #
	# ########################### # ############# #
	# 1. Local    # 4. Project    # 7. Global     #
	# ########################### ############### #
	# 2. File     # 5.  File      # 8.  File      #
	# 3. Dir      # 6.  Dir       # 9.  Dir       #
	# ########################### # ############# #
	fileDir = fixPath(fileDir)
	projectDir = fixPath(projectDir)
	
	importedModulePath = importedModule.replace(".", OS_SLASH)
	
	# Local
	importedFile = fileDir + importedModulePath + extension
	
	importedInFolder = fileDir + importedModulePath
	importedInFolder += OS_SLASH + stripAll(importedInFolder) + extension
	
	# Project
	pImportedFile = projectDir + importedModulePath + extension
	
	pImportedInFolder = projectDir + importedModulePath
	pImportedInFolder += OS_SLASH + stripAll(pImportedInFolder) + extension
	
	# Global
	gImportedFile = getModuleDir() + importedModulePath + extension
	
	gImportedInFolder = getModuleDir() + importedModulePath
	# TODO: pImportedInFolder?!
	gImportedInFolder += OS_SLASH + stripAll(gImportedInFolder) + extension
	
	# Debug
	#print(importedFile, "\n", importedInFolder, "\n", pImportedFile, "\n", pImportedInFolder, "\n", gImportedFile, "\n", gImportedInFolder, "\n")
	
	# TODO: Implement global variant
	
	if os.path.isfile(importedFile):
		return fixPath(os.path.abspath(importedFile))
	elif os.path.isfile(importedInFolder):
		return fixPath(os.path.abspath(importedInFolder))
	elif os.path.isfile(pImportedFile):
		return fixPath(os.path.abspath(pImportedFile))
	elif os.path.isfile(pImportedInFolder):
		return fixPath(os.path.abspath(pImportedInFolder))
	elif os.path.isfile(gImportedFile):
		return fixPath(os.path.abspath(gImportedFile))
	elif os.path.isfile(gImportedInFolder):
		return fixPath(os.path.abspath(gImportedInFolder))
	
	return ""
	#raise CompilerException("Module not found: „%s“" % importedModule)

def getModuleImportType(importedModule, fileDir, projectDir, extension = ".flua"):
	fileDir = fixPath(fileDir)
	projectDir = fixPath(projectDir)
	
	importedModulePath = importedModule.replace(".", OS_SLASH)
	
	# Local
	importedFile = fileDir + importedModulePath + extension
	
	importedInFolder = fileDir + importedModulePath
	importedInFolder += OS_SLASH + stripAll(importedInFolder) + extension
	
	# Project
	pImportedFile = projectDir + importedModulePath + extension
	
	pImportedInFolder = projectDir + importedModulePath
	pImportedInFolder += OS_SLASH + stripAll(pImportedInFolder) + extension
	
	# Global
	gImportedFile = getModuleDir() + importedModulePath + extension
	
	gImportedInFolder = getModuleDir() + importedModulePath
	# TODO: pImportedInFolder?!
	gImportedInFolder += OS_SLASH + stripAll(gImportedInFolder) + extension
	
	if os.path.isfile(importedFile):
		return 1
	elif os.path.isfile(importedInFolder):
		return 2
	elif os.path.isfile(pImportedFile):
		return 3
	elif os.path.isfile(pImportedInFolder):
		return 4
	elif os.path.isfile(gImportedFile):
		return 5
	elif os.path.isfile(gImportedInFolder):
		return 6
		
	return 0

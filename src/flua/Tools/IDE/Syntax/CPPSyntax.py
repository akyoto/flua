from PyQt4 import QtGui, QtCore
from flua.Tools.IDE import *
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Compiler.Input.bpc import *
from flua.Compiler.Output import *

class CPPHighlighter(QtGui.QSyntaxHighlighter, Benchmarkable):
	"""Syntax highlighter for the C++ language.
	"""
	# C++ keywords
	keywords = [{}] * 97 + [
		{'and', 'assert'},
		{'break'},
		{'class', 'continue', 'const', 'case', 'catch'},
		{'default', 'delete'},
		{'elif', 'else', 'ensure', 'extern', 'extends'},
		{'for', 'false', },
		{'get'},
		{},
		{'if', 'inline', 'include'},
		{},
		{},
		{'long'},
		{},
		{'not', 'namespace', 'new'},
		{'or', 'operator'},
		{'private', 'public'},
		{},
		{'return'},
		{'sizeof', 'switch', 'struct'},
		{'try', 'typename', 'typedef', 'template', 'throw', 'true'},
		{'until', 'unsigned'},
		{'virtual', 'volatile'},
		{'while'},
		{},
		{},
		{},
		{},
	] + [{}] * (256 - 97 - 26)
	
	# Keyword list
	keywordList = {
		'and', 'assert',
		'break', 'bool',
		'class', 'continue', 'const', 'char', 'case', 'catch',
		'double', 'default', 'delete',
		'elif', 'else', 'ensure', 'extern', 'extends',
		'for', 'false', 'float',
		'get',
		'if', 'inline', 'include', 'int',
		'long',
		'not', 'null', 'namespace', 'new',
		'or', 'operator',
		'private', 'public',
		'return',
		'sizeof', 'switch', 'struct',
		'try', 'typename', 'typedef', 'template', 'throw', 'true',
		'until', 'unsigned',
		'void', 'virtual', 'volatile',
		'while',
	}
	
	# BPC operators
	operators = {
		'=',
		# Comparison
		'==', '!=', '<', '<=', '>', '>=',
		# Arithmetic
		'\+', '-', '\*', '/', '//', '\%', '\*\*',
		# In-place
		'\+=', '-=', '\*=', '/=', '\%=',
		# Bitwise
		'\^', '\|', '\&', '\~', '>>', '<<',
		# Data Flow
		'<-', '->', '<--', '-->',
		# Type declaration
		':',
	}

	# BPC braces
	braces = {
		'(', ')', '[', ']', '{', '}',
	}
	
	cDataTypes = {
		# C
		'char', 'bool', 'void', 'int', 'float', 'double', 'short',
		
		# GLSL
		'vec2', 'vec3', 'vec4',
		'bvec2', 'bvec3', 'bvec4',
		'ivec2', 'ivec3', 'ivec4',
		'mat2', 'mat3', 'mat4',
		'sampler1D', 'sampler2D', 'sampler3D', 'samplerCube',
		'sampler1DShadow', 'sampler2DShadow',
	}
	
	cFuncs = {
		"isalnum",
		"isalpha",
		"iscntrl",
		"isdigit",
		"isgraph",
		"islower",
		"isprint",
		"ispunct",
		"isspace",
		"isupper",
		"isxdigit",
		"toupper",
		"tolower",
		"errno",
		"setlocale",
		"acos",
		"asin",
		"atan",
		"atan2",
		"ceil",
		"cos",
		"cosh",
		"exp",
		"fabs",
		"floor",
		"fmod",
		"frexp",
		"ldexp",
		"log",
		"log10",
		"modf",
		"pow",
		"sin",
		"sinh",
		"sqrt",
		"tan",
		"tanh",
		"setjmp",
		"longjmp",
		"signal",
		"raise",
		"va_start",
		"va_arg",
		"va_end",
		"clearerr",
		"fclose",
		"feof",
		"fflush",
		"fgetc",
		"fgetpos",
		"fgets",
		"fopen",
		"fprintf",
		"fputc",
		"fputs",
		"fread",
		"freopen",
		"fscanf",
		"fseek",
		"fsetpos",
		"ftell",
		"fwrite",
		"getc",
		"getchar",
		"gets",
		"perror",
		"printf",
		"putchar",
		"puts",
		"remove",
		"rewind",
		"scanf",
		"setbuf",
		"setvbuf",
		"sprintf",
		"sscanf",
		"tmpfile",
		"tmpnam",
		"ungetc",
		"vfprintf",
		"vprintf",
		"vsprintf",
		"abort",
		"abs",
		"atexit",
		"atof",
		"atoi",
		"atol",
		"bsearch",
		"calloc",
		"div",
		"exit",
		"getenv",
		"free",
		"labs",
		"ldiv",
		"malloc",
		"mblen",
		"mbstowcs",
		"mbtowc",
		"qsort",
		"rand",
		"realloc",
		"strtod",
		"strtol",
		"strtoul",
		"srand",
		"system",
		"wctomb",
		"wcstombs",
		"memchr",
		"memcmp",
		"memcpy",
		"memmove",
		"memset",
		"strcat",
		"strchr",
		"strcmp",
		"strcoll",
		"strcpy",
		"strcspn",
		"strerror",
		"strlen",
		"strncat",
		"strncmp",
		"strncpy",
		"strpbrk",
		"strrchr",
		"strspn",
		"strstr",
		"strtok",
		"strxfrm",
		"asctime",
		"clock",
		"ctime",
		"difftime",
		"gmtime",
		"localtime",
		"mktime",
		"strftime",
		"time",
		"opendir",
		"closedir",
		"readdir",
		"rewinddir",
		"scandir",
		"seekdir",
		"telldir",
		"access",
		"alarm",
		"chdir",
		"chown",
		"close",
		"chroot",
		"ctermid",
		"cuserid",
		"dup",
		"dup2",
		"execl",
		"execle",
		"execlp",
		"execv",
		"execve",
		"execvp",
		"fchdir",
		"fork",
		"fpathconf",
		"getegid",
		"geteuid",
		"gethostname",
		"getop",
		"getgid",
		"getgroups",
		"getlogin",
		"getpgrp",
		"getpid",
		"getppi",
		"getuid",
		"isatty",
		"link",
		"lseek",
		"mkdir",
		"open",
		"pathconf",
		"pause",
		"pipe",
		"read",
		"rename",
		"rmdir",
		"setgid",
		"setpgid",
		"setsid",
		"setuid",
		"sleep",
		"sysconf",
		"tcgetpgrp",
		"tcsetpgrp",
		"ttyname",
		"unlink",
		"write",
		"clrscr",
		"getch",
		"getche",
		"direnth",
		"statfs",
		"unistdh",
		"endpwent",
		"fgetpwent",
		"getpw",
		"getpwent",
		"getpwnam",
		"getpwuid",
		"getuidx",
		"index",
		"putpwent",
		"pclose",
		"popen",
		"putenv",
		"setenv",
		"setpwent",
		"setreuid",
		"stat",
		"uname",
		"unsetenv",
		"setuidx",
		"setegid",
		"setrgid",
		"seteuid",
		"setruid",
		"getruid",
		"sizeof",
		"clrscr",
		"convesc",
		"basename",
		"printenv",
		"lenstr",
		"reverse",
	}
	
	glslQualifiers = {
		# GLSL
		'in', 'out', 'inout',
		
		'attribute', 'uniform', 'varying',
	}
	
	def __init__(self, document, bpIDE):
		QtGui.QSyntaxHighlighter.__init__(self, document)
		Benchmarkable.__init__(self)
		
		self.bpIDE = bpIDE
		#self.updateCharFormatFlag = False
	
	def highlightBlock(self, text):
		"""Apply syntax highlighting to the given block of text.
		"""
		bpIDE = self.bpIDE
		if not text:
			return
		
		style = bpIDE.getCurrentTheme()
		
		if bpIDE.outputCompiler:
			externFuncs = bpIDE.outputCompiler.mainClass.externFunctions
		else:
			externFuncs = {}
		
		i = 0
		text += " "
		textLen = len(text)
		userData = None
		
		#print("HIGHLIGHTING >%s< OF LENGTH %d" % (text, textLen))
		#if self.updateCharFormatFlag:
		#	self.setFormat(0, textLen, style['default'])
		
		while i < textLen:
			char = text[i]
			if char.isalpha() or char == '_' or char == '~':
				h = i + 1
				while h < textLen and (text[h].isalnum() or text[h] == '_'): #or (char =='~' and (text[h] == '<' or text[h] == '>'))):
					h += 1
				expr = text[i:h]
				print(expr)
				# No highlighting for unicode
				ascii = ord(char)
				if ascii > 255:
					i = h
					continue
				
				if expr in (CPPHighlighter.keywords[ascii]):
					self.setFormat(i, h - i, style['keyword'])
				elif expr in CPPHighlighter.cFuncs:
					self.setFormat(i, h - i, style['c-function'])
				elif expr in externFuncs:
					# Extern function call
					
					# Temporary hack
					if not expr in bpIDE.processor.externFuncNameToMetaDict:
						pos = expr.find("_")
						if pos != -1:
							expr = expr[pos+1:]
					
					if expr in bpIDE.processor.externFuncNameToMetaDict:
						meta = bpIDE.processor.externFuncNameToMetaDict[expr]
						
						sideEffects = not ("no-side-effects" in meta and meta["no-side-effects"] == "true")
						sameOutput = ("same-output-for-input" in meta and meta["same-output-for-input"] == "true")
						
						if sameOutput and not sideEffects:
							self.setFormat(i, h - i, style['ref-transparent-extern-function'])
						elif sideEffects:
							self.setFormat(i, h - i, style['side-effects-extern-function'])
						else:
							self.setFormat(i, h - i, style['no-side-effects-extern-function'])
					else:
						meta = None
						self.setFormat(i, h - i, style['default'])
					
					i = h
					continue
				elif expr == "this":
					self.setFormat(i, h - i, style['self'])
					i = h
					continue
				elif expr in CPPHighlighter.cDataTypes or expr in nonPointerClasses or expr.startswith("GL") or expr.endswith("_t"):
					# Quick hack
					self.setFormat(i, h - i, style['c-datatypes'])
					i = h
					continue
				elif expr in CPPHighlighter.glslQualifiers:
					self.setFormat(i, h - i, style['keyword'])
					i = h
					continue
				elif expr == "main":
					# Quick hack
					self.setFormat(i, h - i, style['c-main'])
					i = h
					continue
				elif bpIDE.processor.getFirstDTreeByFunctionName(expr):
					self.setFormat(i, h - i, style['function'])
					i = h
					continue
				
				i = h - 1
			elif char.isdigit():
				h = i + 1
				while h < textLen and text[h].isdigit():
					h += 1
				if (i == 0 or not text[i - 1].isalpha()) and not text[h].isalpha():
					self.setFormat(i, h - i, style['number'])
				elif text[i] == '0' and text[h] == 'x':
					h += 1
					while h < textLen and (text[h].isdigit() or text[h] in "ABCDEFabcdef"):
						h += 1
					self.setFormat(i, h - i, style['hex-number'])
				#else:
				#	
				i = h - 1
			elif char == '"':
				h = i + 1
				while h < textLen and text[h] != '"':
					h += 1
				
				# TODO: WHY IS THIS CALL SO BUGGY ON WINDOWS?!
				if h < textLen - 1 and text[h] == '"':
					self.setFormat(i, h - i + 1, style['string'])
				
				#print(i, h - i, style['string'])
				#if h < textLen - 1:
				#	if text[h] == '"':
				#		self.setFormat(i, h - i + 1, style['string'])
				#	else:
				#		self.setFormat(i, h - i, style['string'])
				#else:
				i = h
			elif char == '/' and text[i + 1] == '/':
				if i < textLen - 1 and text[i + 2].isspace():
					self.setFormat(i, textLen - i, style['comment'])
				else:
					self.setFormat(i, textLen - i, style['disabled'])
				return
			elif char == '#':
				self.setFormat(i, textLen - i, style['preprocessor'])
				return
			elif char == ',':
				self.setFormat(i, 1, style['comma'])
			elif char in '+-*/=<>%&|:!\\~':
				#h = i + 1
				#while h < textLen and text[h]:
				#	h += 1
				self.setFormat(i, 1, style['operator'])
				#i = h
			elif char in CPPHighlighter.braces:
				self.setFormat(i, 1, style['brace'])
				
			i += 1
		#self.endBenchmark()
		
		#self.setCurrentBlockState(0)


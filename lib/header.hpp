#ifndef HEADER_HPP_
#define HEADER_HPP_

//C++
#ifndef __cplusplus
	#error You need a C++ compiler.
#endif

//OS
#ifdef _WIN32
	#ifndef WIN32
		#define WIN32
	#endif
	#ifndef WIN32_LEAN_AND_MEAN
		#define WIN32_LEAN_AND_MEAN
	#endif
#elif linux || __linux__ || LINUX
	#ifndef LINUX
		#define LINUX
	#endif
#elif __APPLE__ || macintosh || Macintosh
	#ifndef MACOS
		#define MACOS 1
	#endif
#else
	#error Unknown operating system.
#endif

//Compiler
#ifdef __GNUC__
	#ifndef GCC
		#define GCC
	#endif
#elif _MSC_VER
	#ifndef MSVC
		#define MSVC
	#endif
#elif __INTEL_COMPILER
	#ifndef INTELC
		#define INTELC
	#endif
#else
	#error Unknown compiler.
#endif

//Architecture
#if i386 || _M_IX86
	#ifndef X86
		#define X86
	#endif
#elif __x86_64__ || _M_X64
	#ifndef X86_64
		#define X86_64
	#endif
#else
	#error Unknown architecture.
#endif

//Unicode
#if _UNICODE || UNICODE
	#ifndef UNICODE
		#define UNICODE
	#endif
#else
	#ifndef ASCII
		#define ASCII
	#endif
#endif

//OS compatibility
#ifndef WIN32
	typedef unsigned long DWORD;
#endif

//Debug mode
#ifdef _DEBUG
	#ifndef DEBUG
		#define DEBUG
	#endif
#endif

#endif /*HEADER_HPP_*/

////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Core
// Author:				Eduard Urbach
// Description:			Core functions
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_CORE_HPP_
#define BLITZPROG_CORE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/String/String.hpp>

//C++
#include <cstdlib>

//Boost
#include <boost/shared_ptr.hpp>
#include <boost/weak_ptr.hpp>

//Namespaces
using namespace std;

//Others
#ifdef WIN32
	#include "Core.Win32.hpp"
#elif defined(LINUX)
	#include "Core.Linux.hpp"
#elif defined(MACOS)
	#include "Core.MacOS.hpp"
#endif

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//SharedPtr
template <typename T>
class SharedPtr: public boost::shared_ptr<T>
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		SharedPtr() : boost::shared_ptr<T>()
		{
			
		}
		
		//Constructor
		SharedPtr(T *ptr) : boost::shared_ptr<T>(ptr)
		{
			
		}
		
		//Constructor
		SharedPtr(T &obj) : boost::shared_ptr<T>(&obj)
		{
			
		}
		
		//Constructor
		template <typename X>
		SharedPtr(SharedPtr<X> sp) : boost::shared_ptr<T>(sp)
		{
			
		}
		
		//Constructor
		template <typename X>
		SharedPtr(const SharedPtr<X> &sp) : boost::shared_ptr<T>(sp)
		{
			
		}
		
		//Constructor
		template <typename X>
		SharedPtr(const boost::shared_ptr<X> &sp) : boost::shared_ptr<T>(sp)
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator: bool
		inline operator bool() const
		{
			return this->get() != Null;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: T*
		inline operator T*() const
		{
			return this->get();
		}
		
		//Cast: T&
		inline operator T&() const
		{
			return *this->get();
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//GetReferenceCount
		inline long GetReferenceCount() const
		{
			return this->use_count();
		}
		
		//GetCPointer
		inline T *GetCPointer() const
		{
			return this->get();
		}
		
};

//WeakPtr
template <typename T>
class WeakPtr: public boost::weak_ptr<T>
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		WeakPtr() : boost::weak_ptr<T>()
		{
			
		}
		
		//Constructor
		WeakPtr(T *ptr) : boost::weak_ptr<T>(boost::shared_ptr<T>(ptr))
		{
			
		}
		
		//Constructor
		template <typename X>
		WeakPtr(const SharedPtr<X> &ptr) : boost::weak_ptr<T>(ptr)
		{
			
		}
		
		//Constructor
		template <typename X>
		WeakPtr(const WeakPtr<X> &sp) : boost::weak_ptr<T>(sp)
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator: bool
		inline operator bool() const
		{
			return this->lock().get() != Null;
		}
		
		//Operator: ->
		inline SharedPtr<T> operator ->() const
		{
			return this->lock();
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: SharedPtr
		inline operator SharedPtr<T>() const
		{
			return this->lock();
		}
		
		//Cast: T*
		inline operator T*() const
		{
			return this->lock().get();
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		
		
};

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Print
#define WriteToCPPStream(xCPPStream, msg) xCPPStream << msg
#define Print(msg) WriteToCPPStream(std::cout, msg << std::endl)
#define WriteStdout(msg) WriteToCPPStream(std::cout, msg << std::flush)

//Byte
typedef unsigned char byte;

//Repeat
#define repeat(xTimes) for(int REPEAT_ITERATOR=1; REPEAT_ITERATOR <= xTimes; ++REPEAT_ITERATOR)

//PROCEDURE
//#define PROCEDURE function0<void>
#define CPROCEDURE(funcName) void(*funcName)()

//CPP_TO_STRING
#define CPP_TO_STRING(x) #x

//foreach
//TODO: Check this
#define foreach(iter, stlContainerPtr) \
		typedef __typeof__(*stlContainerPtr) stlContainerPtrContainerType;\
		stlContainerPtrContainerType::value_type iter;\
		if(stlContainerPtr->begin() != stlContainerPtr->end())\
			iter = *stlContainerPtr->begin();\
		for(stlContainerPtrContainerType::iterator iterSTL = stlContainerPtr->begin(); iterSTL != stlContainerPtr->end(); iter = *(++iterSTL))

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////

static int bpRuntimeStart = MilliSecs();
static int bpAppArgsCount = 0;
static char **bpAppArgs = Null;

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//Main: User must define this
void Main();

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//InitBlitzprog
inline void InitBlitzprog(int argc, char *argv[])
{
	bpAppArgsCount = argc;
	bpAppArgs = argv;
}

//GetRunTime
inline int GetRunTime()
{
	return MilliSecs() - bpRuntimeStart;
}

//SetEnv
inline void SetEnv(const String &varName, const String &value)
{
	putenv(varName + "=" + value);
}

//GetEnv
inline String GetEnv(const String &varName)
{
	return getenv(varName);
}

//AppFile
inline String AppFile()
{
	return bpAppArgs[0];
}

//AppDir
inline String AppDir()
{
	return ExtractDir(bpAppArgs[0]);
}

//AppFileName
inline String AppFileName()
{
	return ExtractName(bpAppArgs[0]);
}

//GetCAppArgs
inline char **&GetCAppArgs()
{
	return bpAppArgs;
}

//GetCAppArgsCount
inline int &GetCAppArgsCount()
{
	return bpAppArgsCount;
}

//CommandLine
inline String CommandLine()
{
	static String commandLine = bpAppArgsCount > 1 ? Implode(bpAppArgs+1, bpAppArgsCount-1, " ") : "";
	return commandLine;
}

//End
inline void End(int exitCode = EXIT_SUCCESS)
{
	//Debug info
	EngineLog5("End of program");
	
	throw exitCode;
}

//Abort
inline void Abort(int exitCode = EXIT_FAILURE)
{
	//Debug info
	EngineLog4("End of program (runtime error)");
	
	throw exitCode;
}

//OnEnd
inline bool OnEnd(CPROCEDURE(function))
{
	return !atexit(function);
}

//MemCopy
template <typename T1, typename T2>
inline void MemCopy(const T1* source, T2* destination, size_t num)
{
	memcpy(destination, source, num);
}

//MemSet
template <typename T1, typename T2>
inline void MemSet(T1* destination, T2 value, size_t num)
{
	memset(destination, value, num);
}

//Operator << (ostream, SharedPtr)
template <typename T>
inline std::ostream &operator<<(std::ostream &stream, const SharedPtr<T> &data)
{
	return stream << data->ToString();
}

//Operator << (ostream, SharedPtr<int>)
inline std::ostream &operator<<(std::ostream &stream, const SharedPtr<int> &data)
{
	return stream << (data.GetCPointer() ? *data.GetCPointer() : 0);
}

//Operator << (ostream, SharedPtr<float>)
inline std::ostream &operator<<(std::ostream &stream, const SharedPtr<float> &data)
{
	return stream << (data.GetCPointer() ? *data.GetCPointer() : 0.0f);
}

//main
#ifndef BLITZPROG_LIB
	int main(int argc, char *argv[])
	{
		try
		{
			InitBlitzprog(argc, argv);
			Main();
		}
		catch(int exitCode)
		{
			return exitCode;
		}
		catch(...)
		{
			return EXIT_FAILURE;
		}
	}
#endif

#endif /*BLITZPROG_CORE_HPP_*/

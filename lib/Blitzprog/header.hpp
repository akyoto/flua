#ifndef BLITZPROG_HEADER_HPP_
#define BLITZPROG_HEADER_HPP_

//Includes
#include <header.hpp>

//Debug mode
#define LOG_TO_FILE

#ifdef DEBUG
	#define DEBUG_LEVEL 4
	
	#ifdef LOG_TO_FILE
		#include <fstream>
		#define DEBUG_LOG_FILE "engine-log.html"
		static std::ofstream elog(DEBUG_LOG_FILE, std::ios::out);
		#define LOG_FUNC(msg) { elog << msg << "<br />" << std::endl; }
		#define LOG_FUNC_ERROR(msg) LOG_FUNC("<span style='color: red;'>" << msg << "</span>")
	#else
		#define LOG_FUNC(msg) std::cout << msg << std::endl
		#define LOG_FUNC_ERROR(msg) std::cerr << "[" << __FUNCTION__ << "] " << msg << std::endl
	#endif
#else
	#define DEBUG_LEVEL 0
#endif

//Enable/disable log macros
#if DEBUG_LEVEL == 0
	#define EngineLog(msg) //std::cout << msg << std::endl //
	#define EngineLog2(msg) //EngineLog(msg) //
	#define EngineLog3(msg) //EngineLog(msg) //
	#define EngineLog4(msg) //EngineLog(msg) //
	#define EngineLog5(msg) //EngineLog(msg) //
	#define EngineLogNew(msg) //EngineLog("New " << msg) //
	#define EngineLogDelete(msg) //EngineLog("Delete " << msg) //
	#define EngineLogError(msg) //EngineLog("Error: " << msg) //
#elif DEBUG_LEVEL == 1
	#define EngineLog(msg) LOG_FUNC(msg) //
	#define EngineLog2(msg) //EngineLog(msg) //
	#define EngineLog3(msg) //EngineLog(msg) //
	#define EngineLog4(msg) //EngineLog(msg) //
	#define EngineLog5(msg) //EngineLog(msg) //
	#define EngineLogNew(msg) EngineLog("New " << msg) //
	#define EngineLogDelete(msg) EngineLog("Delete " << msg) //
	#define EngineLogError(msg) LOG_FUNC_ERROR("Error: " << msg) //
#elif DEBUG_LEVEL == 2
	#define EngineLog(msg) LOG_FUNC(msg) //
	#define EngineLog2(msg) EngineLog(msg) //
	#define EngineLog3(msg) //EngineLog(msg) //
	#define EngineLog4(msg) //EngineLog(msg) //
	#define EngineLog5(msg) //EngineLog(msg) //
	#define EngineLogNew(msg) EngineLog("New " << msg) //
	#define EngineLogDelete(msg) EngineLog("Delete " << msg) //
	#define EngineLogError(msg) LOG_FUNC_ERROR("Error: " << msg) //
#elif DEBUG_LEVEL == 3
	#define EngineLog(msg) LOG_FUNC(msg) //
	#define EngineLog2(msg) EngineLog(msg) //
	#define EngineLog3(msg) EngineLog(msg) //
	#define EngineLog4(msg) //EngineLog(msg) //
	#define EngineLog5(msg) //EngineLog(msg) //
	#define EngineLogNew(msg) EngineLog("New " << msg) //
	#define EngineLogDelete(msg) EngineLog("Delete " << msg) //
	#define EngineLogError(msg) LOG_FUNC_ERROR("Error: " << msg) //
#elif DEBUG_LEVEL == 4
	#define EngineLog(msg) LOG_FUNC(msg) //
	#define EngineLog2(msg) EngineLog(msg) //
	#define EngineLog3(msg) EngineLog(msg) //
	#define EngineLog4(msg) EngineLog(msg) //
	#define EngineLog5(msg) //EngineLog(msg) //
	#define EngineLogNew(msg) EngineLog("New " << msg) //
	#define EngineLogDelete(msg) EngineLog("Delete " << msg) //
	#define EngineLogError(msg) LOG_FUNC_ERROR("Error: " << msg) //
#elif DEBUG_LEVEL == 5
	#define EngineLog(msg) LOG_FUNC(msg) //
	#define EngineLog2(msg) EngineLog(msg) //
	#define EngineLog3(msg) EngineLog(msg) //
	#define EngineLog4(msg) EngineLog(msg) //
	#define EngineLog5(msg) EngineLog(msg) //
	#define EngineLogNew(msg) EngineLog("New " << msg) //
	#define EngineLogDelete(msg) EngineLog("Delete " << msg) //
	#define EngineLogError(msg) LOG_FUNC_ERROR("Error: " << msg) //
#endif

//Null
#define nullptr NULL
#define Null nullptr

//int32
typedef int int32;	//TODO: ...

#endif /*BLITZPROG_HEADER_HPP_*/

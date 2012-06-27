#include <ctime>
#include <flua/Core/String/UTF8String/C++/UTF8String.hpp>

// Typedef
#define BPTimeStamp struct tm

// flua_getCurrentDate
inline BPTimeStamp* flua_now() {
	time_t locTime = time(NULL);
	return localtime(&locTime);
}

// flua_formatTimeStamp
inline BPUTF8String *flua_formatTimeStamp(BPTimeStamp* stamp, BPUTF8String* format) {
	char *buf = new (UseGC) char[32];
	strftime(buf, 32, format->_data, stamp);
	return new BPUTF8String(buf);
}
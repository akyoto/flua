#include <ctime>
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>

// Typedef
#define BPTimeStamp struct tm

// bp_getCurrentDate
inline BPTimeStamp* bp_now() {
	time_t locTime = time(NULL);
	return localtime(&locTime);
}

// bp_formatTimeStamp
inline BPUTF8String *bp_formatTimeStamp(BPTimeStamp* stamp, BPUTF8String* format) {
	char *buf = new (UseGC) char[32];
	strftime(buf, 32, format->_data, stamp);
	return new BPUTF8String(buf);
}
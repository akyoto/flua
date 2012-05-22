#include <ctime>
#include <bp/Core/String/C++/UTF8String.hpp>

// TODO: ...

// bp_getCurrentDate
inline BPUTF8String *bp_getCurrentDate() {
	time_t locTime = time(NULL);
	struct tm* tmLocTime;
	//localtime_r(&locTime, &tmLocTime);
	tmLocTime = localtime(&locTime);
	char *buf = new (UseGC) char[16];
	strftime(buf, 16, "%Y-%m-%d", tmLocTime);
	return new BPUTF8String(buf);
}

// bp_getCurrentTime
inline BPUTF8String *bp_getCurrentTime() {
	time_t locTime = time(NULL);
	struct tm* tmLocTime;
	//localtime_r(&locTime, &tmLocTime);
	tmLocTime = localtime(&locTime);
	char *buf = new (UseGC) char[16];
	strftime(buf, 16, "%H:%M:%S", tmLocTime);
	return new BPUTF8String(buf);
}

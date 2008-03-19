#include "Date.hpp"

//CurrentDate
String CurrentDate()
{
	time_t locTime = time(Null);
	struct tm tmLocTime;
	localtime_r(&locTime, &tmLocTime);
	char buf[16];
	strftime(buf, 16, "%d.%m.%Y", &tmLocTime);
	return buf;
}

//CurrentTime
String CurrentTime()
{
	time_t locTime = time(Null);
	struct tm tmLocTime;
	localtime_r(&locTime, &tmLocTime);
	char buf[16];
	strftime(buf, 16, "%H:%M:%S", &tmLocTime);
	return buf;
}

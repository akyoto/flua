// bp
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>

// input
inline BPUTF8String* bp_input() {
	std::string str;
	getline(std::cin, str);
	
	const char* c = str.c_str();
	size_t len = str.length();
	
	char* buf = new (UseGC) char[len];
	
	memcpy(buf, c, len);
	
	return _toString(buf);
}
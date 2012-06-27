#include <iostream>

// write_xchars
template <typename T>
inline void flua_writeXbytes(T* ptr, size_t num) {
	for(T* end = ptr + num; ptr != end;)
		std::cout << *ptr++;
}

template <typename T>
inline void flua_writeXbytesLine(T* ptr, size_t num) {
	for(T* end = ptr + num; ptr != end;)
		std::cout << *ptr++;
	std::cout << std::endl;
}

// writeLine
template <typename T>
inline void flua_writeLine(T var) {
	std::cout << var << std::endl;
}

template <>
inline void flua_writeLine(bool var) {
	static const char *a[2] = {"false", "true"};
	std::cout << a[var] << std::endl;
}

// flush
inline void flua_flush() {
	std::cout.flush();
}

// write
template <typename T>
inline void flua_write(T var) {
	std::cout << var;
}
#include <iostream>

// write
template <typename T>
inline void bp_write(T var) {
	std::cout << var;
}

// write_xchars
template <typename T>
inline void bp_write_xbytes(T* ptr, size_t num) {
	for(T* end = ptr + num; ptr != end;)
		std::cout << *ptr++;
}

// writeln
template <typename T>
inline void bp_writeln(T var) {
	std::cout << var << std::endl;
}

template <>
inline void bp_writeln(bool var) {
	static const char *a[2] = {"false", "true"};
	std::cout << a[var] << std::endl;
}

// flush
inline void bp_flush() {
	std::cout.flush();
}
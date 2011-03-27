#include <iostream>
#include <unistd.h>
#include <sys/time.h>

// Typedefs
typedef bool Bool;
typedef char Byte;
typedef short Short;
typedef int Int;
typedef float Float;
typedef double Double;

// Standard functions
template <typename T>
inline void bp_print(T var) {
	std::cout << var << std::endl;
}

template <typename T>
inline int bp_usleep(T ms) {
	return usleep(ms);
}

inline int bp_milliSecs() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000 + (ts.tv_usec / 1000);
}

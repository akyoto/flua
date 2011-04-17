#include <iostream>
#include <unistd.h>
#include <boost/shared_ptr.hpp>
#include <sys/time.h>

// Macros
#define bp_sizeOf sizeof

// Standard functions
template <typename T>
inline void bp_print(T var) {
	std::cout << var;
}

template <typename T>
inline Int bp_usleep(T ms) {
	return usleep(ms);
}

inline time_t bp_systemTime() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000 + (ts.tv_usec / 1000);
}

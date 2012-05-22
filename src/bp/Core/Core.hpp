#include <iostream>
#include <unistd.h>
#include <sys/time.h>

// Macros
#define bp_sizeOf sizeof

// Standard functions
inline void bp_gcCollect() {
	GC_gcollect();
}

template <typename T>
inline void bp_print(T var) {
	std::cout << var;
}

template <typename T>
inline void bp_println(T var) {
	std::cout << var << std::endl;
}

inline void bp_flush() {
	std::cout.flush();
}

template <>
inline void bp_println(bool var) {
	static const char *a[2] = {"false", "true"};
	std::cout << a[var] << std::endl;
}

// Standard functions
template <typename T1, typename T2>
inline void bp_swap(T1 &x, T2 &y) {
	T1 tmp(x);
	x = y;
	y = tmp;
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

/*inline clock_t bp_systemCPUClock() {
	return clock();
}*/

// operator << for BigInt
/*inline std::ostream &operator<<(std::ostream& stream, const mpz_class& matrix) {
	return stream;
}*/

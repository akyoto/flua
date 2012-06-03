#include <unistd.h>
#include <sys/time.h>

// Macros
#define bp_sizeOf sizeof

// gcCollect
inline void bp_gcCollect() {
	GC_gcollect();
}

template <typename T1, typename T2>
inline void bp_swap(T1 &x, T2 &y) {
	T1 tmp(x);
	x = y;
	y = tmp;
}

template <typename T>
inline Bool bp_usleep(T ms) {
	return usleep(ms) == 0;
}

inline time_t bp_systemTime() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000 + (ts.tv_usec / 1000);
}

inline time_t bp_systemTimeMicro() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000000 + ts.tv_usec;
}

/*inline clock_t bp_systemCPUClock() {
	return clock();
}*/

// operator << for BigInt
/*inline std::ostream &operator<<(std::ostream& stream, const mpz_class& matrix) {
	return stream;
}*/
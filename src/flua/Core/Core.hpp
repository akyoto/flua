#include <unistd.h>
#include <sys/time.h>
#include <cstdarg>

// Macros
#define BPFunction void
#define flua_sizeOf sizeof

// gcCollect
inline void flua_gcCollect() {
	GC_gcollect();
}

template <typename T1, typename T2>
inline void flua_swap(T1 &x, T2 &y) {
	T1 tmp(x);
	x = y;
	y = tmp;
}

template <typename T>
inline Bool flua_usleep(T ms) {
	return usleep(ms) == 0;
}

inline time_t flua_systemTime() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000 + (ts.tv_usec / 1000);
}

inline time_t flua_systemTimeMicro() {
	timeval ts;
	gettimeofday(&ts, NULL);
	
	return ts.tv_sec * 1000000 + ts.tv_usec;
}

inline void flua_exit(int status) {
	exit(status);
}

template <class CollType, typename ElemType, typename PromotedType>
inline CollType* flua_buildCollection(int count, ...) {
	va_list arguments;
	CollType* vec = new (UseGC) CollType(count);
	
	va_start(arguments, count);
	for(int i = 0; i < count; ++i)
		vec->add(static_cast<ElemType>(va_arg(arguments, PromotedType)));
	va_end(arguments);
	
	return vec;
}

// operator << for BigInt
/*inline std::ostream &operator<<(std::ostream& stream, const mpz_class& matrix) {
	return stream;
}*/
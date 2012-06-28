#include <cmath>

template <typename T>
inline bool flua_isNan(T x) {
	return isnan(x);
}

template <typename T>
inline bool flua_isInf(T x) {
	return isinf(x);
}

template <typename T>
inline double flua_sqrt(T num) {
	return sqrt(num);
}

template <typename T>
inline double flua_exp(T x) {
	return exp(x);
}

template <typename T>
inline double flua_floor(T x) {
	return floor(x);
}

template <typename T>
inline double flua_ceil(T x) {
	return ceil(x);
}

template <typename T>
inline double flua_log(T x) {
	return log(x);
}

template <typename T>
inline double flua_log10(T x) {
	return log10(x);
}

template <typename T1, typename T2>
inline int flua_rand(T1 a, T2 b) {
	if(a != b)
		return (b >= a) ? rand() % (b - a) + a : rand() % (a - b) + b;
	return a;
}

template <typename T>
inline void flua_setRandSeed(T x) {
	srand(x);
}

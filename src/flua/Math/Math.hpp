#include <cmath>

BP_WRAP_1(bool, flua_isNan, isnan)
BP_WRAP_1(bool, flua_isInf, isinf)
BP_WRAP_1(double, flua_sqrt, sqrt)
BP_WRAP_1(double, flua_exp, exp)
BP_WRAP_1(double, flua_floor, floor)
BP_WRAP_1(double, flua_ceil, ceil)
BP_WRAP_1(double, flua_log, log)
BP_WRAP_1(double, flua_log10, log10)

template <typename T1, typename T2>
inline int flua_rand(T1 a, T2 b) {
	if(a != b)
		return (b >= a) ? rand() % (b - a) + a : rand() % (a - b) + b;
	return a;
}

template <typename T1, typename T2>
inline float flua_randFloat(T1 a, T2 b) {
	return (b >= a) ? a + (float)rand() / ((float)RAND_MAX / (b - a)) : b + (float)rand() / ((float)RAND_MAX / (a - b));
}

template <typename T>
inline void flua_setRandSeed(T x) {
	srand(x);
}

#include <cmath>

template <typename T>
inline bool bp_isnan(T x) {
	return isnan(x);
}

template <typename T>
inline bool bp_isinf(T x) {
	return isinf(x);
}

template <typename T>
inline double bp_sqrt(T num) {
	return sqrt(num);
}

template <typename T>
inline double bp_exp(T x) {
	return exp(x);
}

template <typename T>
inline double bp_floor(T x) {
	return floor(x);
}

template <typename T>
inline double bp_ceil(T x) {
	return ceil(x);
}

template <typename T>
inline double bp_log(T x) {
	return log(x);
}

template <typename T>
inline double bp_log10(T x) {
	return log10(x);
}

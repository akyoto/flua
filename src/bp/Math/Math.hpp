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
inline double bp_sin(T radian) {
	return sin(radian);
}

template <typename T>
inline double bp_cos(T radian) {
	return cos(radian);
}

template <typename T>
inline double bp_tan(T radian) {
	return tan(radian);
}

template <typename T>
inline double bp_asin(T radian) {
	return asin(radian);
}

template <typename T>
inline double bp_acos(T radian) {
	return acos(radian);
}

template <typename T>
inline double bp_atan(T radian) {
	return atan(radian);
}

template <typename T1, typename T2>
inline double bp_atan2(T1 y, T2 x) {
	return atan2(y, x);
}

template <typename T>
inline double bp_sinh(T radian) {
	return sinh(radian);
}

template <typename T>
inline double bp_cosh(T radian) {
	return cosh(radian);
}

template <typename T>
inline double bp_tanh(T radian) {
	return tanh(radian);
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

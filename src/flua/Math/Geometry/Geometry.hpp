#include <cmath>

template <typename T>
inline double flua_sin(T radian) {
	return sin(radian);
}

template <typename T>
inline double flua_cos(T radian) {
	return cos(radian);
}

template <typename T>
inline double flua_tan(T radian) {
	return tan(radian);
}

template <typename T>
inline double flua_asin(T radian) {
	return asin(radian);
}

template <typename T>
inline double flua_acos(T radian) {
	return acos(radian);
}

template <typename T>
inline double flua_atan(T radian) {
	return atan(radian);
}

template <typename T1, typename T2>
inline double flua_atan2(T1 y, T2 x) {
	return atan2(y, x);
}

template <typename T>
inline double flua_sinh(T radian) {
	return sinh(radian);
}

template <typename T>
inline double flua_cosh(T radian) {
	return cosh(radian);
}

template <typename T>
inline double flua_tanh(T radian) {
	return tanh(radian);
}
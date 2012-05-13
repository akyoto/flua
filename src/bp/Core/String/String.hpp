#include <cstring>
#define _toString(x) (new BPUTF8String(const_cast<char*>(x)))

template <typename T>
inline size_t bp_insertInt(char* ptr, const T num, const size_t index) {
	return fast_itoa_10(num, ptr + index);
}

template <typename T>
inline size_t bp_strlen(T ptr) {
	return strlen(ptr);
}

/**
 * C++ version 0.4 char* style "itoa":
 * Written by Lukás Chmela
 * Released under GPLv3.
 * 
 * Very slightly modified for this specific case.
 */
template <typename T>
size_t fast_itoa_10(T value, char* result) {
	// check that the base if valid
	// if (base < 2 || base > 36) { *result = '\0'; return result; }

	char* ptr = result, *ptr1 = result, tmp_char;
	T tmp_value;

	do {
		tmp_value = value;
		value /= 10;
		*ptr++ = "zyxwvutsrqponmlkjihgfedcba9876543210123456789abcdefghijklmnopqrstuvwxyz" [35 + (tmp_value - value * 10)];
	} while ( value );
	
	int numbersAdded(ptr - result);

	// Apply negative sign
	if (tmp_value < 0) *ptr++ = '-';
	//*ptr-- = '\0';
	--ptr;
	while(ptr1 < ptr) {
		tmp_char = *ptr;
		*ptr--= *ptr1;
		*ptr1++ = tmp_char;
	}
	
	return numbersAdded;
}

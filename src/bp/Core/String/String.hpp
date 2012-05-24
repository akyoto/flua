#include <cstring>
#include <iostream>
#define _toString(x) (new BPUTF8String(const_cast<char*>(x)))

template <typename T>
inline size_t bp_insertInt(char* ptr, const T num, const size_t index) {
	return fast_itoa_10(num, ptr + index);
}

template <typename T>
inline size_t bp_strlen(T ptr) {
	return strlen(ptr);
}

// TODO: Optimize
inline size_t bp_strlen_utf8_xchars(char* _s, size_t _limit) {
	char *start = _s;
	char b;
	size_t count = 0;
	_limit++;
	
	while(count < _limit) {
		b = *_s++;
		if (((b >> 7) & ((~b) >> 6)) == 0)
			count++;
	}
	
	return _s - start - 1;
}

// TODO: Optimize
inline void bp_utf8_slice(
		char* &myData, 
		size_t &myLen,
		size_t &myLenInBytes,
		char* _s,
		size_t _from,
		size_t _limit)
{
	char b;
	size_t count = 0;
	if(_from < 0)
		_from = 0;

	while(count <= _from) {
		b = *_s++;
		if (((b >> 7) & ((~b) >> 6)) == 0)
			count++;
		if(b == '\0')
			break;
	}

	count = 0;
	myData = --_s;

	while(count <= _limit) {
		b = *_s++;
		if (((b >> 7) & ((~b) >> 6)) == 0)
			count++;
		if(b == '\0')
			break;
	}

	myLen = count - 1;
	myLenInBytes = _s - myData - 1;
}

inline size_t bp_strlen_utf8(char* _s) {
	char b;
	size_t count = 0;
	
	while((b = *_s++) != '\0') {
		if (((b >> 7) & ((~b) >> 6)) == 0)
			count++;
	}
	
	return count;
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

// C/C++ files
//#include <hash/phsieh.hpp>
#include <hash/murmur3.hpp>

// bp modules
#include <flua/Core/String/UTF8String/C++/UTF8String.hpp>

// Hash Pointer Type
//#define HPT(x) reinterpret_cast<const char*>(x)
#define HPT(x) reinterpret_cast<void*>(x)
#define MURMUR_SEED 32

// Hash functions

/* Murmur3 */
template <typename T>
inline Int32 flua_hash(T key) {
	Int32 h;
	MurmurHash3_x86_32(HPT(&key), sizeof(T), MURMUR_SEED, &h);
	return h;
}

// Strings
inline Int32 flua_hash(BPUTF8String* key) {
	Int32 h;
	MurmurHash3_x86_32(HPT(key->_data), key->_length, MURMUR_SEED, &h);
	return h;
}

// Other objects
template <typename T>
inline Int32 flua_hash(T* key) {
	Int32 h;
	MurmurHash3_x86_32(HPT(&key), sizeof(T*), MURMUR_SEED, &h);
	return h;
}

/* P. Hsieh
// Int, Float, etc.
template <typename T>
inline Int32 flua_hash(T key) {
	return MurmurHash3_x86_32(HPT(&key), sizeof(T));
}

// Strings
inline Int32 flua_hash(BPUTF8String* key) {
	return SuperFastHash(HPT(key->_data), key->_length);
}

// Other objects
template <typename T>
inline Int32 flua_hash(T* key) {
	return SuperFastHash(HPT(&key), sizeof(T*));
}*/

/*
// This function can hash the content of an object instead of its pointer value
template <typename T>
inline Int32 flua_hashContent(T* key) {
	return SuperFastHash(HPT(key), sizeof(T));
}
*/

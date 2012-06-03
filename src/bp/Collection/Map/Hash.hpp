// C/C++ files
#include <hash/phsieh.hpp>

// bp modules
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>
#define HPT(x) reinterpret_cast<const char*>(x)

// Hash functions

// Int, Float, etc.
template <typename T>
inline Int32 bp_hash(T key) {
	return SuperFastHash(HPT(&key), sizeof(T));
}

// Strings
inline Int32 bp_hash(BPUTF8String* key) {
	return SuperFastHash(HPT(key->_data), key->_length);
}

// Other objects
template <typename T>
inline Int32 bp_hash(T* key) {
	return SuperFastHash(HPT(&key), sizeof(T*));
}

/*
// This function can hash the content of an object instead of its pointer value
template <typename T>
inline Int32 bp_hashContent(T* key) {
	return SuperFastHash(HPT(key), sizeof(T));
}
*/

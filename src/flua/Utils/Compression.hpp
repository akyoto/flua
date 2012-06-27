#include "lz4/lz4.c"

// bp
#include <flua/Collection/Vector/C++/Vector.hpp>
#include <flua/Collection/Vector/C++/Mutable.hpp>

inline Size flua_compressMaxSize(int inputSize) {
	return LZ4_compressBound(inputSize);
}

inline void flua_compress(Byte* source, BPMutableVector<Byte>* dest, Size size) {
	int numBytes = LZ4_compress(source, dest->_start, size);
	dest->_end = dest->_start + numBytes;
}

inline Int flua_compress(Byte* source, Byte* dest, Size size) {
	return LZ4_compress(source, dest, size);
}

inline void flua_uncompress(BPMutableVector<Byte>* compressed, BPMutableVector<Byte>* out) {
	int numBytes = LZ4_uncompress_unknownOutputSize(
		compressed->_start,
		out->_start,
		compressed->_end - compressed->_start, // getLength
		out->_endOfStorage - out->_start // getSize
	);
	out->_end = out->_start + numBytes;
}
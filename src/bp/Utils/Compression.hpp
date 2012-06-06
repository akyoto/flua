#include "lz4/lz4.c"

// bp
#include <bp/Collection/Array/C++/Array.hpp>
#include <bp/Collection/Array/C++/Mutable.hpp>

inline Size bp_compressMaxSize(int inputSize) {
	return LZ4_compressBound(inputSize);
}

inline void bp_compress(Byte* source, BPMutableArray<Byte>* dest, Size size) {
	int numBytes = LZ4_compress(source, dest->_start, size);
	dest->_end = dest->_start + numBytes;
}

inline Int bp_compress(Byte* source, Byte* dest, Size size) {
	return LZ4_compress(source, dest, size);
}

inline void bp_uncompress(BPMutableArray<Byte>* compressed, BPMutableArray<Byte>* out) {
	int numBytes = LZ4_uncompress_unknownOutputSize(
		compressed->_start,
		out->_start,
		compressed->_end - compressed->_start, // getLength
		out->_endOfStorage - out->_start // getSize
	);
	out->_end = out->_start + numBytes;
}
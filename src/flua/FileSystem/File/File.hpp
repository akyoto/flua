#include <sys/stat.h>
#include <cstdio>

// We need bp modules
#include <flua/Core/String/UTF8String/C++/UTF8String.hpp>

// Typedef
#define BPFileHandle FILE

// flua_fopen
inline BPFileHandle* flua_fopen(BPUTF8String* path, BPUTF8String* mode) {
	return fopen(*path, *mode);
}

template <typename T>
inline size_t flua_fwrite(BPFileHandle* fh, T* buffer, size_t bufferSize) {
	return fwrite(buffer, sizeof(T), bufferSize, fh);
}

template <typename T>
inline size_t flua_fwrite(BPFileHandle* fh, T value, size_t valueSize) {
	return fwrite(&value, sizeof(T), valueSize, fh);
}

// flua_fflush
inline bool flua_fflush(BPFileHandle* fh) {
	return !fflush(fh);
}

// flua_fclose
inline bool flua_fclose(BPFileHandle* fh) {
	return !fclose(fh);
}

// flua_fread
template <typename T>
inline size_t flua_fread(BPFileHandle* fh, T* buffer, size_t bufferSize) {
	return fread(buffer, sizeof(T), bufferSize, fh);
}

// flua_fileModificationTime
template <typename T>
inline time_t flua_fileModificationTime(T file) {
	struct stat fileInfo;
	
	if(stat(*file, &fileInfo) != 0) {
		return 0;
	}
	
	return fileInfo.st_mtime;
}

// flua_deleteFile
inline bool flua_deleteFile(BPUTF8String* fileName) {
	return !remove(*fileName);
}

// flua_renameFile
inline bool flua_renameFile(BPUTF8String* oldFile, BPUTF8String* newFile) {
	return !rename(*oldFile, *newFile); 
}

// flua_fileExists
inline bool flua_fileExists(BPUTF8String* fileName) {
	struct stat fileInfo;
	if(stat(*fileName, &fileInfo))
		return false;
	return true;
}

// flua_fileSize
inline size_t flua_fileSize(BPUTF8String* fileName) {
	struct stat fileInfo;
	if(stat(*fileName, &fileInfo))
		return 0;
	return fileInfo.st_size;
}

#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>
#include <cstdio>
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>

// Typedef
#define BPFileHandle FILE

// bp_fopen
inline BPFileHandle* bp_fopen(BPUTF8String* path, BPUTF8String* mode) {
	return fopen(*path, *mode);
}

// bp_fwrite
inline size_t bp_fwrite(BPFileHandle* fh, BPUTF8String *contents) {
	return fwrite(*contents, sizeof(Byte), contents->_lengthInBytes, fh);
}

// bp_fflush
inline bool bp_fflush(BPFileHandle* fh) {
	return !fflush(fh);
}

// bp_fclose
inline bool bp_fclose(BPFileHandle* fh) {
	return !fclose(fh);
}

// bp_fread
template <typename T>
inline size_t bp_fread(BPFileHandle* fh, T* buffer, size_t bufferSize) {
	return fread(buffer, sizeof(T), bufferSize, fh);
}

// bp_fileModificationTime
template <typename T>
inline time_t bp_fileModificationTime(T file) {
	struct stat fileInfo;
	
	if(stat(*file, &fileInfo) != 0) {
		return 0;
	}
	
	return fileInfo.st_mtime;
}

// bp_deleteFile
inline bool bp_deleteFile(BPUTF8String* fileName) {
	return !remove(*fileName);
}

// bp_renameFile
inline bool bp_renameFile(BPUTF8String* oldFile, BPUTF8String* newFile) {
	return !rename(*oldFile, *newFile); 
}

// bp_fileExists
inline bool bp_fileExists(BPUTF8String* fileName) {
	struct stat fileInfo;
	if(stat(*fileName, &fileInfo))
		return false;
	return true;
}

// bp_fileSize
inline size_t bp_fileSize(BPUTF8String* fileName) {
	struct stat fileInfo;
	if(stat(*fileName, &fileInfo))
		return 0;
	return fileInfo.st_size;
}

// bp_changeDir
inline bool bp_changeDir(BPUTF8String* url) {
	return !chdir(*url);
}

// bp_getCurrentDir
inline BPUTF8String* bp_getCurrentDir() {
	char *temp  = new (UseGC) char[PATH_MAX];
	
	if(getcwd(temp, PATH_MAX) != NULL) {
		return new BPUTF8String(temp);
	}
	
	/*int error = errno;

    switch ( error ) {
        // EINVAL can't happen - size argument > 0

        // PATH_MAX includes the terminating nul, 
        // so ERANGE should not be returned

        case EACCES:
            throw std::runtime_error("Access denied");

        case ENOMEM:
            // I'm not sure whether this can happen or not 
            throw std::runtime_error("Insufficient storage");

        default: {
            std::ostringstream str;
            str << "Unrecognised error" << error;
            throw std::runtime_error(str.str());
        }
    }*/
	
	return _toString("");
}

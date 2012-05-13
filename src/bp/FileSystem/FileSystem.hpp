#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>
#include <bp/Core/String/UTF8String-out.hpp>
#include <iostream>

// bp_fileModificationTime
template <typename T>
time_t bp_fileModificationTime(T file) {
	struct stat fileInfo;
	
	if(stat(*file, &fileInfo) != 0) {
		return 0;
	}
	
	return fileInfo.st_mtime;
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
	
	std::cout << "Error" << PATH_MAX << std::endl;
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

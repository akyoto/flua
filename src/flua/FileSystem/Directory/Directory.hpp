#include <dirent.h>
#include <limits.h>
#include <unistd.h>

// We need bp modules
#include <flua/Core/String/UTF8String/C++/UTF8String.hpp>
#include <flua/FileSystem/Directory/C++/Exceptions.hpp>

// Typedef
#define BPDirectoryHandle DIR

// flua_changeDir
inline bool flua_changeDir(BPUTF8String* url) {
	return !chdir(*url);
}

// flua_openDir
inline BPDirectoryHandle* flua_openDir(BPUTF8String* url) {
	return opendir(url->_data);
}

// flua_closeDir
inline void flua_closeDir(BPDirectoryHandle* dir) {
	closedir(dir);
}

// flua_getNextFile
inline BPUTF8String* flua_getNextFile(BPDirectoryHandle* dir) {
	struct dirent* ent = readdir(dir);
	
	if(ent == NULL)
		return EMPTY_STRING;
	
	return _toString(ent->d_name);
	//String tmp = ent->d_name;
	//return tmp != "." && tmp != ".." ? tmp : GetNextFile();
}

// flua_getCurrentDir
inline BPUTF8String* flua_getCurrentDir() {
	char *temp  = new (UseGC) char[PATH_MAX];
	
	if(getcwd(temp, PATH_MAX) != NULL) {
		return new BPUTF8String(temp);
	}
	
	/*switch(errorno) {
		case EACCES:
			throw new BPAccessDeniedException();
		
		case ENOMEM:
			throw new BPInsufficientStorageException();
		
		default: {
			throw new BPException();
		}
	}*/
	
	return EMPTY_STRING;
}

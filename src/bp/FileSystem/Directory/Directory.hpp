#include <dirent.h>
#include <limits.h>
#include <unistd.h>

// We need bp modules
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>
#include <bp/FileSystem/Directory/C++/Exceptions.hpp>

// Typedef
#define BPDirectoryHandle DIR

// bp_changeDir
inline bool bp_changeDir(BPUTF8String* url) {
	return !chdir(*url);
}

// bp_openDir
inline BPDirectoryHandle* bp_openDir(BPUTF8String* url) {
	return opendir(url->_data);
}

// bp_closeDir
inline void bp_closeDir(BPDirectoryHandle* dir) {
	closedir(dir);
}

// bp_getNextFile
inline BPUTF8String* bp_getNextFile(BPDirectoryHandle* dir) {
	struct dirent* ent = readdir(dir);
	
	if(ent == NULL)
		return EMPTY_STRING;
	
	return _toString(ent->d_name);
	//String tmp = ent->d_name;
	//return tmp != "." && tmp != ".." ? tmp : GetNextFile();
}

// bp_getCurrentDir
inline BPUTF8String* bp_getCurrentDir() {
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

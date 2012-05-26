#include <pthread.h>

/*#define BPThreadHandle HANDLE

inline void bp_createThread(BPThreadHandle &hThread, unsigned ( __stdcall *start_address )( void * ), void *arg) {
	unsigned threadId;
	hThread = (HANDLE)_beginthreadex(
		NULL,
		0,
		start_address,
		NULL,
		0,
		&threadId
	);
}*/
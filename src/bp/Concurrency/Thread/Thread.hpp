#include <pthread.h>

#define BPThreadHandle pthread_t

template <typename T1, typename T2>
inline bool bp_createThread(BPThreadHandle* pThread, T1 func, T2 args) {
	return pthread_create(pThread, NULL, func, args) == 0;
}
#include <unistd.h>

inline size_t bp_getCPUCount() {
#ifdef WINDOWS
	SYSTEM_INFO sysInfo;
	GetSystemInfo(&sysInfo);
	return sysInfo.dwNumberOfProcessors;
#else
	return sysconf(_SC_NPROCESSORS_ONLN);
#endif
}

template <typename T1, typename T2>
inline void bp_atomicAdd(T1 &var, T2 value) {
	__sync_fetch_and_add(&var, value);
}

template <typename T1, typename T2>
inline void bp_atomicSetFlag(T1 &ref, T2 value) {
	asm volatile("":::"memory");
	ref = value;
}

// CAS
// _InterlockedCompareExchange
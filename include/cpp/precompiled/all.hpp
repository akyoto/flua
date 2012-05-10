// Two underscores because it makes the header look important and cool
#ifndef __bp_precompiler_header
#define __bp_precompiler_header

#include <cstdint>
#include <cstdlib>

#ifdef BP_USE_BOEHM_GC
	// ./configure
	//  --enable-cplusplus
	//  --enable-threads=posix
	//  --enable-thread-local-alloc
	//  --enable-parallel-mark
	
	//compile with
	//	-DUSE_LIBC_PRIVATES
	//	-DPARALLEL_MARK
	
	#define GC_THREADS
	#define _REENTRANT
	#define GC_OPERATOR_NEW_ARRAY
	#define PARALLEL_MARK
	#define USE_LIBC_PRIVATE
	
	#include "../gc/gc_cpp.h"
#endif

#ifdef BP_USE_GMP
	// ./configure
	//  --enable-cxx
	//  --enable-fat
	#include <gmpxx.h>
	#include <gmp.h>
#endif

#ifdef BP_USE_BOOST
	#include "../boost/shared_ptr.hpp"
	#include "../boost/enable_shared_from_this.hpp"
#endif

#endif

// Two underscores because it makes the header look important and cool
#ifndef __bp_precompiler_header
#define __bp_precompiler_header

#include <cstdint>
#include <cstdlib>

#ifdef BP_USE_BOEHM_GC
	#include "../gc/gc_cpp.h"
#endif

#ifdef BP_USE_GMP
	#include "../gmp/gmpxx.h"
#endif

#ifdef BP_USE_BOOST
	#include "../boost/shared_ptr.hpp"
	#include "../boost/enable_shared_from_this.hpp"
#endif

#endif

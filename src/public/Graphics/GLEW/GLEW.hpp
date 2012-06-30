#ifdef _WIN32
	#include "Windows/glew.h"
	
	/*namespace glewWGL {
		#include "Windows/wglew.h"
	}*/
#else
	
	#include "Linux/glew.h"
	
	/*namespace glewGLX {
		inline void glXSwapIntervalSGI(bool enable) {}
	}*/
	
	/*namespace glewGLX {
		#include "Linux/glxew.h"
	}*/
#endif
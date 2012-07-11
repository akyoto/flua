#include <FreeImage/FreeImage.h>

inline void FreeImage_init() {
	FreeImage_Initialise();
}

inline void FreeImage_exit() {
	FreeImage_DeInitialise();
}
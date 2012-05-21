#include <bp/Concurrency/GPU/C++/Exception.hpp>

// Global
cl_platform_id _bp_cl_platforms[4];
cl_device_id _bp_cl_devices[8];
cl_uint _bp_cl_platformID = 0;
cl_uint _bp_cl_deviceID = 0;

cl_uint _bp_cl_numPlatforms;
cl_uint _bp_cl_numDevices;

BPUTF8String* _bp_cl_platformNames[4];
BPUTF8String* _bp_cl_deviceNames[8];

// Functions
inline void bp_setActiveGPUPlatform(int id) {
	if(id < 0)
		return;
		
	_bp_cl_platformID = id;
	
	if(clGetDeviceIDs(_bp_cl_platforms[_bp_cl_platformID], CL_DEVICE_TYPE_GPU, 8, _bp_cl_devices, &_bp_cl_numDevices) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	char *deviceName = new char[256];
	if(clGetDeviceInfo(_bp_cl_devices[_bp_cl_platformID], CL_DEVICE_NAME, 256, deviceName, NULL) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	_bp_cl_deviceNames[_bp_cl_platformID] = _toString(deviceName);
}

void bp_initGPUCalculations() {
	if(clGetPlatformIDs(4, _bp_cl_platforms, &_bp_cl_numPlatforms) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	if(_bp_cl_numPlatforms < 1) {
		return;
	}

	for(size_t i = 0; i < _bp_cl_numPlatforms; i++) {
		char *platformName = new char[256];
		clGetPlatformInfo(_bp_cl_platforms[i], CL_PLATFORM_NAME, 256, platformName, NULL);
		_bp_cl_platformNames[i] = _toString(platformName);
	}
	
	bp_setActiveGPUPlatform(0);
}

inline BPUTF8String* bp_getCLPlatformName(int id = -1) {
	if(id < 0)
		return _bp_cl_platformNames[_bp_cl_platformID];
	
	return _bp_cl_platformNames[id];
}

inline size_t bp_getCLPlatformCount() {
	return _bp_cl_numPlatforms;
}

inline BPUTF8String* bp_getCLDeviceName(int id = -1) {
	if(id < 0)
		return _bp_cl_deviceNames[_bp_cl_deviceID];
	
	return _bp_cl_deviceNames[id];
}

inline size_t bp_getGPUCount() {
	return _bp_cl_numDevices;
}
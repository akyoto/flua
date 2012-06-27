#include <flua/Concurrency/GPU/C++/Exception.hpp>

// Global
cl_platform_id _flua_cl_platforms[4];
cl_device_id _flua_cl_devices[8];
cl_uint _flua_cl_platformID = 0;
cl_uint _flua_cl_deviceID = 0;

cl_uint _flua_cl_numPlatforms;
cl_uint _flua_cl_numDevices;

BPUTF8String* _flua_cl_platformNames[4];
BPUTF8String* _flua_cl_deviceNames[8];

// Functions
inline void flua_setActiveGPUPlatform(int id) {
	if(id < 0)
		return;
		
	_flua_cl_platformID = id;
	
	if(clGetDeviceIDs(_flua_cl_platforms[_flua_cl_platformID], CL_DEVICE_TYPE_GPU, 8, _flua_cl_devices, &_flua_cl_numDevices) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	char *deviceName = new char[256];
	if(clGetDeviceInfo(_flua_cl_devices[_flua_cl_platformID], CL_DEVICE_NAME, 256, deviceName, NULL) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	_flua_cl_deviceNames[_flua_cl_platformID] = _toString(deviceName);
}

void flua_initGPUCalculations() {
	if(clGetPlatformIDs(4, _flua_cl_platforms, &_flua_cl_numPlatforms) != CL_SUCCESS) {
		throw new BPGPUInitException();
	}
	
	if(_flua_cl_numPlatforms < 1) {
		return;
	}

	for(size_t i = 0; i < _flua_cl_numPlatforms; i++) {
		char *platformName = new char[256];
		clGetPlatformInfo(_flua_cl_platforms[i], CL_PLATFORM_NAME, 256, platformName, NULL);
		_flua_cl_platformNames[i] = _toString(platformName);
	}
	
	flua_setActiveGPUPlatform(0);
}

inline BPUTF8String* flua_getCLPlatformName(int id = -1) {
	if(id < 0)
		return _flua_cl_platformNames[_flua_cl_platformID];
	
	return _flua_cl_platformNames[id];
}

inline size_t flua_getCLPlatformCount() {
	return _flua_cl_numPlatforms;
}

inline BPUTF8String* flua_getCLDeviceName(int id = -1) {
	if(id < 0)
		return _flua_cl_deviceNames[_flua_cl_deviceID];
	
	return _flua_cl_deviceNames[id];
}

inline size_t flua_getGPUCount() {
	return _flua_cl_numDevices;
}
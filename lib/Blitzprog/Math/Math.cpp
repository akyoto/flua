#include "Math.hpp"

//Static Var/FPS map
static map<int*, FPSInfo> fpsVarMap;

//UpdateFPS
bool UpdateFPS(int &fpsVar)
{
	FPSInfo &fpsInfo = fpsVarMap[&fpsVar];
	++fpsInfo.currentFrame;
	
	if(MilliSecs() - fpsInfo.lastCheck >= 1000)
	{
		fpsVar = fpsInfo.currentFrame;
		fpsInfo.currentFrame = 0;
		fpsInfo.lastCheck = MilliSecs();
		return 1;
	}
	
	return 0;
}

//UpdateFPS
bool UpdateFPS(int &fpsVar, DWORD updateInterval)
{
	FPSInfo &fpsInfo = fpsVarMap[&fpsVar];
	++fpsInfo.currentFrame;
	
	if(MilliSecs() - fpsInfo.lastCheck >= updateInterval)
	{
		fpsVar = fpsInfo.currentFrame * 1000 / updateInterval;
		fpsInfo.currentFrame = 0;
		fpsInfo.lastCheck = MilliSecs();
		return 1;
	}
	
	return 0;
}

//SwapByteOrder8
void SwapByteOrder8(byte *ptr)
{
	byte t = ptr[0];
	ptr[0] = ptr[7];
	ptr[7] = t;
	t = ptr[1];
	ptr[1] = ptr[6];
	ptr[6] = t;
	t = ptr[2];
	ptr[2] = ptr[5];
	ptr[5] = t;
	t = ptr[3];
	ptr[3] = ptr[4];
	ptr[4] = t;
}

//SwapByteOrder4
void SwapByteOrder4(byte *ptr)
{
	byte t = ptr[0];
	ptr[0] = ptr[3];
	ptr[3] = t;
	t = ptr[1];
	ptr[1] = ptr[2];
	ptr[2] = t;
	//return num >> 24 | (((num << 8) >> 24) << 8) | (((num >> 8) << 24) >> 8) | num << 24;	//<< 2 == * 4
}

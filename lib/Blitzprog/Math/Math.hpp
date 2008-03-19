////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Math
// Author:				Eduard Urbach
// Description:			Mathematical functions
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_MATH_HPP_
#define BLITZPROG_MATH_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>

//C++ standard header files
#include <cmath>
#include <map>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//FPSInfo
struct FPSInfo
{
	DWORD lastCheck;
	DWORD currentFrame;
};

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Pi
const float Pi = 3.1415926535897932384626433832795f;
const double PiAsDouble = 3.1415926535897932384626433832795;

//Deg <-> Rad
const float RAD_TO_DEG = 57.2957795130823208767981548141052f;
const float DEG_TO_RAD = 0.0174532925199432957692369076848861f;

//Rand
const float RAND_MAX_FLOAT_INV = 1.0f / RAND_MAX;

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//UpdateFPS
bool UpdateFPS(int &fpsVar);
bool UpdateFPS(int &fpsVar, DWORD updateInterval);

//SwapByteOrder8
void SwapByteOrder8(byte *ptr);

//SwapByteOrder4
void SwapByteOrder4(byte *ptr);

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//TODO: Add static map<int*, int>

//UpdateFrameTime (not thread-safe, use it only in one thread)
template <typename T>
inline void UpdateFrameTime(T &frmTimeVar)
{
	static T lastUpdateTime = MilliSecs();
	frmTimeVar = MilliSecs() - lastUpdateTime;
	lastUpdateTime = MilliSecs();
}

//UpdateFrameTime (not thread-safe, use it only in one thread)
template <typename T>
inline void UpdateFrameTime(T &frmTimeVar, T scalar)
{
	static T lastUpdateTime = MilliSecs();
	frmTimeVar = (MilliSecs() - lastUpdateTime) * scalar;
	lastUpdateTime = MilliSecs();
}

//UpdateFrameTime (not thread-safe, use it only in one thread)
template <typename T>
inline void UpdateFrameTime(T &frmTimeVar, T scalar, T increment)
{
	static T lastUpdateTime = MilliSecs();
	frmTimeVar = (MilliSecs() - lastUpdateTime) * scalar + increment;
	lastUpdateTime = MilliSecs();
}

//GetFPS (not thread-safe, use it only in one thread)
inline int GetFPS()
{
	static int staticFPS = 0;
	UpdateFPS(staticFPS);
	return staticFPS;
}

//SwapByteOrder2
inline void SwapByteOrder2(byte *ptr)
{
	byte t = ptr[0];
	ptr[0] = ptr[1];
	ptr[1] = t;
}

//SwapByteOrder
inline double SwapByteOrder(double num)
{
	SwapByteOrder8(reinterpret_cast<byte*>(&num));
	return num;
}

//SwapByteOrder
inline long SwapByteOrder(long num)
{
	SwapByteOrder4(reinterpret_cast<byte*>(&num));
	return num;
}

//SwapByteOrder
inline int SwapByteOrder(int num)
{
	SwapByteOrder4(reinterpret_cast<byte*>(&num));
	return num;
}

//SwapByteOrder
inline float SwapByteOrder(float num)
{
	SwapByteOrder4(reinterpret_cast<byte*>(&num));
	return num;
}

//SwapByteOrder
inline short SwapByteOrder(short num)
{
	SwapByteOrder2(reinterpret_cast<byte*>(&num));
	return num;
}

//SwapByteOrder
inline byte SwapByteOrder(byte num)
{
	return num;
}

//TODO: SwapBitOrder
/*
//SwapBitOrder
inline byte SwapBitOrder(byte num)
{
	num = ((num >> 4) & 0x0F) | ((num << 4) & 0xF0);
	num = ((num >> 2) & 0x33) | ((num << 2) & 0xCC);
	return ((num >> 1) & 0x55) | ((num << 1) & 0xAA);
}

//SwapBitOrder2
inline byte SwapBitOrder2(byte num)
{
	num = (num & 0xF0) >> 4 | (num & 0x0F) << 4;
	num = (num & 0xCC) >> 2 | (num & 0x33) << 2;
	return (num & 0xAA) >> 1 | (num & 0x55) << 1;
}
*/

//IsPowerOfTwo
inline bool IsPowerOfTwo(int value)
{
    return value ? ((value & -value) == value) : false;
}

//IsPowerOfTwo
inline bool IsPowerOfTwo(float value)
{
    return IsPowerOfTwo(static_cast<int>(value));
}

//IsPythagoreanTriple
template <typename T1, typename T2, typename T3>
inline bool IsPythagoreanTriple(T1 a, T2 b, T3 c)
{
    return a * a + b * b == c * c;
}

//Abs
template <typename T>
inline T Abs(T val)
{
	return val < 0 ? -val : val;	//This is also possible: Max(-val, val);
}

//Sgn
template <typename T>
inline int Sgn(T val)
{
	return val > 0 ? 1 : (val < 0 ? -1 : 0);
}

//Sq
template <typename T>
inline T Sq(T num)
{
	return num * num;
}

//Sqr
template <typename T>
inline float Sqr(T num)
{
	return sqrtf(num);
}

//Sqr
inline double Sqr(double num)
{
	return sqrt(num);
}

//DegToRad
inline float DegToRad(float degree)
{
	return degree * DEG_TO_RAD;
}

//RadToDeg
inline float RadToDeg(float rad)
{
	return rad * RAD_TO_DEG;
}

//Sin
inline float Sin(float degree)
{
	return sinf(degree * DEG_TO_RAD);
}

//SinRad
inline float SinRad(float rad)
{
	return sinf(rad);
}

//Cos
inline float Cos(float degree)
{
	return cosf(degree * DEG_TO_RAD);
}

//CosRad
inline float CosRad(float rad)
{
	return cosf(rad);
}

//ASin
inline float ASin(float sinValueDegree)
{
	return asinf(sinValueDegree) * RAD_TO_DEG;
}

//ASinRad
inline float ASinRad(float sinValueRad)
{
	return asinf(sinValueRad);
}

//ACos
inline float ACos(float cosValueDegree)
{
	return acosf(cosValueDegree) * RAD_TO_DEG;
}

//ACosRad
inline float ACosRad(float cosValueRad)
{
	return acosf(cosValueRad);
}

//ATan
inline float ATan(float tanValueDegree)
{
	return atanf(tanValueDegree) * RAD_TO_DEG;
}

//ATanRad
inline float ATanRad(float tanValueRad)
{
	return atanf(tanValueRad);
}

//ATan2
inline float ATan2(float x, float y)
{
	return atan2f(y, x) * RAD_TO_DEG;
}

//ATan2Rad
inline float ATan2Rad(float x, float y)
{
	return atan2f(y, x);
}

//Log
inline float Log(float x)
{
	return logf(x);
}

//Log10
/*
 * <en>Returns the base-10 logarithm of x.</en>
 * <de>Berechnet den Logarithmus zur Basis 10.</de>
 * */
inline float Log10(float x)
{
	return log10f(x);
}

//RoundUp
/* 
 * <en>Round up value.</en>
 * <de>Wert aufrunden.</de>
 * */
inline float RoundUp(float x)
{
	return ceilf(x);
}

//RoundDown
/* 
 * <en>Round down value.</en>
 * <de>Wert abrunden.</de>
 * */
inline float RoundDown(float x)
{
	return floorf(x);
}

//SeedRnd
inline void SeedRnd(unsigned int seed)
{
	srand(seed);	//TODO: Thread-safety
}

//Rand
inline int Rand(int rangeStart, int rangeEnd)
{
	return rand() % (rangeEnd - rangeStart + 1) + rangeStart;	//TODO: Thread-safety
}

//RandFloat
inline float RandFloat(float rangeStart, float rangeEnd)
{
	return (rand() * RAND_MAX_FLOAT_INV) * (rangeEnd - rangeStart) + rangeStart;	//TODO: Thread-safety
}

//DistanceSq
template <typename xT, typename yT, typename xT2, typename yT2>
inline float DistanceSq(xT x1, yT y1, xT2 x2, yT2 y2)
{
	return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

//DistanceSq
template <typename xT, typename yT, typename zT, typename xT2, typename yT2, typename zT2>
inline float DistanceSq(xT x1, yT y1, zT z1, xT2 x2, yT2 y2, zT2 z2)
{
	return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) + (z2 - z1) * (z2 - z1);
}

//Distance
template <typename xT, typename yT, typename xT2, typename yT2>
inline float Distance(xT x1, yT y1, xT2 x2, yT2 y2)
{
	return Sqr(DistanceSq(x1, y1, x2, y2));	//Sqr((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

//Distance
template <typename xT, typename yT, typename zT, typename xT2, typename yT2, typename zT2>
inline float Distance(xT x1, yT y1, zT z1, xT2 x2, yT2 y2, zT2 z2)
{
	return Sqr(DistanceSq(x1, y1, z1, x2, y2, z2));	//Sqr((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) + (z2 - z1) * (z2 - z1));
}

//Min
template <typename T>
inline const T &Min(const T &a, const T &b)
{
	return a < b ? a : b;
}

//Max
template <typename T>
inline const T &Max(const T &a, const T &b)
{
	return a > b ? a : b;
}

//Add
template <typename T>
inline const T &Add(const T &a, const T &b)
{
	return a + b;
}

//Sub
template <typename T>
inline const T &Sub(const T &a, const T &b)
{
	return a - b;
}

//Mul
template <typename T>
inline const T &Mul(const T &a, const T &b)
{
	return a * b;
}

//Div
template <typename T>
inline const T &Div(const T &a, const T &b)
{
	return a / b;
}

//ConstFactorial
template <size_t x>
class ConstFactorialTemplate {
	public:
	    static const size_t value = x * ConstFactorialTemplate<x-1>::value;
};

template <>
class ConstFactorialTemplate<1> {
	public:
	    static const size_t value = 1;
};

#define ConstFactorial(x) ConstFactorialTemplate<x>::value;

//Factorial
template <typename T>
inline T Factorial(T n)
{
	T tmp = 1;
	for(T i = 2; i <= n; ++i)
		tmp *= i;
	return tmp;
}

//BinomialCoefficient
template <typename T>
inline T BinomialCoefficient(T n, T k)
{
	return Factorial(n) / (Factorial(k) * Factorial(n - k));
}

//TODO: Convert these functions
/*
'Gibt die Entfernung zwischen den beiden angegebenen Punkten zurück.
Function Distance:Float(fParX1:Float, fParY1:Float, fParX2:Float = 0, fParY2:Float = 0)
   Return Sqr((fParX1 - fParX2) * (fParX1 - fParX2) + (fParY1 - fParY2) * (fParY1 - fParY2))
End Function

'Gibt die Entfernung zwischen den beiden angegebenen Punkten zurück, ohne vorher die Wurzel zu ziehen. Ein bischen schneller, dafür nicht für alles geeignet.
Function DistanceQuad:Float(fParX1:Float, fParY1:Float, fParX2:Float = 0, fParY2:Float = 0)
   Return ((fParX1 - fParX2) * (fParX1 - fParX2) + (fParY1 - fParY2) * (fParY1 - fParY2))
End Function

'Gibt die ungefähre (Integer) Entfernung zwischen den beiden angegebenen Punkten zurück.
Function IntDistance:Int(iParX1:Int, iParY1:Int, iParX2:Int = 0, iParY2:Int = 0)
   Return Sqr((iParX1 - iParX2) * (iParX1 - iParX2) + (iParY1 - iParY2) * (iParY1 - iParY2))
End Function

'Gibt die ungefähre (Integer) Entfernung zwischen den beiden angegebenen Punkten zurück, ohne vorher die Wurzel zu ziehen. Ein bischen schneller, dafür nicht für alles geeignet.
Function IntDistanceQuad:Int(iParX1:Int, iParY1:Int, iParX2:Int = 0, iParY2:Int = 0)
   Return ((iParX1 - iParX2) * (iParX1 - iParX2) + (iParY1 - iParY2) * (iParY1 - iParY2))
End Function

'Schätzt die Distanz zwischen 2 Punkten ab. Als Parameter werden jeweils bereits die Differenzen verlangt.
'iParXD = (iParX1 - iParX2)
'iParYD = (iParY1 - iParY2)
Function ApproxDistance:Int(iParXD:Int, iParYD:Int)
   Local iMin:Int
   Local iMax:Int
   
   If iParXD < 0 Then iParXD = -iParXD
   If iParYD < 0 Then iParYD = -iParYD
   If iParXD < iParYD Then
      iMin = iParXD
      iMax = iParYD
   Else
      iMin = iParYD
      iMax = iParXD
   EndIf
   
   Return (((iMax Shl 8) + (iMax Shl 3) - (iMax Shl 4) - (iMax Shl 1) + (iMin Shl 7) - (iMin Shl 5) + (iMin Shl 3) - (iMin Shl 1)) Shr 8)
End Function

'Liefert den Winkel von Punkt 2 zu Punkt 1 zurück.
'Beispiel: Punkt 1 liegt bei 0,0, Punkt 2 bei 10,0
'Dann wird der Winkel 90 zurückgeliefert.
Function Angle:Float(fX1:Float, fY1:Float, fX2:Float, fY2:Float)
   Return (ATan2(fY2 - fY1, fX2 - fX1) + 450.0) Mod 360.0
End Function

'Wie Angle, aber etwas schneller. Dafür arbeitet IntAngle nur mit Integer-Werten, folglich treten Rundungsfehler auf.
Function IntAngle:Float(iX1:Int, iY1:Int, iX2:Int, iY2:Int)
   Return (Int(ATan2(iY2 - iY1, iX2 - iX1)) + 450) Mod 360
End Function

'Dreht und Skaliert die angegebenen Koordinaten im angegebenen Winkel um eine Mitte die Mitte 0,0.
Function TransformCoord:Byte(fVarX:Float Var, fVarY:Float Var, fAngle:Float, fParCenterX:Float = 0.0, fParCenterY:Float = 0.0, fScale:Float = 1.0)
   Local fTempAngle:Float = Angle(fParCenterX, fParCenterY, fVarX, fVarY) + fAngle
   Local fTempDist:Float = Distance(fVarX, fVarY, fParCenterX, fParCenterY) * fScale
   fVarX = fParCenterX + Sin(fTempAngle) * fTempDist
   fVarY = fParCenterY - Cos(fTempAngle) * fTempDist
   Return True
End Function

'Dreht und Skaliert die angegebenen Koordinaten im angegebenen Winkel um die Mitte 0,0. Ungenauer als die Float-Funktion, dafür aber schneller. Nur für Werte ab 10 gedacht, ansonsten extremst ungenau.
Function IntTransformCoord:Byte(iVarX:Int Var, iVarY:Int Var, iAngle:Int, iParCenterX:Int = 0.0, iParCenterY:Int = 0.0, fScale:Float = 1.0)
   Local iTempAngle:Int = IntAngle(iParCenterX, iParCenterY, iVarX, iVarY) + iAngle
   Local iTempDist:Int = IntDistance(iVarX, iVarY, iParCenterX, iParCenterY) * fScale
   iVarX = iParCenterX + Sin(iTempAngle) * iTempDist
   iVarY = iParCenterY - Cos(iTempAngle) * iTempDist
   Return True
End Function 
*/

//DiffSwitch
int DiffSwitch(const unsigned int b, unsigned int n, const unsigned int z)
{
	--n;
	int result = 0;
	for(unsigned int i = 0; i <= n; ++i)
	{
		result += ((z*(n-i)+1) - (z*i+1)) * static_cast<int>(pow(static_cast<float>(b), static_cast<int>(n-i)));
	}
	return result;
}

#endif /*BLITZPROG_MATH_HPP_*/

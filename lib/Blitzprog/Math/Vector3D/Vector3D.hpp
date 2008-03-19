////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Math.Vector3D
// Author:				Eduard Urbach
// Description:			3D Vector
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_MATH_VECTOR3D_HPP_
#define BLITZPROG_MATH_VECTOR3D_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Math/Math.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Vector3D
template <typename vecTX=float, typename vecTY=float, typename vecTZ=float>
class TVector3D: public TPrintable
{
	protected:
		typedef TVector3D<vecTX, vecTY, vecTZ> TPL_TVector3D;
		
	public:
		
		//Public vars
		vecTX x;
		vecTY y;
		vecTZ z;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor (default)
		TVector3D() : x(0.0f), y(0.0f), z(0.0f)
		{
			
		}
		
		//Constructor (float, float, float)
		template <typename TX, typename TY, typename TZ>
		TVector3D(TX nX, TY nY, TZ nZ) : x(nX), y(nY), z(nZ)
		{
			
		}
		
		//Constructor (float)
		template <typename T>
		TVector3D(T nVal) : x(nVal), y(nVal), z(nVal)
		{
			
		}
		
		//Constructor (float array)
		template <typename T>
		TVector3D(T *floatArray) : x(floatArray[0]), y(floatArray[1]), z(floatArray[2])
		{
			
		}
		
		//Constructor (copy)
		TVector3D(const TPL_TVector3D &vec) : x(vec.x), y(vec.y), z(vec.z)
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator = (Vector3D &)
		inline TPL_TVector3D &operator=(const TPL_TVector3D &vec)
		{
			x = vec.x;
			y = vec.y;
			z = vec.z;
			return *this;
		}
		
		//Operator += (Vector3D &)
		inline void operator+=(const TPL_TVector3D &vec)
		{
			x += vec.x;
			y += vec.y;
			z += vec.z;
		}
		
		//Operator -= (Vector3D &)
		inline void operator-=(const TPL_TVector3D &vec)
		{
			x -= vec.x;
			y -= vec.y;
			z -= vec.z;
		}
		
		//Operator *= (Vector3D &)
		inline void operator*=(const TPL_TVector3D &vec)
		{
			x *= vec.x;
			y *= vec.y;
			z *= vec.z;
		}
		
		//Operator /= (Vector3D &)
		inline void operator/=(const TPL_TVector3D &vec)
		{
			x /= vec.x;
			y /= vec.y;
			z /= vec.z;
		}
		
		//Operator += (numeric)
		template <typename T>
		inline void operator+=(T val)
		{
			x += val;
			y += val;
			z += val;
		}
		
		//Operator -= (numeric)
		template <typename T>
		inline void operator-=(T val)
		{
			x -= val;
			y -= val;
			z -= val;
		}
		
		//Operator *= (numeric)
		template <typename T>
		inline void operator*=(T val)
		{
			x *= val;
			y *= val;
			z *= val;
		}
		
		//Operator /= (numeric)
		template <typename T>
		inline void operator/=(T val)
		{
			x /= val;
			y /= val;
			z /= val;
		}
		
		//Operator + (Vector3D &)
		inline TPL_TVector3D operator+(const TPL_TVector3D &vec)
		{
			return TPL_TVector3D(x + vec.x, y + vec.y, z + vec.z);
		}
		
		//Operator * (float)
		template <typename T>
		inline TPL_TVector3D operator*(T s)
		{
			return TPL_TVector3D(x * s, y * s, z * s);
		}
		
		//TODO: -
		/*/Operator -
		inline TPL_TVector3D operator-()
		{
			return TPL_TVector3D(-x, -y, -z);
		}*/
		
		//Operator - (Vector3D &)
		inline TPL_TVector3D operator-(const TPL_TVector3D &vec)
		{
			return TPL_TVector3D(x - vec.x, y - vec.y, z - vec.z);
		}
		
		//Operator ->
		inline TPL_TVector3D *operator->()
		{
			return this;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast (float array)
		inline operator float*()
		{
			return reinterpret_cast<float*>(this);
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//SetPosition
		template <typename TX, typename TY, typename TZ>
		inline void SetPosition(TX nX, TY nY, TZ nZ)
		{
			x = nX;
			y = nY;
			z = nZ;
		}
		
		//SetX
		template <typename T>
		inline void SetX(T nX)
		{
			x = nX;
		}
		
		//SetY
		template <typename T>
		inline void SetY(T nY)
		{
			y = nY;
		}
		
		//SetZ
		template <typename T>
		inline void SetZ(T nZ)
		{
			z = nZ;
		}
		
		//GetLength
		inline float GetLength() const
		{
			return Sqr(x * x + y * y + z * z);
		}
		
		//GetLengthSq
		inline float GetLengthSq() const
		{
			return x * x + y * y + z * z;
		}
		
		//GetDotProduct
		inline float GetDotProduct(const TPL_TVector3D &vec) const
		{
			return x * vec.x + y * vec.y + z * vec.z;
		}
		
		//GetCrossProduct
		inline TPL_TVector3D GetCrossProduct(const TPL_TVector3D &vec) const
		{
			return TPL_TVector3D(y * vec.z - z * vec.y, z * vec.x - x * vec.z, x * vec.y - y * vec.x);
		}
		
		//GetAngle
		inline float GetAngle(const TPL_TVector3D &vec) const
		{
			return ACosRad((x * vec.x + y * vec.y + z * vec.z) / Sqr((x * x + y * y + z * z) * (vec.x * vec.x + vec.y * vec.y + vec.z * vec.z)));
		}
		
		//GetNormalizedVector
		inline TPL_TVector3D GetNormalizedVector() const
		{
			float l = GetLength();
			if(l != 0)
				return TPL_TVector3D(x / l, y / l, z / l);
			return TPL_TVector3D(0.0f, 0.0f, 0.0f);
		}
		
		//Normalize
		inline void Normalize()
		{
			float len = GetLength();
			if(len != 0.0f)
			{
				x /= len;
				y /= len;
				z /= len;
			}
		}
		
		//ToString
		inline String ToString() const
		{
			return String(x) + ", " + y + ", " + z;
		}
};

//Vector3D
typedef TVector3D<float, float, float> Vector3D;
typedef TVector3D<int, int, int> IntVector3D;

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////

//NullVector
static Vector3D NullVector(0, 0, 0);

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//NormalizeVector
inline Vector3D NormalizeVector(Vector3D &vec)
{
	return vec.GetNormalizedVector();
}

//TODO: Remove this
//D3D specific functions
#ifdef D3DVECTOR_DEFINED
	//TODO: Can this be optimized?
	inline D3DVECTOR ToD3DVECTOR(Vector3D &vec)
	{
		D3DVECTOR tmp = {vec.x, vec.y, vec.z};
		return tmp;
	}
#endif

#endif // BLITZPROG_MATH_VECTOR3D_HPP_

////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Math.Vector2D
// Author:				Eduard Urbach
// Description:			2D Vector (point)
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_MATH_VECTOR2D_HPP_
#define BLITZPROG_MATH_VECTOR2D_HPP_

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

//Vector2D
template <typename vecTX=int, typename vecTY=int>
class TVector2D: public TPrintable
{
	protected:
		typedef TVector2D<vecTX, vecTY> TPL_TVector2D;
		
	public:
		
		//Public vars
		vecTX x;
		vecTY y;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor (default)
		TVector2D() : x(0), y(0)
		{
			
		}
		
		//Constructor (int, int)
		template <typename TX, typename TY>
		TVector2D(TX nX, TY nY) : x(nX), y(nY)
		{
			
		}
		
		//Constructor (int)
		template <typename T>
		TVector2D(T nVal) : x(nVal), y(nVal)
		{
			
		}
		
		//Constructor (int array)
		template <typename T>
		TVector2D(T *intArray) : x(intArray[0]), y(intArray[1])
		{
			
		}
		
		//Constructor (copy)
		TVector2D(const TPL_TVector2D &vec) : x(vec.x), y(vec.y)
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator = (Vector2D &)
		inline TPL_TVector2D &operator=(const TPL_TVector2D &vec)
		{
			x = vec.x;
			y = vec.y;
			return *this;
		}
		
		//Operator += (Vector2D &)
		inline void operator+=(const TPL_TVector2D &vec)
		{
			x += vec.x;
			y += vec.y;
		}
		
		//Operator -= (Vector2D &)
		inline void operator-=(const TPL_TVector2D &vec)
		{
			x -= vec.x;
			y -= vec.y;
		}
		
		//Operator *= (Vector2D &)
		inline void operator*=(const TPL_TVector2D &vec)
		{
			x *= vec.x;
			y *= vec.y;
		}
		
		//Operator /= (Vector2D &)
		inline void operator/=(const TPL_TVector2D &vec)
		{
			x /= vec.x;
			y /= vec.y;
		}
		
		//Operator += (numeric)
		template <typename T>
		inline void operator+=(T val)
		{
			x += val;
			y += val;
		}
		
		//Operator -= (numeric)
		template <typename T>
		inline void operator-=(T val)
		{
			x -= val;
			y -= val;
		}
		
		//Operator *= (numeric)
		template <typename T>
		inline void operator*=(T val)
		{
			x *= val;
			y *= val;
		}
		
		//Operator /= (numeric)
		template <typename T>
		inline void operator/=(T val)
		{
			x /= val;
			y /= val;
		}
		
		//Operator + (Vector2D &)
		inline TPL_TVector2D operator+(const TPL_TVector2D &vec)
		{
			return TPL_TVector2D(x + vec.x, y + vec.y);
		}
		
		//Operator *
		template <typename T>
		inline TPL_TVector2D operator*(T s)
		{
			return TPL_TVector2D(x * s, y * s);
		}
		
		//TODO: -
		/*/Operator -
		inline TPL_TVector3D operator-()
		{
			return TPL_TVector3D(-x, -y, -z);
		}*/
		
		//Operator - (Vector2D &)
		inline TPL_TVector2D operator-(const TPL_TVector2D &vec)
		{
			return TPL_TVector2D(x - vec.x, y - vec.y);
		}
		
		//Operator ->
		inline TPL_TVector2D *operator->()
		{
			return this;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast (int array)
		inline operator int*()
		{
			return reinterpret_cast<int*>(this);
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//SetPosition
		template <typename TX, typename TY>
		inline void SetPosition(TX nX, TY nY)
		{
			x = nX;
			y = nY;
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
		
		//GetLength
		inline float GetLength() const
		{
			return Sqr(x * x + y * y);
		}
		
		//GetLengthSq
		inline float GetLengthSq() const
		{
			return x * x + y * y;
		}
		
		//GetDotProduct
		inline float GetDotProduct(const TPL_TVector2D &vec) const
		{
			//TODO: Implement this
			return x * vec.x + y * vec.y;
		}
		
		//GetAngle
		inline int GetAngle(const TPL_TVector2D &vec) const
		{
			//TODO: Implement this
			//return ACosRad((x * vec.x + y * vec.y) / Sqr((x * x + y * y) * (vec.x * vec.x + vec.y * vec.y)));
			return static_cast<int>(ATan2((vec.y - y), (vec.x - x)) + 360) % 360;
		}
		
		//GetNormalizedVector
		inline TPL_TVector2D GetNormalizedVector() const
		{
			float l = GetLength();
			if(l != 0)
				return TPL_TVector2D(static_cast<vecTX>(x / l), static_cast<vecTY>(y / l));
			return TPL_TVector2D(0, 0);
		}
		
		//Normalize
		inline void Normalize()
		{
			float len = GetLength();
			if(len != 0)
			{
				x /= len;
				y /= len;
			}
		}
		
		//ToString
		inline String ToString() const
		{
			return String(x) + ", " + y;
		}
};

//Vector2D
typedef TVector2D<int, int> Vector2D;
typedef TVector2D<float, float> FloatVector2D;
typedef Vector2D Point;

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////

//NullPoint
static Vector2D NullPoint(0, 0);

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//GetAngle
template <typename T>
inline int GetAngle(T x1, T y1, T x2, T y2)
{
	return static_cast<int>(ATan2((y2 - y1), (x2 - x1)) + 360) % 360;
}

//NormalizeVector
inline Vector2D NormalizeVector(Vector2D &vec)
{
	return vec.GetNormalizedVector();
}

#endif // BLITZPROG_MATH_VECTOR3D_HPP_

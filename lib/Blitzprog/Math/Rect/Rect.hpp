////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Core
// Author:				Eduard Urbach
// Description:			Core functions
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_MATH_RECT_HPP_
#define BLITZPROG_MATH_RECT_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Math/Math.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Rect
template <typename T>
class TRect: public TPrintable
{
	public:
		
		//Public vars
		T x;
		T y;
		T width;
		T height;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor (default)
		TRect() : x(0), y(0), width(0), height(0)
		{
			//Debug info
			EngineLogNew("Rect: " << x << ", " << y << ", " << width << ", " << height);
		}
		
		//Constructor
		TRect(T xpos, T ypos, T iWidth, T iHeight) : x(xpos), y(ypos), width(iWidth), height(iHeight)
		{
			//Debug info
			EngineLogNew("Rect: " << x << ", " << y << ", " << width << ", " << height);
		}
		
#ifdef WIN32
		//Constructor
		TRect(const RECT &rect) : x(rect.left), y(rect.top), width(rect.right - rect.left), height(rect.bottom - rect.top)
		{
			//Debug info
			EngineLogNew("Rect: " << x << ", " << y << ", " << width << ", " << height);
		}
#endif
		
		//Destructor
		~TRect()
		{
			//Debug info
			EngineLogDelete("Rect: " << x << ", " << y << ", " << width << ", " << height);
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
#ifdef WIN32
		//Operator = (RECT)
		inline void operator=(RECT &rect)
		{
			x = rect.left;
			y = rect.top;
			width = rect.right - x;
			height = rect.bottom - y;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast (RECT)
		inline operator RECT() const
		{
			//TODO: Reduce to one code line, if possible
			RECT tmp = {x, y, x + width, y + height};
			return tmp;
		}
#endif
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		// GET & SET //
		
		//SetX
		inline void SetX(T nX)
		{
			x = nX;
		}
		
		//SetY
		inline void SetY(T nY)
		{
			y = nY;
		}
		
		//SetPosition
		inline void SetPosition(T nX, T nY)
		{
			x = nX;
			y = nY;
		}
		
		//SetWidth
		inline void SetWidth(T nWidth)
		{
			width = nWidth;
		}
		
		//SetHeight
		inline void SetHeight(T nHeight)
		{
			height = nHeight;
		}
		
		//SetSize
		inline void SetSize(T nWidth, T nHeight)
		{
			width = nWidth;
			height = nHeight;
		}
		
		//SetRect
		inline void SetRect(T nX, T nY, T nWidth, T nHeight)
		{
			x = nX;
			y = nY;
			width = nWidth;
			height = nHeight;
		}
		
#ifdef WIN32
		//SetRect
		inline void SetRect(RECT &rect)
		{
			x = rect.left;
			y = rect.top;
			width = rect.right - x;
			height = rect.bottom - y;
		}
#endif
		
		//GetX
		inline T GetX() const
		{
			return x;
		}
		
		//GetY
		inline T GetY() const
		{
			return y;
		}
		
		//GetWidth
		inline T GetWidth() const
		{
			return width;
		}
		
		//GetHeight
		inline T GetHeight() const
		{
			return height;
		}
		
		//ToString
		inline String ToString() const
		{
			return Str(x) + ", " + y + ", " + width + ", " + height;
		}
};
typedef TRect<int> Rect;
#define CreateRect Rect

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif /*BLITZPROG_MATH_RECT_HPP_*/

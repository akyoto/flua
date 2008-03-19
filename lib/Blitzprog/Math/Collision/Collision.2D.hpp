////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Math.Collision.2D
// Author:				Eduard Urbach
// Description:			2D Collision detection
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_MATH_COLLISION_2D_HPP_
#define BLITZPROG_MATH_COLLISION_2D_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Math/Math.hpp>
//#include <Blitzprog/Math/Vector2D/Vector2D.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

#define MATH_USE_ALIAS

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//RectsIntersect
template 	<
				typename TX1, typename TY1, typename TW1, typename TH1,
				typename TX2, typename TY2, typename TW2, typename TH2
			>
inline bool RectsIntersect(TX1 x1, TY1 y1, TW1 w1, TH1 h1, TX2 x2, TY2 y2, TW2 w2, TH2 h2)
{
	return !(x1 + w1 < x2 || y1 + h1 < y2 || x1 > x2 + w2 || y1 > y2 + h2);
}
#ifdef MATH_USE_ALIAS
	#define RectRectIntersect RectsIntersect
#endif

//RectCircleIntersect
template <typename rectPosT, typename circlePosT, typename circleRadiusT>
inline bool RectCircleIntersect(rectPosT rectX, rectPosT rectY, rectPosT rectWidth, rectPosT rectHeight, circlePosT circleX, circlePosT circleY, circleRadiusT circleRadius)
{
	circlePosT tX = circleX;
	circlePosT tY = circleY;
	
	if(tX < rectX)
		tX = rectX;
	if(tX > rectX + rectWidth)
		tX = rectX + rectWidth;
	if(tY < rectY)
		tY = rectY;
	if(tY > rectY + rectHeight)
		tY = rectY + rectHeight;
	
	return ((circleX - tX) * (circleX - tX) + (circleY - tY) * (circleY - tY)) < circleRadius * circleRadius;
}

//CirclesIntersect
template <typename circlePosT, typename circleRadiusT, typename circlePosT2, typename circleRadiusT2>
inline bool CirclesOverlap(circlePosT circleX, circlePosT circleY, circleRadiusT circleRadius, circlePosT2 circleX2, circlePosT2 circleY2, circleRadiusT2 circleRadius2)
{
	return DistanceSq(circleX, circleY, circleX2, circleY2) < (circleRadius + circleRadius2) * (circleRadius + circleRadius2);
}
#ifdef MATH_USE_ALIAS
	#define CircleCircleIntersect CirclesIntersect
#endif

//SpheresIntersect
template <typename spherePosT, typename sphereRadiusT, typename spherePosT2, typename sphereRadiusT2>
inline bool SpheresIntersect(spherePosT sphereX, spherePosT sphereY, spherePosT sphereZ, sphereRadiusT sphereRadius, spherePosT2 sphereX2, spherePosT2 sphereY2, spherePosT2 sphereZ2, sphereRadiusT2 sphereRadius2)
{
	return DistanceSq(sphereX, sphereY, sphereZ, sphereX2, sphereY2, sphereZ2) <= Sq(sphereRadius + sphereRadius2);
}
#ifdef MATH_USE_ALIAS
	#define SphereSphereIntersect SpheresIntersect
#endif

#endif /*BLITZPROG_MATH_COLLISION_2D_HPP_*/

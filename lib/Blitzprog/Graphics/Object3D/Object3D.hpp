////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Graphics.Object3D
// Author:				Eduard Urbach
// Description:			Base class for 3D objects
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GRAPHICS_OBJECT3D_HPP_
#define BLITZPROG_GRAPHICS_OBJECT3D_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Math/Vector3D/Vector3D.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Object3D
class TObject3D
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TObject3D() : position(0), rotation(0), scaling(1), viewDirection(0, 0, 1), upVector(0, 1, 0), rightVector(1, 0, 0)
		{
			//Debug info
			EngineLogNew("Object3D");
		}
		
		//Constructor
		TObject3D(Vector3D &pos, Vector3D &rot, Vector3D &scl) : position(pos), rotation(rot), scaling(scl)
		{
			//Debug info
			EngineLogNew("Object3D");
			
			//TODO: Recalculate vectors
		}
		
		//Constructor
		TObject3D(Vector3D &pos, Vector3D &rot, Vector3D &scl, Vector3D &viewVec, Vector3D &upVec, Vector3D &rightVec) : position(pos), rotation(rot), scaling(scl), viewDirection(viewVec), upVector(upVec), rightVector(rightVec)
		{
			//Debug info
			EngineLogNew("Object3D");
		}
		
		//Destructor
		~TObject3D()
		{
			//Debug info
			EngineLogDelete("Object3D");
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		// GET //
		
		//GetPosition
		inline Vector3D &GetPosition()
		{
			return position;
		}
		
		//GetX
		inline float GetX()
		{
			return position.x;
		}
		
		//GetY
		inline float GetY()
		{
			return position.y;
		}
		
		//GetZ
		inline float GetZ()
		{
			return position.z;
		}
		
		//GetRotation
		inline Vector3D &GetRotation()
		{
			return rotation;
		}
		
		//GetRotationX
		inline float GetRotationX()
		{
			return rotation.x;
		}
		
		//GetRotationY
		inline float GetRotationY()
		{
			return rotation.y;
		}
		
		//GetRotationZ
		inline float GetRotationZ()
		{
			return rotation.z;
		}
		
		//GetScaling
		inline Vector3D &GetScaling()
		{
			return scaling;
		}
		
		//GetScalingX
		inline float GetScalingX()
		{
			return scaling.x;
		}
		
		//GetScalingY
		inline float GetScalingY()
		{
			return scaling.y;
		}
		
		//GetScalingZ
		inline float GetScalingZ()
		{
			return scaling.z;
		}
		
		//GetViewDirection()
		inline Vector3D &GetViewDirection()
		{
			return viewDirection;
		}
		
		//GetUpVector
		inline Vector3D &GetUpVector()
		{
			return upVector;
		}
		
		//GetRightVector
		inline Vector3D &GetRightVector()
		{
			return rightVector;
		}
		
		// SET //
		
		//SetPosition
		template <typename TX, typename TY, typename TZ>
		inline void SetPosition(TX x, TY y, TZ z)
		{
			position.x = x;
			position.y = y;
			position.z = z;
		}
		
		//SetPosition
		inline void SetPosition(Vector3D &vec)
		{
			position = vec;
		}
		
		//Transform
		template <typename TX, typename TY, typename TZ>
		inline void Transform(TX x, TY y, TZ z)
		{
			position.x += x;
			position.y += y;
			position.z += z;
		}
		
		//Transform
		inline void Transform(Vector3D &vec)
		{
			position += vec;
		}
		
		//TransformX
		template <typename T>
		inline void TransformX(T x)
		{
			position.x += x;
		}
		
		//TransformY
		template <typename T>
		inline void TransformY(T y)
		{
			position.y += y;
		}
		
		//TransformZ
		template <typename T>
		inline void TransformZ(T z)
		{
			position.z += z;
		}
		
		//Move
		template <typename TX, typename TY, typename TZ>
		inline void Move(TX x, TY y, TZ z)
		{
			position += rightVector * x + upVector * y + viewDirection * z;
		}
		
		//Move
		inline void Move(Vector3D &vec)
		{
			position += rightVector * vec.x + upVector * vec.y + viewDirection * vec.z;
		}
		
		//MoveX
		template <typename T>
		inline void MoveX(T x)
		{
			position += rightVector * x;
		}
		
		//MoveY
		template <typename T>
		inline void MoveY(T y)
		{
			position += upVector * y;
		}
		
		//MoveZ
		template <typename T>
		inline void MoveZ(T z)
		{
			position += viewDirection * z;
		}
		
		//SetRotation
		template <typename TX, typename TY, typename TZ>
		inline void SetRotation(TX xRot, TY yRot, TZ zRot)
		{
			//TODO: Optimize this
			Rotate(rotation.x - xRot, rotation.y - yRot, rotation.z - zRot);
		}
		
		//SetRotation
		inline void SetRotation(Vector3D &vec)
		{
			//TODO: Optimize this
			Rotate(rotation.x - vec.x, rotation.y - vec.y, rotation.z - vec.z);
		}
		
		//Rotate
		template <typename TX, typename TY, typename TZ>
		inline void Rotate(TX xRot, TY yRot, TZ zRot)
		{
			//TODO: Optimize this
			RotateX(xRot);
			RotateY(yRot);
			RotateZ(zRot);
		}
		
		//Rotate
		template <typename T>
		inline void Rotate(T uniform)
		{
			//TODO: Optimize this
			RotateX(uniform);
			RotateY(uniform);
			RotateZ(uniform);
		}
		
		//RotateX
		template <typename T>
		inline void RotateX(T xRot)
		{
			rotation.x += xRot;
			
			//Rotate viewDirection around the rightVector
			viewDirection = (viewDirection * Cos(xRot) + upVector * Sin(xRot));	//Cos(xRot) == Cos(-xRot)
			viewDirection.Normalize();
			
			//Compute the new upVector (by cross product)
			upVector = viewDirection.GetCrossProduct(rightVector);
		}
		
		//RotateY
		template <typename T>
		inline void RotateY(T yRot)
		{
			rotation.y += yRot;
			
			//Rotate viewDirection around the upVector
			viewDirection = (viewDirection * Cos(yRot) - rightVector * Sin(yRot));	//Cos(yRot) == Cos(-yRot)
			viewDirection.Normalize();
			
			//Compute the new rightVector (by cross product)
			rightVector = viewDirection.GetCrossProduct(upVector) * -1;	//TODO: Optimize this
		}
		
		//RotateZ
		template <typename T>
		inline void RotateZ(T zRot)
		{
			rotation.z += zRot;
			
			//Rotate viewDirection around the rightVector
			rightVector = (rightVector * Cos(zRot) + upVector * Sin(zRot));
			rightVector.Normalize();
			
			//Compute the new upVector (by cross product)
			upVector = viewDirection.GetCrossProduct(rightVector);
		}
		
		//SetRotationX
		template <typename T>
		inline void SetRotationX(T xRot)
		{
			//TODO: Optimize this
			RotateX(xRot - rotation.x);
		}
		
		//SetRotationY
		template <typename T>
		inline void SetRotationY(T yRot)
		{
			//TODO: Optimize this
			RotateY(yRot - rotation.y);
		}
		
		//SetRotationZ
		template <typename T>
		inline void SetRotationZ(T zRot)
		{
			//TODO: Optimize this
			RotateZ(zRot - rotation.z);
		}
		
		//SetScaling
		template <typename T>
		inline void SetScaling(T xyz)
		{
			scaling = xyz;
		}
		
		//SetScaling
		template <typename TX, typename TY, typename TZ>
		inline void SetScaling(TX xScale, TY yScale, TZ zScale)
		{
			scaling.x = xScale;
			scaling.y = yScale;
			scaling.z = zScale;
		}
		
		//SetScaling
		inline void SetScaling(Vector3D &vec)
		{
			scaling = vec;
		}
		
		//SetScalingX
		template <typename T>
		inline void SetScalingX(T xScale)
		{
			scaling.x = xScale;
		}
		
		//SetScalingY
		template <typename T>
		inline void SetScalingY(T yScale)
		{
			scaling.y = yScale;
		}
		
		//SetScalingZ
		template <typename T>
		inline void SetScalingZ(T zScale)
		{
			scaling.z = zScale;
		}
		
		//Scale
		template <typename T>
		inline void Scale(T uniform)
		{
			scaling *= uniform;
		}
		
		//Scale
		template <typename TX, typename TY, typename TZ>
		inline void Scale(TX xScale, TY yScale, TZ zScale)
		{
			scaling.x *= xScale;
			scaling.y *= yScale;
			scaling.z *= zScale;
		}
		
		//Reset
		inline void Reset()
		{
			position = 0;
			rotation = 0;
			scaling = 1;
			viewDirection.SetPosition(0, 0, 1);
			upVector.SetPosition(0, 1, 0);
			rightVector.SetPosition(1, 0, 0);
		}
		
	protected:
		Vector3D position;
		Vector3D rotation;
		Vector3D scaling;
		Vector3D viewDirection;
		Vector3D upVector;
		Vector3D rightVector;
};
typedef SharedPtr<TObject3D> Object3D;
#define CreateObject3D new TObject3D

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif // BLITZPROG_GRAPHICS_OBJECT3D_HPP_

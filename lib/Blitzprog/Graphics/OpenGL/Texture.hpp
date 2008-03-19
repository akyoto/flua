////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Graphics.OpenGL.Texture
// Author:				Eduard Urbach
// Description:			OpenGL-specific texture class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GRAPHICS_OPENGL_TEXTURE_HPP_
#define BLITZPROG_GRAPHICS_OPENGL_TEXTURE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Graphics/GraphicsDriver.hpp>
#include <Blitzprog/Graphics/OpenGL/Header.hpp>
#include <Blitzprog/Pixmap/Pixmap.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//DrawImageCallInfo
struct DrawImageCallInfo
{
	int x;
	int y;
	int frame;
	
	Point handleXY;
	float z;					//Z
	int r, g, b, a;				//Color
	float rotationZ;			//Rotation
	float scalingX, scalingY;	//Scaling
};

//OpenGLTexture
class TOpenGLTexture;
typedef SharedPtr<TOpenGLTexture> OpenGLTexture;
class TOpenGLTexture: public TTexture
{
	public:
		
		//Public static vars
		static vector<OpenGLTexture> List;
		static float currentRotationZ;
		static float currentScalingX;
		static float currentScalingY;
		static float cosScaleX;
		static float cosScaleY;
		static float sinScaleX;
		static float sinScaleY;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TOpenGLTexture(Pixmap data) : handle(0)
		{
			//Debug info
			EngineLogNew("OpenGLTexture");
			
			//Add to list
			List.push_back(this);
			
			Load(data);
		}
		
		//Destructor
		~TOpenGLTexture()
		{
			//Debug info
			EngineLogDelete("OpenGLTexture");
			
			//TODO: Remove from list
			
			Destroy();
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
		
		//Load
		bool Load(Pixmap pixmap);
		
		//DrawQueue
		void DrawQueue();
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Destroy
		inline void Destroy()
		{
			if(handle)
			{
				glDeleteTextures(1, &handle);
				handle = 0;
			}
		}
		
		//Draw
		inline void Draw(	int x, int y, int frame,
							float z, int r, int g, int b, int a,
							float rotationZ, float scalingX, float scalingY)
		{
			DrawImageCallInfo tmp = {x, y, frame, handleXY, z, r, g, b, a, rotationZ, scalingX, scalingY};
			drawImageQueue.push_back(tmp);
		}
		
		//Update2DMatrix
		static inline void Update2DMatrix()
		{
			float cosRot = Cos(currentRotationZ);
			float sinRot = Sin(currentRotationZ);
			
			cosScaleX = cosRot * currentScalingX;
			cosScaleY = cosRot * currentScalingY;
			sinScaleX = sinRot * currentScalingX;
			sinScaleY = sinRot * -currentScalingY;
		}
		
	protected:
		GLuint handle;
		
		vector<DrawImageCallInfo> drawImageQueue;
};
#define CreateOpenGLTexture new TOpenGLTexture

//Static vars
#ifndef BLITZPROG_LIB
	vector<OpenGLTexture> TOpenGLTexture::List;
	float TOpenGLTexture::currentRotationZ;
	float TOpenGLTexture::currentScalingX;
	float TOpenGLTexture::currentScalingY;
	float TOpenGLTexture::cosScaleX;
	float TOpenGLTexture::cosScaleY;
	float TOpenGLTexture::sinScaleX;
	float TOpenGLTexture::sinScaleY;
#endif

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif // BLITZPROG_GRAPHICS_OPENGL_TEXTURE_HPP_

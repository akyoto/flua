////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Graphics.OpenGL
// Author:				Eduard Urbach
// Description:			OpenGL graphics
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GRAPHICS_OPENGL_HPP_
#define BLITZPROG_GRAPHICS_OPENGL_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Graphics/OpenGL/Header.hpp>
#include <Blitzprog/Graphics/GraphicsDriver.hpp>
#include <Blitzprog/Graphics/OpenGL/Texture.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

#define Z_2D_RESET -0.999999f
#define Z_2D_INCREASE 0.00001f

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//DrawRectCallInfo
struct DrawRectCallInfo
{
	int x;
	int y;
	int width;
	int height;
	
	float z;					//Z
	int r, g, b, a;				//Color
	float rotationZ;			//Rotation
	float scalingX, scalingY;	//Scaling
	float fHandleX, fHandleY;	//Handle
};

//DrawLineCallInfo
struct DrawLineCallInfo
{
	int x;
	int y;
	int toX;
	int toY;
	
	float z;					//Z
	int r, g, b, a;				//Color
	float rotationZ;			//Rotation
	float scalingX, scalingY;	//Scaling
	float fHandleX, fHandleY;	//Handle
};

//DrawPixelCallInfo
struct DrawPixelCallInfo
{
	int x;
	int y;
	
	float z;					//Z
	int r, g, b, a;				//Color
};

//DrawPixmapCallInfo
struct DrawPixmapCallInfo
{
	Pixmap pixmap;
	int x;
	int y;
	int frame;
};

//OpenGL
class TOpenGL: public TGraphicsDriver
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TOpenGL(Window win, int flags=0);
		
		//Destructor
		~TOpenGL();
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		//DrawCamera
		void DrawCamera(TCamera *cam);
		
		//DrawEntity
		void DrawEntity(TEntity *entity);
		
		//DrawSurface
		void DrawSurface(TSurface *surface);
		
		//SetRenderMode
		void SetRenderMode(RenderMode mode);
		
		//SetViewport
		void SetViewport(int x, int y, int width, int height);
		
		//RenderWorld
		void RenderWorld();
		
		//Set2D
		void Set2D();
		
		//Set3D
		void Set3D(float fovAngle = defaultFOVAngle, float zNear = defaultCameraNear, float zFar = defaultCameraFar);
		
		//Flush
		void Flush();
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//EnableCulling
		inline void EnableCulling()
		{
			glEnable(GL_CULL_FACE);
			culling = true;
		}
		
		//DisableCulling
		inline void DisableCulling()
		{
			glDisable(GL_CULL_FACE);
			culling = false;
		}
		
		//EnableLighting
		inline void EnableLighting()
		{
			glEnable(GL_LIGHTING);
			lighting = true;
		}
		
		//DisableLighting
		inline void DisableLighting()
		{
			glDisable(GL_LIGHTING);
			lighting = false;
		}
		
		//Cls
		inline void Cls()
		{
			//BEGIN_GL_FUNCS();
			glClear(clearFlags);
			//END_GL_FUNCS();
		}
		
		//Flip
		inline void Flip()
		{
			Flush();
#ifdef WIN32
			SwapBuffers(hDC);
#elif defined(LINUX)
			gdk_threads_enter();
			gdk_gl_drawable_swap_buffers(dr);
			gdk_threads_leave();
#endif
		}
		
		//SetClsColor
		inline void SetClsColor(int red, int green, int blue, int alpha=0)
		{
			glClearColor(RGBByteToFloat(red), RGBByteToFloat(green), RGBByteToFloat(blue), RGBByteToFloat(alpha));
		}
		
		//SetClsColorFloat
		inline void SetClsColorFloat(float red, float green, float blue, float alpha=0.0f)
		{
			glClearColor(red, green, blue, alpha);
		}
		
		//SetColor
		inline void SetColor(int red, int green, int blue)
		{
			color.SetComponents(red, green, blue);
		}
		
		//SetColor
		inline void SetColor(int red, int green, int blue, int alpha)
		{
			color.SetComponents(red, green, blue, alpha);
		}
		
		//SetColorFloat
		inline void SetColorFloat(float red, float green, float blue)
		{
			color.SetComponents(RGBFloatToByte(red), RGBFloatToByte(green), RGBFloatToByte(blue));
		}
		
		//SetColorFloat
		inline void SetColorFloat(float red, float green, float blue, float alpha)
		{
			color.SetComponents(RGBFloatToByte(red), RGBFloatToByte(green), RGBFloatToByte(blue), RGBFloatToByte(alpha));
		}
		
		//SetRotation
		inline void SetRotation(float zRotation)
		{
			rotationZ = zRotation;
		}
		
		//SetScale
		inline void SetScale(float xScale, float yScale)
		{
			scalingX = xScale;
			scalingY = yScale;
		}
		
		//DrawPixel
		inline void DrawPixel(int x, int y)
		{
			DrawPixelCallInfo tmp = {x, y, zPos2D, color.r, color.g, color.b, color.a};
			drawPixelQueue.push_back(tmp);
			zPos2D += Z_2D_INCREASE;
		}
		
		//DrawLine
		inline void DrawLine(int x, int y, int toX, int toY)
		{
			DrawLineCallInfo tmp = {x, y, toX, toY, zPos2D, color.r, color.g, color.b, color.a, rotationZ, scalingX, scalingY};
			drawLineQueue.push_back(tmp);
			zPos2D += Z_2D_INCREASE;
		}
		
		//DrawRect
		inline void DrawRect(int x, int y, int width, int height)
		{
			DrawRectCallInfo tmp = {x, y, width, height, zPos2D, color.r, color.g, color.b, color.a, rotationZ, scalingX, scalingY};
			drawRectQueue.push_back(tmp);
			zPos2D += Z_2D_INCREASE;
		}
		
		//DrawPixmap
		inline void DrawPixmap(Pixmap pixmap, int x, int y, int frame=0)
		{
			DrawPixmapCallInfo tmp = {pixmap, x, y, frame};
			drawPixmapQueue.push_back(tmp);
			zPos2D += Z_2D_INCREASE;
		}
		
		//DrawImage
		inline void DrawImage(Image img, int x, int y, int frame=0)
		{
			img->Draw(x, y, frame, zPos2D, color.r, color.g, color.b, color.a, rotationZ, scalingX, scalingY);
			zPos2D += Z_2D_INCREASE;
		}
		
		//LoadTexture
		inline Texture LoadTexture(Pixmap pixmap) const
		{
			return CreateOpenGLTexture(pixmap);
		}
		
		//Activate
		inline void Activate()
		{
#ifdef LINUX
			EngineLog5("Activating graphics driver");
			gdk_threads_enter();
			if(!gdk_gl_drawable_make_current(dr, ct))
			{
				EngineLogError("gdk_gl_drawable_make_current");
				return;
			}
			gdk_threads_leave();
#endif
		}
		
		//GetDriverName
		inline String GetDriverName() const
		{
			return "OpenGL";
		}
		
		//GetDriverVersion
		inline String GetDriverVersion() const
		{
			return strGLVersion;
		}
		
		//GetDriverExtraInformation
		inline String GetDriverExtraInformation() const
		{
			return "";	//TODO: 
		}
		
		//SetEntityMatrix
		inline void SetEntityMatrix(TEntity *entity)
		{
			//TODO: Optimize this
			glTranslatef(entity->GetX(), entity->GetY(), -entity->GetZ());
			glRotatef(entity->GetRotationX(), 1.0f, 0.0f, 0.0f);
			glRotatef(entity->GetRotationY(), 0.0f, 1.0f, 0.0f);
			glRotatef(entity->GetRotationZ(), 0.0f, 0.0f, 1.0f);
			glScalef(entity->GetScalingX(), entity->GetScalingY(), entity->GetScalingZ());
		}
		
		//SetCameraMatrix
		inline void SetCameraMatrix(TCamera *cam)
		{
			//Temp
			//TODO: Could be cached
			Vector3D &pos = cam->GetPosition();
			Vector3D viewPoint = pos + cam->GetViewDirection();
			Vector3D &upVector = cam->GetUpVector();
			
			//TODO: Optimize this
			gluLookAt(	pos.x, pos.y, -pos.z,
						viewPoint.x, viewPoint.y, -viewPoint.z,
						upVector.x, upVector.y, -upVector.z);
			
			//Camera scaling
			//glScalef(cam->GetScalingX(), cam->GetScalingY(), cam->GetScalingZ());	//TODO: Optimize this
		}
		
	protected:
#ifdef WIN32
		HDC hDC;
		HGLRC hRC;
#elif defined(LINUX)
		GdkGLContext* ct;
		GdkGLDrawable* dr;
#endif
		TColor<int> color;
		float rotationZ, scalingX, scalingY;
		
		//Queues
		vector<DrawPixelCallInfo> drawPixelQueue;
		vector<DrawLineCallInfo> drawLineQueue;
		vector<DrawRectCallInfo> drawRectQueue;
		vector<DrawPixmapCallInfo> drawPixmapQueue;
		
		//Handles
		Point handleXY;
		
		//Static vars
		static int graphicsContextCount;
		static GLbitfield clearFlags;
		static GLenum lastError;
		static String glewVersion;
		static String strGLVersion;
		static String strGLVendor;
		static String strGLRenderer;
		static bool tex2DEnabled;
		static float zPos2D;
};

//Static vars
#ifndef BLITZPROG_LIB
	int TOpenGL::graphicsContextCount = 0;
	GLbitfield TOpenGL::clearFlags;
	GLenum TOpenGL::lastError;
	String TOpenGL::glewVersion;
	String TOpenGL::strGLVersion;
	String TOpenGL::strGLVendor;
	String TOpenGL::strGLRenderer;
	bool TOpenGL::tex2DEnabled;
	float TOpenGL::zPos2D;
#endif

//OpenGLFactory
class TOpenGLFactory: public TGraphicsDriverFactory
{
	public:
		TOpenGLFactory()
		{
#ifdef LINUX
			int argc = 0;
			char **argv = Null;
			gdk_threads_enter();
			if(!GUIStartUp::bpGtkInitialized || !gtk_gl_init_check(&argc, &argv))
			{
				EngineLogError("GtkGL initialization failed");
			}
			gdk_threads_leave();
#endif
		}
		
		TGraphicsDriver *CreateGraphicsDriver(Window win, int flags=0)
		{
			return new TOpenGL(win, flags);
		}
};

#ifndef BLITZPROG_LIB
	static TOpenGLFactory OpenGLFactoryInstance;
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



#endif // BLITZPROG_GRAPHICS_OPENGL_HPP_

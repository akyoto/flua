////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Graphics
// Author:				Eduard Urbach
// Description:			2D/3D graphics
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GRAPHICS_HPP_
#define BLITZPROG_GRAPHICS_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/GUI/GUI.hpp>

#ifdef WIN32
	#include <Blitzprog/Graphics/Direct3D9/Direct3D9.hpp>
	#include <Blitzprog/Graphics/OpenGL/OpenGL.hpp>
#else
	#include <Blitzprog/Graphics/OpenGL/OpenGL.hpp>
#endif

//#include <Blitzprog/Graphics/NullDevice/NullDevice.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//SharedPtr<TGraphics>
class TGraphics;
typedef SharedPtr<TGraphics> Graphics;

//Graphics
class TGraphics: public TGraphicsDriver
{
	public:
		
		//Public static vars
		static Graphics currentGraphics;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TGraphics(Window win, int flags=0);
		
		//Destructor
		virtual ~TGraphics()
		{
			//Debug info
			EngineLogDelete("Graphics");
			
			//Delete driver instance
			delete driver;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator ->
		inline TGraphicsDriver *operator->()
		{
			return driver;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Set2D
		inline void Set2D()
		{
			driver->Set2D();
		}
		
		//Set3D
		inline void Set3D(float fovAngle = defaultFOVAngle, float zNear = defaultCameraNear, float zFar = defaultCameraFar)
		{
			driver->Set3D(fovAngle, zNear, zFar);
		}
		
		//Cls
		inline void Cls()
		{
			driver->Cls();
		}
		
		//Flip
		inline void Flip()
		{
			driver->Flip();
		}
		
		//RenderWorld
		inline void RenderWorld()
		{
			driver->RenderWorld();
		}
		
		//DrawEntity
		inline void DrawEntity(TEntity *entity)
		{
			driver->DrawEntity(entity);
		}
		
		//DrawSurface
		inline void DrawSurface(TSurface *surface)
		{
			driver->DrawSurface(surface);
		}
		
		//DrawPixel
		inline void DrawPixel(int x, int y)
		{
			driver->DrawPixel(x, y);
		}
		
		//DrawLine
		inline void DrawLine(int x, int y, int toX, int toY)
		{
			driver->DrawLine(x, y, toX, toY);
		}
		
		//DrawRect
		inline void DrawRect(int x, int y, int width, int height)
		{
			driver->DrawRect(x, y, width, height);
		}
		
		//DrawPixmap
		inline void DrawPixmap(Pixmap pixmap, int x, int y, int frame=0)
		{
			driver->DrawPixmap(pixmap, x, y, frame);
		}
		
		//DrawImage
		inline void DrawImage(Image img, int x, int y, int frame=0)
		{
			driver->DrawImage(img, x, y, frame);
		}
		
		//SetClsColor
		inline void SetClsColor(int red, int green, int blue, int alpha=0)
		{
			driver->SetClsColor(red, green, blue, alpha);
		}
		
		//SetClsColorFloat
		inline void SetClsColorFloat(float red, float green, float blue, float alpha=0.0f)
		{
			driver->SetClsColorFloat(red, green, blue, alpha);
		}
		
		//SetColor
		inline void SetColor(int red, int green, int blue)
		{
			driver->SetColor(red, green, blue);
		}
		
		//SetColor
		inline void SetColor(int red, int green, int blue, int alpha)
		{
			driver->SetColor(red, green, blue, alpha);
		}
		
		//SetColorFloat
		inline void SetColorFloat(float red, float green, float blue)
		{
			driver->SetColorFloat(red, green, blue);
		}
		
		//SetColorFloat
		inline void SetColorFloat(float red, float green, float blue, float alpha)
		{
			driver->SetColorFloat(red, green, blue, alpha);
		}
		
		//LoadTexture
		inline Texture LoadTexture(Pixmap pixmap) const
		{
			return driver->LoadTexture(pixmap);
		}
		
		//Activate
		inline void Activate()
		{
			driver->Activate();
		}
		
		//SetRenderMode
		inline void SetRenderMode(RenderMode mode)
		{
			driver->SetRenderMode(mode);
		}
		
		//SetViewport
		inline void SetViewport(int x, int y, int width, int height)
		{
			driver->SetViewport(x, y, width, height);
		}
		
		//SetRotation
		inline void SetRotation(float zRotation)
		{
			driver->SetRotation(zRotation);
		}
		
		//SetScale
		inline void SetScale(float xScale, float yScale)
		{
			driver->SetScale(xScale, yScale);
		}
		
		//GetDriver
		inline TGraphicsDriver *GetDriver()
		{
			return driver;
		}
		
		//GetDriverName
		inline String GetDriverName() const
		{
			return driver->GetDriverName();
		}
		
		//GetDriverVersion
		inline String GetDriverVersion() const
		{
			return driver->GetDriverVersion();
		}
		
		//InitializationFailed
		inline bool InitializationFailed() const
		{
			return driver->InitializationFailed();
		}
		
		//Friends
		friend inline void SetGraphics(Graphics g);
		
	protected:
		TGraphicsDriver *driver;
};

#ifndef BLITZPROG_LIB
	Graphics TGraphics::currentGraphics;
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

//CreateGraphics
#define CreateGraphics new TGraphics

//Set2D
inline void Set2D()
{
	cg->Set2D();
}

//Set3D
inline void Set3D(float fovAngle = defaultFOVAngle, float zNear = defaultCameraNear, float zFar = defaultCameraFar)
{
	cg->Set3D(fovAngle, zNear, zFar);
}

//SetGraphics
inline void SetGraphics(Graphics g)
{
	TGraphics::currentGraphics = g;
	cg = g->driver;
	cg->Activate();
}

//Cls
inline void Cls()
{
	cg->Cls();
}

//Flip
inline void Flip()
{
	cg->Flip();
}

//RenderWorld
inline void RenderWorld()
{
	cg->RenderWorld();
}

//SetClsColor
inline void SetClsColor(int red, int green, int blue, int alpha=0)
{
	cg->SetClsColor(red, green, blue, alpha);
}

//SetClsColorFloat
inline void SetClsColorFloat(float red, float green, float blue, float alpha=0.0f)
{
	cg->SetClsColorFloat(red, green, blue, alpha);
}

//SetColor
inline void SetColor(int red, int green, int blue)
{
	cg->SetColor(red, green, blue);
}

//SetColor
inline void SetColor(int red, int green, int blue, int alpha)
{
	cg->SetColor(red, green, blue, alpha);
}

//SetColorFloat
inline void SetColorFloat(float red, float green, float blue)
{
	cg->SetColorFloat(red, green, blue);
}

//SetColorFloat
inline void SetColorFloat(float red, float green, float blue, float alpha)
{
	cg->SetColorFloat(red, green, blue, alpha);
}

//DrawPixel
inline void DrawPixel(int x, int y)
{
	cg->DrawPixel(x, y);
}

//DrawLine
inline void DrawLine(int x, int y, int toX, int toY)
{
	cg->DrawLine(x, y, toX, toY);
}

//DrawRect
inline void DrawRect(int x, int y, int width, int height)
{
	cg->DrawRect(x, y, width, height);
}

//DrawPixmap
inline void DrawPixmap(Pixmap pixmap, int x, int y, int frame=0)
{
	cg->DrawPixmap(pixmap, x, y, frame);
}

//DrawImage
inline void DrawImage(Image img, int x, int y, int frame=0)
{
	cg->DrawImage(img, x, y, frame);
}

//SetRenderMode
inline void SetRenderMode(RenderMode mode)
{
	cg->SetRenderMode(mode);
}

//SetRotation
inline void SetRotation(float zRotation)
{
	cg->SetRotation(zRotation);
}

//SetScale
inline void SetScale(float xScale, float yScale)
{
	cg->SetScale(xScale, yScale);
}

//CurrentGraphics
inline Graphics CurrentGraphics()
{
	return TGraphics::currentGraphics;
}

//GraphicsWidth
inline int GraphicsWidth()
{
	return cg->GetGraphicsWidth();
}

//GraphicsHeight
inline int GraphicsHeight()
{
	return cg->GetGraphicsHeight();
}

//GraphicsWindow
inline Window GraphicsWindow()
{
	return cg->window;
}

//MouseX
inline int MouseX()
{
	return cg->window->GetMouseX();
}

//MouseY
inline int MouseY()
{
	return cg->window->GetMouseY();
}

//DrawCross
inline void DrawCross(int x, int y, int width, int height)
{
	//TODO: Export to graphics driver class
	cg->DrawLine(x, y, x + width, y + height);
	cg->DrawLine(x + width, y, x, y + height);
}

//DrawPlus
inline void DrawPlus(int x, int y, int width, int height)
{
	//TODO: Export to graphics driver class
	cg->DrawLine(x + width / 2, y, x + width / 2, y + height);
	cg->DrawLine(x, y + height / 2, x + width, y + height / 2);
}

//LoadImage
inline Image LoadImage(Pixmap pixmap)
{
	return cg->LoadTexture(pixmap);
}

//InitGraphics
inline void InitGraphics(int width, int height, int depth, bool fullscreen=true)
{
	static Window stdWin;
	static Graphics stdGfx;
	stdWin = CreateWindow(AppFileName(), -1, -1, width, height);
	stdGfx = CreateGraphics(stdWin, (depth > 16 ? GRAPHICS_32BIT : 0) | (fullscreen ? GRAPHICS_FULLSCREEN : 0));
	stdWin->Show();
}

#endif // BLITZPROG_GRAPHICS_HPP_

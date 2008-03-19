////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Graphics.GraphicsDriver
// Author:				Eduard Urbach
// Description:			Abstract graphics driver class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GRAPHICS_GRAPHICSDRIVER_HPP_
#define BLITZPROG_GRAPHICS_GRAPHICSDRIVER_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/GUI/GUI.hpp>
#include <Blitzprog/Graphics/Object3D/Object3D.hpp>
#include <Blitzprog/Collection/Array/Array.hpp>
#include <Blitzprog/FileSystem/FileSystem.hpp>
#include <Blitzprog/Pixmap/Pixmap.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//RGB -> float
#define RGB_BYTE_TO_FLOAT 0.003921568627450980392156862745098f
#define RGB_FLOAT_TO_BYTE 255
#define RGBByteToFloat(x) (x * RGB_BYTE_TO_FLOAT)
#define RGBFloatToByte(x) static_cast<int>(x * RGB_FLOAT_TO_BYTE)	//TODO: Maybe you can multiply this with 256 (faster)

//Default
#define defaultFOVAngle 45
#define defaultCameraNear 0.1f
#define defaultCameraFar 1000.0f

//Graphics flags
#define GRAPHICS_FULLSCREEN 1
#define GRAPHICS_ANTIALIAS 2
#define GRAPHICS_STENCILBUFFER 4
#define GRAPHICS_NOVSYNC 8
#define GRAPHICS_32BIT 16
#define GRAPHICS_DIRECT3D9 64
#define GRAPHICS_DIRECT3D10 128
#define GRAPHICS_OPENGL 256

//Other settings
#define STDVECTOR_USE_ITERATORS 1

//RenderMode
enum RenderMode
{
	RENDERMODE_NORMAL = 0x0004,		//GL_TRIANGLES,
	RENDERMODE_FLAT = 0x1D00,		//GL_FLAT,
	RENDERMODE_LINES = 0x0001,		//GL_LINES,
	RENDERMODE_POINTS =	0x0000		//GL_POINTS
};

//Shorter version
#define cg TGraphicsDriver::currentGraphicsDriver

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

struct TVertex;
class TVertexBuffer;
class TSurface;
class TMesh;
class TEntity;
class TCamera;
class TGraphicsDriver;

//Color
template <typename T=byte>
class TColor
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TColor() : r(0), g(0), b(0), a(0)
		{
			//Debug info
			EngineLogNew("Color: 0, 0, 0, 0");
		}
		
		//Constructor
		TColor(T alpha, T red, T green, T blue) : r(red), g(green), b(blue), a(alpha)
		{
			//Debug info
			EngineLogNew("Color: " << static_cast<int>(a) << ", " << static_cast<int>(r) << ", " << static_cast<int>(g) << ", " << static_cast<int>(b));
		}
		
		//Destructor
		~TColor()
		{
			//Debug info
			EngineLogDelete("Color: " << static_cast<int>(a) << ", " << static_cast<int>(r) << ", " << static_cast<int>(g) << ", " << static_cast<int>(b));
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: int
		operator int()
		{
			return a << 24 | r << 16 | g << 8 | b;	//ARGB
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//SetComponents
		inline void SetComponents(T red, T green, T blue, T alpha)
		{
			r = red;
			g = green;
			b = blue;
			a = alpha;
		}
		
		//SetComponents
		inline void SetComponents(T red, T green, T blue)
		{
			r = red;
			g = green;
			b = blue;
		}
		
		//SetAlpha
		inline void SetAlpha(T alpha)
		{
			a = alpha;
		}
		
		//GetAlpha
		inline T GetAlpha() const
		{
			return a;
		}
		
		//SetRed
		inline void SetRed(T red)
		{
			r = red;
		}
		
		//GetRed
		inline T GetRed() const
		{
			return r;
		}
		
		//SetGreen
		inline void SetGreen(T green)
		{
			g = green;
		}
		
		//GetGreen
		inline T GetGreen() const
		{
			return g;
		}
		
		//SetBlue
		inline void SetBlue(T blue)
		{
			b = blue;
		}
		
		//GetBlue
		inline T GetBlue() const
		{
			return b;
		}
		
		//GetARGB
		inline int GetARGB() const
		{
			return a << 24 | r << 16 | g << 8 | b;	//ARGB
		}
		
		//GetRGBA
		inline int GetRGBA() const
		{
			return r << 24 | g << 16 | b << 8 | a;	//RGBA
		}
		
		//GetRGB
		inline int GetRGB() const
		{
			return r << 16 | g << 8 | b;	//ARGB
		}
		
	public:
		T r;
		T g;
		T b;
		T a;
};
typedef TColor<byte> Color;

//Material
class TMaterial
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TMaterial()
		{
			//Debug info
			EngineLogNew("Material");
		}
		
		//Destructor
		~TMaterial()
		{
			//Debug info
			EngineLogDelete("Material");
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
		
		
		
	protected:
		Color alpha;
};
typedef SharedPtr<TMaterial> Material;
#define CreateMaterial new TMaterial

//Vertex
struct TVertex
{
	public:
		//Position
		Vector3D position;
		
		//Color
		float r, g, b, a;
		
		//Constructor
		TVertex(float x = 0.0f, float y = 0.0f, float z = 0.0f,
				float red = 1.0f, float green = 1.0f, float blue = 1.0f, float alpha = 1.0f)
				:
				position(x, y, z),
				r(red), g(green), b(blue), a(alpha)
		{
			
		}
};
typedef TVertex Vertex;

//CreateVertexBuffer
#define CreateVertex new TVertex

//VertexBuffer
class TVertexBuffer: public TPrintable
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TVertexBuffer() : localBuffer(Null), vertexCount(0)
		{
			//Debug info
			EngineLogNew("VertexBuffer");
		}
		
		//Constructor
		TVertexBuffer(TVertexBuffer &buffer) : localBuffer(buffer.localBuffer), vertexCount(buffer.vertexCount)
		{
			//Debug info
			EngineLogNew("VertexBuffer");
		}
		
		//Constructor
		TVertexBuffer(TVertex *vertexArray, int countVertices) : localBuffer(vertexArray), vertexCount(countVertices)
		{
			//Debug info
			EngineLogNew("VertexBuffer");
		}
		
		//Destructor
		~TVertexBuffer()
		{
			//Debug info
			EngineLogDelete("VertexBuffer");
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
		
		//ToString
		inline String ToString() const
		{
			String tmp;
			for(int i=0; i < vertexCount; ++i)
			{
				tmp += "(" + localBuffer[i].position.ToString() + "), ";
			}
			return tmp;
		}
		
	//protected:
		TVertex *localBuffer;		//Local buffer
		int vertexCount;
};
typedef SharedPtr<TVertexBuffer> VertexBuffer;
#define CreateVertexBuffer new TVertexBuffer

//TODO: IndexBuffer

//CreateIndexBuffer
#define CreateIndexBuffer new TIndexBuffer

//Surface
class TSurface
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TSurface()
		{
			//Debug info
			EngineLogNew("Surface");
		}
		
		//Constructor (VertexBuffer)
		TSurface(TVertexBuffer &buffer) : vertexBuffer(buffer)
		{
			//Debug info
			EngineLogNew("Surface");
		}
		
		//Destructor
		~TSurface()
		{
			//Debug info
			EngineLogDelete("Surface");
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
		
		
		
	//protected:
		TVertexBuffer vertexBuffer;
		//TIndexBuffer indexBuffer;
};
typedef SharedPtr<TSurface> Surface;
#define CreateSurface new TSurface

//Mesh
class TMesh
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TMesh()
		{
			//Debug info
			EngineLogNew("Mesh");
		}
		
		//Constructor
		TMesh(String &meshFileName) : fileName(meshFileName)
		{
			//Debug info
			EngineLogNew("Mesh");
		}
		
		//Destructor
		~TMesh()
		{
			//Debug info
			EngineLogDelete("Mesh");
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
		
		
		
	//protected:
		vector<TSurface*> surfaceList;
		String fileName;
};
typedef SharedPtr<TMesh> Mesh;
#define CreateMesh new TMesh

//Entity
class TEntity: public TObject3D//, public TPrintable
{
	public:
		
		//Public static vars
		static TEntity *Root;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TEntity() : mesh(Null), name(""), visible(false), culling(1), lighting(1), parent(Root)
		{
			//Debug info
			EngineLogNew("Entity");
		}
		
		//Copy Constructor
		TEntity(TEntity *nParent) : mesh(Null), name(""), visible(false), culling(1), lighting(1), parent(nParent)
		{
			//Debug info
			EngineLogNew("Entity");
			
			//Add to list
			AddToList();
		}
		
		//Copy Constructor
		TEntity(TEntity *nParent, String objectName) : mesh(Null), name(objectName), visible(false), culling(1), lighting(1), parent(nParent)
		{
			//Debug info
			EngineLogNew("Entity");
			
			//Add to list
			AddToList();
		}
		
		//Constructor (String)
		TEntity(String fileName) : mesh(new TMesh(fileName)), name(""), visible(false), parent(Root)
		{
			//Debug info
			EngineLogNew("Entity: " << fileName);
			
			//Load mesh
			LoadMesh(fileName);
		}
		
		//Destructor
		~TEntity()
		{
			//Debug info
			EngineLogDelete("Entity");
			
			//TODO: Remove from list
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast (Mesh)
		operator Mesh()
		{
			return mesh;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//LoadMesh
		inline void LoadMesh(String fileName)
		{
			//Load mesh
			TFileReadStream stream(fileName);
			int count;
			//TODO: Read
			//stream.Read(count);
			TVertex *vertexArray = new TVertex[count];
			//stream.ReadArray(vertexArray, count);
			stream.Close();
			
			//Create surfaces
			TVertexBuffer buffer(vertexArray, count);
			mesh = new TMesh(fileName);
			mesh->surfaceList.push_back(new TSurface(buffer));
			
			//Add to list
			if(!visible)
			{
				AddToList();
				visible = true;
			}
		}
		
		//CopyEntity
		inline void CopyEntity(TEntity *ent)
		{
			//Remove from list
			if(visible)
				RemoveFromList();
			
			position = ent->GetPosition();
			rotation = ent->GetRotation();
			scaling = ent->GetScaling();
			viewDirection = ent->GetViewDirection();
			upVector = ent->GetUpVector();
			rightVector = ent->GetRightVector();
			mesh = ent->GetMesh();
			name = ent->GetName();	//Root->childList.size();
			visible = ent->IsVisible();
			culling = ent->CullingIsEnabled();
			lighting = ent->LightingIsEnabled();
			parent = ent->GetParent();
			
			//Add to list (if the copied entity was visible)
			if(visible)
				AddToList();
		}
		
		//Show
		inline void Show()
		{
			if(!visible)
			{
				AddToList();
				visible = true;
			}
		}
		
		//Show
		inline void Show(bool show)
		{
			if(show && !visible)
			{
				AddToList();
				visible = true;
			}
			else if(!show && visible)	//TODO: Can this be optimized?
			{
				RemoveFromList();
				visible = false;
			}
		}
		
		//Hide
		inline void Hide()
		{
			if(visible)
			{
				RemoveFromList();
				visible = false;
			}
		}
		
		//IsVisible
		inline bool IsVisible() const
		{
			return visible;
		}
		
		//CullingIsEnabled
		inline bool CullingIsEnabled() const
		{
			return culling;
		}
		
		//LightingIsEnabled
		inline bool LightingIsEnabled() const
		{
			return lighting;
		}
		
		//SetCulling
		inline void SetCulling(bool enabled)
		{
			culling = enabled;
		}
		
		//SetLighting
		inline void SetLighting(bool enabled)
		{
			lighting = enabled;
		}
		
		//SetName
		inline void SetName(String nName)
		{
			name = nName;
		}
		
		//GetName
		inline String &GetName()
		{
			return name;
		}
		
		//SetParent
		inline void SetParent(TEntity *nEntity)
		{
			if(nEntity == Null)
				nEntity = TEntity::Root;
			
			if(parent == nEntity)
				return;
			
			RemoveFromList();
			parent = nEntity;
			AddToList();
		}
		
		//GetParent
		inline TEntity *GetParent() const
		{
			return parent;
		}
		
		//SetMesh
		inline void SetMesh(Mesh nMesh)
		{
			mesh = nMesh;
		}
		
		//GetMesh
		inline Mesh GetMesh() const
		{
			return mesh;
		}
		
		//ToString
		inline String ToString() const
		{
			return name;
		}
		
		//GetChildListAsCPPVector
		inline vector<TEntity*> &GetChildListAsCPPVector()
		{
			return childList;
		}
		
	protected:
		Mesh mesh;
		String name;
		bool visible;
		bool culling;
		bool lighting;
		//EntityClass entityClass;
		vector<TEntity*> childList;
		TEntity *parent;
		
		//AddToList
		inline void AddToList()
		{
			if(parent)
				parent->childList.push_back(this);
		}
		
		//RemoveFromList
		inline void RemoveFromList()
		{
			if(parent)
				parent->childList.erase(find(parent->childList.begin(), parent->childList.end(), this));
		}
};
typedef SharedPtr<TEntity> Entity;
#define CreateEntity new TEntity

//Static vars
#ifndef BLITZPROG_LIB
	TEntity *TEntity::Root = CreateEntity(Null, "Root");
#endif

//DeleteRootEntity
inline void DeleteRootEntity()
{
	delete TEntity::Root;
}

//Camera
class TCamera: public TObject3D
{
	public:
		
		//Public static vars
		static vector<TCamera*> List;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TCamera()
		{
			//Debug info
			EngineLogNew("Camera");
			
			//Add to list
			List.push_back(this);
		}
		
		//Destructor
		~TCamera()
		{
			//Debug info
			EngineLogDelete("Camera");
			
			//TODO: Remove from list
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
		
		//TODO: Zoom functions
		
	protected:
		Rect viewport;	//TODO: Use viewport (glScissor)
};
typedef SharedPtr<TCamera> Camera;
#define CreateCamera new TCamera

//Static vars
#ifndef BLITZPROG_LIB
	vector<TCamera*> TCamera::List;
#endif

//Texture
class TTexture
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TTexture() : width(0), height(0), handleXY(0, 0)
		{
			//Debug info
			EngineLogNew("Texture");
		}
		
		//Destructor
		virtual ~TTexture()
		{
			//Debug info
			EngineLogDelete("Texture");
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
		virtual bool Load(Pixmap pixmap) = 0;
		
		//Draw
		virtual void Draw(	int x, int y, int frame,
							float z, int r, int g, int b, int a,
							float rotationZ, float scalingX, float scalingY) = 0;
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//SetHandle
		inline void SetHandle(int xPos, int yPos)
		{
			handleXY.x = xPos;
			handleXY.y = yPos;
		}
		
		//SetMidHandle
		inline void SetMidHandle()
		{
			SetHandle(width / 2, height / 2);
		}
		
		//GetWidth
		inline int GetWidth() const
		{
			return width;
		}
		
		//GetHeight
		inline int GetHeight() const
		{
			return height;
		}
		
	protected:
		int width;
		int height;
		Point handleXY;
};
typedef SharedPtr<TTexture> Texture;
typedef Texture Image;

//GraphicsDriver
class TGraphicsDriver
{
	public:
		
		//Public static vars
		static TGraphicsDriver *currentGraphicsDriver;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TGraphicsDriver(Window win, int flags=0) :	window(win),
													viewport(),
													initialized(false),
													fullscreen(flags & GRAPHICS_FULLSCREEN),
													antiAlias(flags & GRAPHICS_ANTIALIAS),
													force32Bit(flags & GRAPHICS_32BIT),
													stencilBuffer(flags & GRAPHICS_STENCILBUFFER),
													vsync(!(flags & GRAPHICS_NOVSYNC)),
													culling(1),
													lighting(1),
													trisRendered(0),
													currentRenderMode(RENDERMODE_NORMAL)
		{
			//Debug info
			EngineLogNew("GraphicsDriver");
		}
		
		//Destructor
		virtual ~TGraphicsDriver()
		{
			//Debug info
			EngineLogDelete("GraphicsDriver");
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
		
		//Set2D
		virtual void Set2D() = 0;
		
		//Set3D
		virtual void Set3D(float fovAngle = defaultFOVAngle, float zNear = defaultCameraNear, float zFar = defaultCameraFar) = 0;
		
		//Cls
		virtual void Cls() = 0;
		
		//Flip
		virtual void Flip() = 0;
		
		//DrawEntity
		virtual void DrawEntity(TEntity *entity) = 0;
		
		//DrawSurface
		virtual void DrawSurface(TSurface *surface) = 0;
		
		//DrawPixel
		virtual void DrawPixel(int x, int y) = 0;
		
		//DrawLine
		virtual void DrawLine(int x, int y, int toX, int toY) = 0;
		
		//DrawRect
		virtual void DrawRect(int x, int y, int width, int height) = 0;
		
		//DrawPixmap
		virtual void DrawPixmap(Pixmap pixmap, int x, int y, int frame=0) = 0;
		
		//DrawImage
		virtual void DrawImage(Image img, int x, int y, int frame=0) = 0;
		
		//RenderWorld
		virtual void RenderWorld() = 0;
		
		//SetClsColor
		virtual void SetClsColor(int red, int green, int blue, int alpha=0) = 0;
		
		//SetClsColorFloat
		virtual void SetClsColorFloat(float red, float green, float blue, float alpha=0.0f) = 0;
		
		//SetColor
		virtual void SetColor(int red, int green, int blue) = 0;
		
		//SetColor
		virtual void SetColor(int red, int green, int blue, int alpha) = 0;
		
		//SetColorFloat
		virtual void SetColorFloat(float red, float green, float blue) = 0;
		
		//SetColorFloat
		virtual void SetColorFloat(float red, float green, float blue, float alpha) = 0;
		
		//SetRenderMode
		virtual void SetRenderMode(RenderMode mode) = 0;
		
		//SetViewport
		virtual void SetViewport(int x, int y, int width, int height) = 0;
		
		//SetRotation
		virtual void SetRotation(float zRotation) = 0;
		
		//SetScale
		virtual void SetScale(float xScale, float yScale) = 0;
		
		//LoadTexture
		virtual Texture LoadTexture(Pixmap pixmap) const = 0;
		
		//Activate
		virtual void Activate() = 0;
		
		//GetDriverName
		virtual String GetDriverName() const = 0;
		
		//GetDriverVersion
		virtual String GetDriverVersion() const = 0;
		
		//TODO: Add culling/lighting state methods
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//InitializationFailed
		inline bool InitializationFailed() const { return !initialized; };
		
		//GraphicsWidth
		inline int GetGraphicsWidth() const
		{
			return viewport.width;
		}
		
		//GraphicsHeight
		inline int GetGraphicsHeight() const
		{
			return viewport.height;
		}
		
		//GetTrisRendered
		inline int GetTrisRendered() const
		{
			return trisRendered;
		}
		
		friend inline Window GraphicsWindow();
		friend inline int MouseX();
		friend inline int MouseY();
		
	protected:
		Window window;
		Rect viewport;
		bool initialized;
		bool fullscreen;
		bool antiAlias;
		bool force32Bit;
		bool stencilBuffer;
		bool vsync;
		bool culling;
		bool lighting;
		int trisRendered;
		RenderMode currentRenderMode;
		
		//TODO: Add color depth get method
		//int colorDepth;
};

//Static vars
#ifndef BLITZPROG_LIB
	TGraphicsDriver *TGraphicsDriver::currentGraphicsDriver = Null;
#endif

//GraphicsDriverFactory
class TGraphicsDriverFactory
{
	public:
		
		//Public static vars
		static TArray<TGraphicsDriverFactory *> ObjectArray;
		
		//Constructor
		TGraphicsDriverFactory()
		{
			//Debug info
			EngineLogNew("GraphicsDriverFactory");
			
			//Add to list
			TGraphicsDriverFactory::ObjectArray.Add(this);
		}
		
		//Destructor
		virtual ~TGraphicsDriverFactory()
		{
			
		}
		
		//CreateGraphicsDriver
		virtual TGraphicsDriver *CreateGraphicsDriver(Window win, int flags=0) = 0;
};

//Static vars
#ifndef BLITZPROG_LIB
	TArray<TGraphicsDriverFactory*> TGraphicsDriverFactory::ObjectArray;
#endif

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////

//GFXStartUp
class GFXStartUp
{
	public:
		GFXStartUp()
		{
			OnEnd(DeleteRootEntity);
		}
};

#ifndef BLITZPROG_LIB
	static GFXStartUp GFXStartUpObject;
#endif

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif // BLITZPROG_GRAPHICS_GRAPHICSDRIVER_HPP_

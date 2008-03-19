////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Pixmap
// Author:				Eduard Urbach
// Description:			Class for bitmaps
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_PIXMAP_HPP_
#define BLITZPROG_PIXMAP_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/FileSystem/FileSystem.hpp>

//DevIL
#include <IL/il.h>
#include <IL/ilu.h>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Post- or Pre-Increment?
#define PIXMAP_USE_POST_INCREMENT 0

//PixmapFormat
enum PixmapFormat
{
	PIXMAPFORMAT_RGBA = 0,
	PIXMAPFORMAT_BGRA = 1,
	PIXMAPFORMAT_RGB = 2,
	PIXMAPFORMAT_A = 3
};

//SetPixmapPtrFastRGB
#define SetPixmapPtrFastRGB(aPixelPtr, r, g, b) *++aPixelPtr = r; *++aPixelPtr = g; *++aPixelPtr = b

//BytesPerPixel
static const int BytesPerPixel[] =	{
										4,	//PIXMAPFORMAT_RGBA
										4,	//PIXMAPFORMAT_BGRA
										3,	//PIXMAPFORMAT_RGB
										1	//PIXMAPFORMAT_A
									};

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Pixmap
class TPixmap
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//TODO: Remove constructor and add LoadImage
		
		//Constructor
		TPixmap(const String &imageFileName) : handle(0)
		{
			//Debug info
			EngineLogNew("Pixmap: " << imageFileName);
			
			//Generate image
			ilGenImages(1, &handle);
			
			//Load file
			Load(imageFileName);
		}
		
		//Constructor
		TPixmap(int nWidth, int nHeight) : handle(0)
		{
			//Debug info
			EngineLogNew("Pixmap: " << nWidth << ", " << nHeight);
			
			//Generate image
			ilGenImages(1, &handle);
			
			//TODO: Create image
		}
		
		//Destructor
		~TPixmap()
		{
			//Debug info
			EngineLogDelete("Pixmap: " << handle << " -> " << size.x << ", " << size.y << " [" << fileName << "]");
			
			//Delete image
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
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Destroy
		inline void Destroy()
		{
			if(handle)
			{
				ilDeleteImages(1, &handle);
				handle = 0;
			}
		}
		
		//GetData
		inline byte *GetData()
		{
			return data;
		}
		
		//GetSize
		inline Vector2D GetSize()
		{
			return size;
		}
		
		//GetWidth
		inline int GetWidth()
		{
			return size.x;
		}
		
		//GetHeight
		inline int GetHeight()
		{
			return size.y;
		}
		
		//GetFormat
		inline int GetFormat()
		{
			return format;
		}
		
		//GetSizeInBytes
		inline int GetSizeInBytes()
		{
			return sizeInBytes;
		}
		
		//GetBytesPerPixel
		inline int GetBytesPerPixel()
		{
			return bytesPerPixel;
		}
		
		//SetPixel
		inline void SetPixel(int x, int y, byte red, byte green, byte blue, byte alpha=255)
		{
			//TODO: Implement this
		}
		
		//SetPixel
		inline void SetPixel(int x, int y, int argb)
		{
			SetPixel(x, y, argb >> 16, argb >> 8, argb, argb >> 24);
		}
		
		//GetPixel
		inline int GetPixel(int x, int y)
		{
			//TODO: Implement this
			return 0;
		}
		
		//Clear
		inline void Clear(byte uniform = 0)
		{
			//TODO: Are there some exceptions for other formats?
			MemSet(data, uniform, GetSizeInBytes());
		}
		
		//Fill
		inline void Fill(byte red, byte green, byte blue, byte alpha=255)	//TODO: Int?
		{
			//TODO: Implement this
		}
		
		//Fill
		inline void Fill(int argb)
		{
			Fill(argb >> 16, argb >> 8, argb, argb >> 24);
		}
		
		//PixelPtrAt
		inline byte *PixelPtrAt(int x, int y)
		{
			return data + y * bytesPerRow + x * ilGetInteger(IL_IMAGE_BPP);
		}
		
		//Load
		inline bool Load(const String &imageFileName)
		{
			//Destroy old image
			Destroy();
			
			//Bind
			ilBindImage(handle);
			
			//Load image
			if(!ilLoadImage(const_cast<char*>(imageFileName.ToCharString())))
			{
				EngineLogError("Can't load pixmap: " << imageFileName << " -> " << iluErrorString(ilGetError()));
				return false;
			}
			EngineLog4("Pixmap loaded: " << imageFileName);
			
			//Set file name
			fileName = imageFileName;
			
			//Get information
			data = ilGetData();
			size.x = ilGetInteger(IL_IMAGE_WIDTH);
			size.y = ilGetInteger(IL_IMAGE_HEIGHT);
			format = ilGetInteger(IL_IMAGE_FORMAT);
			bytesPerPixel = ilGetInteger(IL_IMAGE_BPP);
			bytesPerRow = size.x * bytesPerPixel;
			sizeInBytes = size.x * size.y * bytesPerPixel;
			
			//Everything ok
			return true;
		}
		
		//Save
		inline bool Save(const String &imageFileName) const
		{
			//Bind
			ilBindImage(handle);
			
			//Delete file if it exists
			if(FileExists(imageFileName))
			{
				DeleteFile(imageFileName);
			}
			
			//Save image
			if(!ilSaveImage(const_cast<char*>(imageFileName.ToCharString())))
			{
				EngineLogError("Can't save pixmap: " << imageFileName << " -> " << iluErrorString(ilGetError()));
				return false;
			}
			EngineLog4("Pixmap saved: " << imageFileName);
			
			//Everything ok
			return true;
		}
		
		//Public pointer
		byte *currentPixelPtr;
		
	protected:
		byte *data;
		ILuint handle;
		Vector2D size;
		int bytesPerPixel;
		int bytesPerRow;
		int sizeInBytes;
		int format;
		String fileName;
};
typedef SharedPtr<TPixmap> Pixmap;
#define CreatePixmap new TPixmap

//PixmapStartUp
class PixmapStartUp
{
	public:
		//Constructor
		PixmapStartUp()
		{
			//Initialize IL
			ilInit();
			iluInit();
			
			//Check version
			if(ilGetInteger(IL_VERSION_NUM) < IL_VERSION || iluGetInteger(ILU_VERSION_NUM) < ILU_VERSION)
			{
				EngineLogError("Incompatible DevIL version.");
			}
		}
};

//Static vars
#ifndef BLITZPROG_LIB
	static PixmapStartUp PixmapStartUpObject;
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



#endif /*BLITZPROG_PIXMAP_HPP_*/

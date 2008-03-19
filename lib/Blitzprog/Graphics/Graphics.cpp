#include "Graphics.hpp"

//Constructor
TGraphics::TGraphics(Window win, int flags) : TGraphicsDriver(win, flags)
{
	//Debug info
	EngineLogNew("Graphics");
	
	//Preferred driver
	if(flags & GRAPHICS_OPENGL)
	{
		driver = new TOpenGL(win, flags);
	}
#ifdef WIN32
	else if(flags & GRAPHICS_DIRECT3D9)
	{
		driver = new TDirect3D9(win, flags);
	}
#endif
	else	//Try out every driver
	{
		//Debug info
		EngineLog2("Trying to find a graphics driver (" << TGraphicsDriverFactory::ObjectArray.GetSize() << " to check)");
		
		TGraphicsDriverFactory *currentFactory;
		
		for(size_t i=0; i < TGraphicsDriverFactory::ObjectArray.GetSize(); ++i)
		{
			currentFactory = TGraphicsDriverFactory::ObjectArray[i];
			driver = currentFactory->CreateGraphicsDriver(win, flags);
			
			if(driver->InitializationFailed())
			{
				//Debug info
				EngineLogError(driver->GetDriverName() << " initialization failed");
				
				//Delete the previously created object
				delete driver;
				driver = Null;
				
				continue;
			}
			else
			{
				break;
			}
		}
		
		//If nothing works, take the null device
		if(driver == Null)
		{
			//TODO: 
			//driver = new TNullDevice(win, flags);
		}
	}
	
	//This becomes the active graphics object
	cg = driver;
}

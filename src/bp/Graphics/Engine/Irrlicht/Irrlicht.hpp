#include "irrlicht/irrlicht.h"

using namespace irr;
using namespace core;
using namespace scene;
using namespace video;
using namespace io;
using namespace gui;

// Typedefs
#define BPIrrlichtDevice IrrlichtDevice

// Global
IrrlichtDevice *irrDevice;
IVideoDriver* irrDriver;
ISceneManager* irrSmgr;
IGUIEnvironment* irrGuienv;

inline void bp_cls() {
	irrDriver->beginScene(true, true, SColor(255, 0, 0, 0));
}

inline void bp_flip() {
	irrSmgr->drawAll();
	irrGuienv->drawAll();
	
	irrDriver->endScene();
}

inline void bp_closeGraphicsWindow() {
	irrDevice->drop();
}

inline IrrlichtDevice* bp_createIrrDevice(char* title, int width, int height, int depth, bool fullscreen) {
	irrDevice = createDevice(EDT_OPENGL, dimension2d<u32>(width, height), depth, fullscreen, false, false, 0);
	
	stringw titleWstr(title);
	irrDevice->setWindowCaption(titleWstr.c_str());
	
	irrDriver = irrDevice->getVideoDriver();
	irrSmgr = irrDevice->getSceneManager();
	irrGuienv = irrDevice->getGUIEnvironment();
	
	//irrGuienv->addStaticText(L"OpenGL", rect<int>(10,10,200,22), true);
	
	irrSmgr->addCameraSceneNode(0, vector3df(0,30,-40), vector3df(0,5,0));
	
	return irrDevice;
	
	/*while(bp_appRunning())
	{
		bp_cls();
		
		bp_flip();
	}
	
	bp_closeGraphicsWindow();*/
}


























































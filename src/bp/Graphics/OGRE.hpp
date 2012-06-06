#include <OGRE/OgreRoot.h>
#include <OGRE/OgreCamera.h>
#include <OGRE/OgreSceneManager.h>
#include <OGRE/OgreRenderWindow.h>

#include <OGRE/OgreLogManager.h>
#include <OGRE/OgreViewport.h>
#include <OGRE/OgreEntity.h>
#include <OGRE/OgreWindowEventUtilities.h>
#include <OGRE/OgrePlugin.h>

class LowLevelOgre
{
public:
    LowLevelOgre(void);
    virtual ~LowLevelOgre(void);
    bool go(void);
protected:
    Ogre::Root *mRoot;
    Ogre::Camera* mCamera;
    Ogre::SceneManager* mSceneMgr;
    Ogre::RenderWindow* mWindow;
};

//-------------------------------------------------------------------------------------
LowLevelOgre::LowLevelOgre(void)
    : mRoot(0),
    mCamera(0),
    mSceneMgr(0),
    mWindow(0)
{
}
//-------------------------------------------------------------------------------------
LowLevelOgre::~LowLevelOgre(void)
{
    delete mRoot;
}

bool LowLevelOgre::go(void)
{
    // construct Ogre::Root : no plugins filename, no config filename, using a custom log filename
    mRoot = new Ogre::Root("", "", "LowLevelOgre.log");
	
    // A list of required plugins
    Ogre::StringVector required_plugins;
    required_plugins.push_back("GL RenderSystem");
    required_plugins.push_back("Octree & Terrain Scene Manager");

    // List of plugins to load
    Ogre::StringVector plugins_toLoad;
    plugins_toLoad.push_back("RenderSystem_GL");
    plugins_toLoad.push_back("Plugin_OctreeSceneManager");
	
    // Load the OpenGL RenderSystem and the Octree SceneManager plugins
    for (Ogre::StringVector::iterator j = plugins_toLoad.begin(); j != plugins_toLoad.end(); j++)
    {
#ifdef _DEBUG
        mRoot->loadPlugin(*j + Ogre::String("_d"));
#else
        mRoot->loadPlugin(*j);
#endif;
    }
	
    // Check if the required plugins are installed and ready for use
    // If not: exit the application
    Ogre::Root::PluginInstanceList ip = mRoot->getInstalledPlugins();
    for (Ogre::StringVector::iterator j = required_plugins.begin(); j != required_plugins.end(); j++)
    {
        bool found = false;
        // try to find the required plugin in the current installed plugins
        for (Ogre::Root::PluginInstanceList::iterator k = ip.begin(); k != ip.end(); k++)
        {
            if ((*k)->getName() == *j)
            {
                found = true;
                break;
            }
        }
        if (!found)  // return false because a required plugin is not available
        {
            return false;
        }
    }

//-------------------------------------------------------------------------------------
    // setup resources
    // Only add the minimally required resource locations to load up the Ogre head mesh
    Ogre::ResourceGroupManager::getSingleton().addResourceLocation("../../media/materials/programs", "FileSystem", "General");
    Ogre::ResourceGroupManager::getSingleton().addResourceLocation("../../media/materials/scripts", "FileSystem", "General");
    Ogre::ResourceGroupManager::getSingleton().addResourceLocation("../../media/materials/textures", "FileSystem", "General");
    Ogre::ResourceGroupManager::getSingleton().addResourceLocation("../../media/models", "FileSystem", "General");

//-------------------------------------------------------------------------------------
    // configure
    // Grab the OpenGL RenderSystem, or exit
    Ogre::RenderSystem* rs = mRoot->getRenderSystemByName("OpenGL Rendering Subsystem");
    if(!(rs->getName() == "OpenGL Rendering Subsystem"))
    {
        return false; //No RenderSystem found
    }
    // configure our RenderSystem
    rs->setConfigOption("Full Screen", "No");
    rs->setConfigOption("VSync", "No");
    rs->setConfigOption("Video Mode", "800 x 600 @ 32-bit");

    mRoot->setRenderSystem(rs);

    mWindow = mRoot->initialise(true, "LowLevelOgre Render Window");
//-------------------------------------------------------------------------------------
    // choose scenemanager
    // Get the SceneManager, in this case the OctreeSceneManager
    mSceneMgr = mRoot->createSceneManager("OctreeSceneManager", "DefaultSceneManager");
//-------------------------------------------------------------------------------------
    // create camera
    // Create the camera
    mCamera = mSceneMgr->createCamera("PlayerCam");

    // Position it at 500 in Z direction
    mCamera->setPosition(Ogre::Vector3(0,0,80));
    // Look back along -Z
    mCamera->lookAt(Ogre::Vector3(0,0,-300));
    mCamera->setNearClipDistance(5);

//-------------------------------------------------------------------------------------
    // create viewports
    // Create one viewport, entire window
    Ogre::Viewport* vp = mWindow->addViewport(mCamera);
    vp->setBackgroundColour(Ogre::ColourValue(0,0,0));

    // Alter the camera aspect ratio to match the viewport
    mCamera->setAspectRatio(
        Ogre::Real(vp->getActualWidth()) / Ogre::Real(vp->getActualHeight()));
//-------------------------------------------------------------------------------------
    // Set default mipmap level (NB some APIs ignore this)
    Ogre::TextureManager::getSingleton().setDefaultNumMipmaps(5);
//-------------------------------------------------------------------------------------
    // Create any resource listeners (for loading screens)
    //createResourceListener();
//-------------------------------------------------------------------------------------
    // load resources
    Ogre::ResourceGroupManager::getSingleton().initialiseAllResourceGroups();
//-------------------------------------------------------------------------------------
    // Create the scene
    Ogre::Entity* ogreHead = mSceneMgr->createEntity("Head", "ogrehead.mesh");

    Ogre::SceneNode* headNode = mSceneMgr->getRootSceneNode()->createChildSceneNode();
    headNode->attachObject(ogreHead);

    // Set ambient light
    mSceneMgr->setAmbientLight(Ogre::ColourValue(0.5, 0.5, 0.5));

    // Create a light
    Ogre::Light* l = mSceneMgr->createLight("MainLight");
    l->setPosition(20,80,50);
//-------------------------------------------------------------------------------------

    //mRoot->startRendering();
    while(true)
    {
        // Pump window messages for nice behaviour
        Ogre::WindowEventUtilities::messagePump();

        // Render a frame
        mRoot->renderOneFrame();

        if(mWindow->isClosed())
        {
            return false;
        }
    }

    // We should never be able to reach this corner
    // but return true to calm down our compiler
    return true;
}

inline void bp_ogreHelloWorld() {
	std::cout << "Running!" << std::endl;
	
	LowLevelOgre app;
	
	try {
		app.go();
	} catch(Ogre::Exception& e) {
		std::cerr << "An exception has occured: " << e.getFullDescription().c_str() << std::endl;
	}
}
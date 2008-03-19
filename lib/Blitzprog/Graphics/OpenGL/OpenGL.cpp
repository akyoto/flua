#include "OpenGL.hpp"

//Constructor
TOpenGL::TOpenGL(Window win, int flags) : TGraphicsDriver(win, flags), ct(Null), dr(Null), rotationZ(0.0f), scalingX(1.0f), scalingY(1.0f), handleXY(0, 0)
{
	//Debug info
	EngineLogNew("OpenGL");
	
	//Increment counter
	graphicsContextCount++;
	
#ifdef WIN32
	
	//Format
	int iFormat;
	
	//Set the pixel format for the DC
	PIXELFORMATDESCRIPTOR pfd[4] =
	{
		//#1
		{
		sizeof(pfd),						//pfd.nSize = Size of the struct
		1,									//pfd.nVersion = Version
		PFD_DRAW_TO_WINDOW | 				//pfd.dwFlags = PFD_DRAW_TO_WINDOW	(draw on a window)
		PFD_SUPPORT_OPENGL | 				//				PFD_SUPPORT_OPENGL	(has to support OpenGL)
		PFD_DOUBLEBUFFER,					//				PFD_DOUBLEBUFFER	(double-buffering)
		PFD_TYPE_RGBA,						//pfd.iPixelType = RGBA backbuffer format
		force32Bit ? 32 : 16,				//pfd.cColorBits = Color depth
		0, 0, 0, 0, 0, 0,					//Color bits
		0,									//Alpha buffer
		0,									//Shift bit
		0,									//Accumulation buffer
		0, 0, 0, 0,							//Accumulation bits
		24,									//pfd.cDepthBits = Z/Depth buffer
		stencilBuffer,						//Stencil buffer
		0,									//Auxiliary buffer
		PFD_MAIN_PLANE,						//pfd.iLayerType = Drawing layer
		0,									//Reserved
		0, 0, 0								//Layer masks
		},
		
		//#2
		{
		sizeof(pfd),						//pfd.nSize = Size of the struct
		1,									//pfd.nVersion = Version
		PFD_DRAW_TO_WINDOW | 				//pfd.dwFlags = PFD_DRAW_TO_WINDOW	(draw on a window)
		PFD_SUPPORT_OPENGL | 				//				PFD_SUPPORT_OPENGL	(has to support OpenGL)
		PFD_DOUBLEBUFFER,					//				PFD_DOUBLEBUFFER	(double-buffering)
		PFD_TYPE_RGBA,						//pfd.iPixelType = RGBA backbuffer format
		force32Bit ? 32 : 16,				//pfd.cColorBits = Color depth
		0, 0, 0, 0, 0, 0,					//Color bits
		0,									//Alpha buffer
		0,									//Shift bit
		0,									//Accumulation buffer
		0, 0, 0, 0,							//Accumulation bits
		16,									//pfd.cDepthBits = Z/Depth buffer
		stencilBuffer,						//Stencil buffer
		0,									//Auxiliary buffer
		PFD_MAIN_PLANE,						//pfd.iLayerType = Drawing layer
		0,									//Reserved
		0, 0, 0								//Layer masks
		},
		
		//#3
		{
		sizeof(pfd),						//pfd.nSize = Size of the struct
		1,									//pfd.nVersion = Version
		PFD_DRAW_TO_WINDOW | 				//pfd.dwFlags = PFD_DRAW_TO_WINDOW	(draw on a window)
		PFD_SUPPORT_OPENGL | 				//				PFD_SUPPORT_OPENGL	(has to support OpenGL)
		PFD_DOUBLEBUFFER,					//				PFD_DOUBLEBUFFER	(double-buffering)
		PFD_TYPE_RGBA,						//pfd.iPixelType = RGBA backbuffer format
		force32Bit ? 32 : 16,				//pfd.cColorBits = Color depth
		0, 0, 0, 0, 0, 0,					//Color bits
		0,									//Alpha buffer
		0,									//Shift bit
		0,									//Accumulation buffer
		0, 0, 0, 0,							//Accumulation bits
		16,									//pfd.cDepthBits = Z/Depth buffer
		0,									//Stencil buffer
		0,									//Auxiliary buffer
		PFD_MAIN_PLANE,						//pfd.iLayerType = Drawing layer
		0,									//Reserved
		0, 0, 0								//Layer masks
		},
		
		//#4
		{
		sizeof(pfd),						//pfd.nSize = Size of the struct
		1,									//pfd.nVersion = Version
		PFD_DRAW_TO_WINDOW | 				//pfd.dwFlags = PFD_DRAW_TO_WINDOW	(draw on a window)
		PFD_SUPPORT_OPENGL | 				//				PFD_SUPPORT_OPENGL	(has to support OpenGL)
		PFD_DOUBLEBUFFER,					//				PFD_DOUBLEBUFFER	(double-buffering)
		PFD_TYPE_RGBA,						//pfd.iPixelType = RGBA backbuffer format
		16,									//pfd.cColorBits = Color depth
		0, 0, 0, 0, 0, 0,					//Color bits
		0,									//Alpha buffer
		0,									//Shift bit
		0,									//Accumulation buffer
		0, 0, 0, 0,							//Accumulation bits
		16,									//pfd.cDepthBits = Z/Depth buffer
		0,									//Stencil buffer
		0,									//Auxiliary buffer
		PFD_MAIN_PLANE,						//pfd.iLayerType = Drawing layer
		0,									//Reserved
		0, 0, 0								//Layer masks
		},
	};
	
	//DC
	if(!(hDC = win->GetDC()))
	{
		EngineErrorLog("hDC = Null");
		return;
	}
	
	//Test every pixel format
	int i=0;
	for(; i<4; ++i)
	{
		//Debug info
		EngineLogDetailed("Trying to set pixel format #" << i+1);
		
		//Choose a pixel format
		if(!(iFormat = ChoosePixelFormat(hDC, &pfd[i])))
		{
			EngineErrorLog("ChoosePixelFormat failed");
			continue;
		}
		
		//Set pixel format
		if(!SetPixelFormat(hDC, iFormat, &pfd[i]))
		{
			EngineErrorLog("SetPixelFormat failed");
			continue;
		}
		
		break;
	}
	
	//RC
	if(!(hRC = wglCreateContext(hDC)))
	{
		EngineErrorLog("wglCreateContext failed");
		return;
	}
	
	//Activate the RC
	if(!wglMakeCurrent(hDC, hRC))
	{
		EngineErrorLog("wglMakeCurrent failed");
		return;
	}
	
	//Stencil buffer and color depth
	stencilBuffer = stencilBuffer ? i < 3 : 0;
	force32Bit = force32Bit ? i < 4 : 0;
	
#elif defined(LINUX)
	
	//Hide it
	bool wasVisible = false;
	PollSystem();
	Delay(0);
	Rect savedShape = window->GetShape();
	if(wasVisible = window->IsVisible())
	{
		EngineLog4("Window is visible, trying to hide it");
		window->Hide();
	}
	
	GdkGLConfigMode mode = static_cast<GdkGLConfigMode>(GDK_GL_MODE_RGBA | GDK_GL_MODE_ALPHA | GDK_GL_MODE_DOUBLE | GDK_GL_MODE_DEPTH);
	if(stencilBuffer)
		mode = static_cast<GdkGLConfigMode>(mode | GDK_GL_MODE_STENCIL);
	
	gdk_threads_enter();
	gtk_widget_unrealize(window->GetHandle());
	if(!gtk_widget_set_gl_capability(	window->GetHandle(),
										gdk_gl_config_new_by_mode(mode),
										Null,
										true,	//TODO: true or false?
										GDK_GL_RGBA_TYPE))
	{
		EngineLogError("gtk_widget_set_gl_capability");
		return;
	}
	gtk_widget_realize(window->GetHandle());
	
	ct = gtk_widget_create_gl_context(window->GetHandle(), Null, true, GDK_GL_RGBA_TYPE);
	if(!ct)
	{
		EngineLogError("gtk_widget_create_gl_context");
		return;
	}
	
	dr = gtk_widget_get_gl_drawable(window->GetHandle());
	if(!dr)
	{
		EngineLogError("gtk_widget_get_gl_drawable");
		return;
	}
	
	//Fullscreen
	if(fullscreen)
	{
		gtk_window_set_decorated(GTK_WINDOW(window->GetHandle()), false);
		gtk_window_fullscreen(GTK_WINDOW(window->GetHandle()));
	}
	
	gdk_threads_leave();
	
	//Show it again
	if(wasVisible)
	{
		EngineLog4("Showing window again");
		window->Show();
		window->SetShape(savedShape);
	}
	
	Activate();
#endif
	
	//Is this the first OpenGL gc?
	if(graphicsContextCount == 1)
	{
		//Initialize GLEW
		if((lastError = glewInit()) != GLEW_OK)
		{
			EngineLogErrorOGL("glewInit failed", lastError);
		}
		
		//GLEW version
		glewVersion = glewGetString(GLEW_VERSION);
		EngineLog2("Using GLEW version " << glewVersion);
		
		//GL version
		strGLVersion = glGetString(GL_VERSION);
		strGLVendor = glGetString(GL_VENDOR);
		strGLRenderer = glGetString(GL_RENDERER);
		EngineLog2("Version &nbsp;= OpenGL " << strGLVersion << " <br /> Vendor &nbsp;&nbsp;= " << strGLVendor << " <br /> Renderer = " << strGLRenderer);
		EngineLog3("OpenGL extensions:<br />\n" << Replace(glGetString(GL_EXTENSIONS), " ", "<br />"));
	}
	
	//Default settings
	glShadeModel(GL_SMOOTH);
	glDepthFunc(GL_LEQUAL);
	glClearDepth(1.0);
	glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	
	//Features
	glEnable(GL_DEPTH_TEST);							//Enables Depth Testing
	glEnable(GL_CULL_FACE);								//Culling
	glEnable(GL_TEXTURE_2D);							//Texture Mapping
	//glEnable(GL_LIGHTING);								//Lighting
	glEnable(GL_BLEND);
	
	//Antialiasing
	if(antiAlias)
	{
		//TODO: ...
		glEnable(GL_MULTISAMPLE);
	}
	else
	{
		glDisable(GL_MULTISAMPLE);
	}
	
	//Hints
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
	glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST);
	
	//Set pixel zoom (for y-flipped pixmaps)
	glPixelZoom(1.0f, -1.0f);
	
	//Texture settings
	//TODO: Set this for every texture
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	//glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	
	/*
	//Fog
	glEnable(GL_FOG);
	glFogf(GL_FOG_START, 40.0);
	glFogf(GL_FOG_END, 100.0);
	float fogColor[4] = {1.0, 0.0, 0.0, 0.0};
	glFogfv(GL_FOG_COLOR, fogColor);
	glFogf(GL_FOG_DENSITY, 0.005);//0.01
	*/
	
	//Set the flags for clearing the screen
	clearFlags = stencilBuffer ? GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT : GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT;
	
	//TODO: Change to fullscreen mode
	
#ifdef WIN32
	//VSync
	if(WGLEW_EXT_swap_control)
	{
		if(vsync)
		{
			wglSwapIntervalEXT(true);
		}
		else
		{
			wglSwapIntervalEXT(false);
		}
	}
#endif
	
	//Set viewport
#ifdef WIN32
	win->UpdateClientSize();
#endif
	SetViewport(0, 0, win->GetWidth(), win->GetHeight());
	SetColor(255, 255, 255, 255);
	SetRotation(0);
	
	//Success
	initialized = true;
}

//Destructor
TOpenGL::~TOpenGL()
{
	//Debug info
	EngineLogDelete("OpenGL");
	
	//Change to window mode
#ifdef WIN32
	if(fullscreen)
	{
		ChangeDisplaySettings(Null, 0);
		//TODO: Implement this
	}
#elif defined(LINUX)
	if(fullscreen)
	{
		//TODO: Implement this
	}
#endif
	
#ifdef WIN32
	//Delete RC
	if(hRC)
	{
		//Test if it is possible
		if(!wglMakeCurrent(Null, Null))
		{
			EngineErrorLog("OpenGL Error: wglMakeCurrent(Null, Null) failed");
		}
		
		//Delete hRC
		if(!wglDeleteContext(hRC))
		{
			EngineErrorLog("OpenGL was not able to delete the rendering context [wglDeleteContext(hRC) failed]");
		}
	}
#endif
	
	//Release OpenGL
	if(--graphicsContextCount == 0)
	{
		//TODO: This could be removed
	}
}

//DrawCamera
void TOpenGL::DrawCamera(TCamera *cam)
{
	//TODO: Use viewport
	
	//TODO: Camera fov + range
	Set3D();
	
	//Set matrix
	SetCameraMatrix(cam);
	
	//Draw all child nodes of the root scene node
	DrawEntity(TEntity::Root);
}

//DrawEntity
void TOpenGL::DrawEntity(TEntity *entity)
{
	//Save camera (or parent) matrix
	glPushMatrix();
	
	//Set matrix
	SetEntityMatrix(entity);
	
	//Draw all child nodes
	#if STDVECTOR_USE_ITERATORS
		vector<TEntity*>::iterator childListEnd = entity->GetChildListAsCPPVector().end();
		for(vector<TEntity*>::iterator entityIt = entity->GetChildListAsCPPVector().begin(); entityIt != childListEnd; ++entityIt)
		{
			DrawEntity(*entityIt);
		}
	#else
		vector<TEntity*> &vec = entity->GetChildListAsCPPVector();
		int childListEnd = vec.size();
		for(int i=0; i < childListEnd; ++i)
		{
			DrawEntity(vec[i]);
		}
	#endif
	
	//Return if the mesh is Null
	if(!entity->GetMesh())
	{
		glPopMatrix();
		return;
	}
	
	//Culling
	if(!entity->CullingIsEnabled() && culling)
		DisableCulling();
	else if(entity->CullingIsEnabled() && !culling)
		EnableCulling();
		
	//Lighting
	if(!entity->LightingIsEnabled() && lighting)
		DisableLighting();
	else if(entity->LightingIsEnabled() && !lighting)
		EnableLighting();
	
	//TODO: Effects
	
	//End of the list
	vector<TSurface*>::iterator surfaceListEnd = entity->GetMesh()->surfaceList.end();	//TODO: Get mesh directly (friend function)
	
	//Draw every surface
	glBegin(GL_TRIANGLES);
		for(vector<TSurface*>::iterator surface = entity->GetMesh()->surfaceList.begin(); surface != surfaceListEnd; ++surface)		//TODO: Get mesh directly (friend function)
		{
			DrawSurface(*surface);
		}
	glEnd();
	
	//Load camera matrix
	glPopMatrix();
}

//DrawSurface
void TOpenGL::DrawSurface(TSurface *surface)
{
	int maxVertices = surface->vertexBuffer.vertexCount;
	TVertex *localBuffer = surface->vertexBuffer.localBuffer;
	
	for(int i = 0; i < maxVertices; ++i)
	{
		glColor3f(localBuffer[i].r, localBuffer[i].g, localBuffer[i].b);
		glVertex3f(localBuffer[i].position.x, localBuffer[i].position.y, localBuffer[i].position.z);
	}
	
	//Count rendered tris
	//TODO: Count for every mesh
	//TODO: Use indices for the counter
	trisRendered += maxVertices / 3;
}

//SetRenderMode
void TOpenGL::SetRenderMode(RenderMode mode)
{
	currentRenderMode = mode;
	switch(currentRenderMode)
	{
		//Normal
		case RENDERMODE_NORMAL:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
			glShadeModel(GL_SMOOTH);
			//EnableCulling();
			return;
			
		//Flat
		case RENDERMODE_FLAT:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
			glShadeModel(GL_FLAT);
			//EnableCulling();
			return;
		
		//Lines
		case RENDERMODE_LINES:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
			glShadeModel(GL_SMOOTH);
			//DisableCulling();
			return;
			
		//Points
		case RENDERMODE_POINTS:
			glPolygonMode(GL_FRONT_AND_BACK, GL_POINT);
			glShadeModel(GL_SMOOTH);	//TODO: Can this be GL_FLAT?
			//DisableCulling();
			return;
	}
}

//SetViewport
void TOpenGL::SetViewport(int x, int y, int width, int height)
{
	//Prevent division by zero
	if(height == 0)
	{
		height = 1;
	}
	
	//Debug info
	EngineLog4("Viewport: " << x << ", " << y << ", " << width << ", " << height);
	
	viewport.SetRect(x, y, width, height);
	
	gdk_threads_enter();
	glViewport(x, y, width, height);
	Set2D();
	gdk_threads_leave();
}

//RenderWorld
void TOpenGL::RenderWorld()
{
	//Reset counter
	trisRendered = 0;
	
	//Draw all cameras
	//BEGIN_GL_FUNCS();
	Set3D();
	for(vector<TCamera*>::iterator cam = TCamera::List.begin(); cam != TCamera::List.end(); ++cam)
	{
		DrawCamera(*cam);
	}
	Set2D();
	//END_GL_FUNCS();
}

//Set2D
void TOpenGL::Set2D()
{
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0, GetGraphicsWidth(), GetGraphicsHeight(), 0);
	glMatrixMode(GL_MODELVIEW);		//TODO: Is this required?
	glLoadIdentity();
	//glDisable(GL_DEPTH_TEST);							//Disables Depth Testing
	if(culling)
		DisableCulling();									//Culling
	if(lighting)
		DisableLighting();								//Beleuchtung
}

//Set3D
void TOpenGL::Set3D(float fovAngle, float zNear, float zFar)
{
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluPerspective(fovAngle, GLfloat(GetGraphicsWidth()) / GLfloat(GetGraphicsHeight()), zNear, zFar);
	glMatrixMode(GL_MODELVIEW);		//TODO: Is this required?
	glLoadIdentity();
	//glEnable(GL_DEPTH_TEST);							//Enables Depth Testing
	//glEnable(GL_LIGHTING);								//Beleuchtung
}

//Flush
void TOpenGL::Flush()
{
	if(!tex2DEnabled)
	{
		glEnable(GL_TEXTURE_2D);
		tex2DEnabled = true;
	}
	
	//Foreach image
	for(size_t i = 0; i < TOpenGLTexture::List.size(); ++i)
	{
		TOpenGLTexture::List[i]->DrawQueue();
	}
	glDisable(GL_TEXTURE_2D);
	tex2DEnabled = false;
	
	//Foreach pixmap
	vector<DrawPixmapCallInfo>::iterator theEnd_Pixmap = drawPixmapQueue.begin() - 1;
	
	for(vector<DrawPixmapCallInfo>::iterator it = drawPixmapQueue.end() - 1; it != theEnd_Pixmap; --it)
	{
		glRasterPos2i(it->x, it->y);
		glDrawPixels(it->pixmap->GetWidth(), it->pixmap->GetHeight(), it->pixmap->GetFormat(), GL_UNSIGNED_BYTE, it->pixmap->GetData());
	}
	drawPixmapQueue.clear();
	
	//Pos vars
	float x, y, z, endX, endY;
	
	//Foreach rect
	vector<DrawRectCallInfo>::iterator theEnd_Rect = drawRectQueue.begin() - 1;
	
	glBegin(GL_QUADS);
	for(vector<DrawRectCallInfo>::iterator it = drawRectQueue.end() - 1; it != theEnd_Rect; --it)
	{
		x = it->x;
		y = it->y;
		z = it->z;
		endX = it->width - handleXY.x;
		endY = it->height - handleXY.y;
		
		if(it->rotationZ != TOpenGLTexture::currentRotationZ || it->scalingX != TOpenGLTexture::currentScalingX || it->scalingY != TOpenGLTexture::currentScalingY)
		{
			TOpenGLTexture::currentRotationZ = it->rotationZ;
			TOpenGLTexture::currentScalingX = it->scalingX;
			TOpenGLTexture::currentScalingY = it->scalingY;
			TOpenGLTexture::Update2DMatrix();
		}
		
		glColor4ub(it->r, it->g, it->b, it->a);
		
		glVertex3f(	-handleXY.x * TOpenGLTexture::cosScaleX - handleXY.y * TOpenGLTexture::sinScaleY + x,
					-handleXY.x * TOpenGLTexture::sinScaleX - handleXY.y * TOpenGLTexture::cosScaleY + y,
					z);
		
		glVertex3f(	endX * TOpenGLTexture::cosScaleX - handleXY.y * TOpenGLTexture::sinScaleY + x,
					endX * TOpenGLTexture::sinScaleX - handleXY.y * TOpenGLTexture::cosScaleY + y,
					z);
		
		glVertex3f(	endX * TOpenGLTexture::cosScaleX + endY * TOpenGLTexture::sinScaleY + x,
					endX * TOpenGLTexture::sinScaleX + endY * TOpenGLTexture::cosScaleY + y,
					z);
		
		glVertex3f(	-handleXY.x * TOpenGLTexture::cosScaleX + endY * TOpenGLTexture::sinScaleY + x,
					-handleXY.x * TOpenGLTexture::sinScaleX + endY * TOpenGLTexture::cosScaleY + y,
					z);
	}
	glEnd();
	drawRectQueue.clear();
	
	//Foreach line
	vector<DrawLineCallInfo>::iterator theEnd_Line = drawLineQueue.begin() - 1;
	
	glBegin(GL_LINES);
	for(vector<DrawLineCallInfo>::iterator it = drawLineQueue.end() - 1; it != theEnd_Line; --it)
	{
		x = it->x;
		y = it->y;
		z = it->z;
		endX = it->toX - x - handleXY.x;
		endY = it->toY - y - handleXY.y;
		
		if(it->rotationZ != TOpenGLTexture::currentRotationZ || it->scalingX != TOpenGLTexture::currentScalingX || it->scalingY != TOpenGLTexture::currentScalingY)
		{
			TOpenGLTexture::currentRotationZ = it->rotationZ;
			TOpenGLTexture::currentScalingX = it->scalingX;
			TOpenGLTexture::currentScalingY = it->scalingY;
			TOpenGLTexture::Update2DMatrix();
		}
		
		glColor4ub(it->r, it->g, it->b, it->a);
		
		glVertex3f(	-handleXY.x * TOpenGLTexture::cosScaleX - handleXY.y * TOpenGLTexture::sinScaleY + x + 0.5f,
					-handleXY.x * TOpenGLTexture::sinScaleX - handleXY.y * TOpenGLTexture::cosScaleY + y + 0.5f,
					z);
		
		glVertex3f(	endX * TOpenGLTexture::cosScaleX + endY * TOpenGLTexture::sinScaleY + x + 0.5f,
					endX * TOpenGLTexture::sinScaleX + endY * TOpenGLTexture::cosScaleY + y + 0.5f,
					z);
	}
	glEnd();
	drawLineQueue.clear();
	
	//Foreach pixel
	vector<DrawPixelCallInfo>::iterator theEnd_Pixel = drawPixelQueue.begin() - 1;
	
	glBegin(GL_POINTS);
	for(vector<DrawPixelCallInfo>::iterator it = drawPixelQueue.end() - 1; it != theEnd_Pixel; --it)
	{
		glColor4ub(it->r, it->g, it->b, it->a);
		glVertex3f(it->x + 0.5f, it->y + 0.5f, it->z);
	}
	glEnd();
	drawPixelQueue.clear();
	
	//Reset z position
	zPos2D = Z_2D_RESET;
}

#define flua_glVertexAttribPointer(a, b, c, d, e, f) glVertexAttribPointer(a, b, c, d, e, reinterpret_cast<const GLvoid*>(f))

#include <public/Graphics/GLUT/C++/GLUT.hpp>

#include <flua/Math/Geometry/Euclidean/C++/Vector3.hpp>

//#include <public/Graphics/GLEW/C++/GLEW.hpp>
//#include <public/Graphics/GLEW/GLEW.hpp>

// ----------------------------------------------------
//  TODO: Replace all errors with exceptions
// ----------------------------------------------------

typedef Byte KeyType;

// Keys
KeyType KEY_DOWN = GLUT_KEY_DOWN;
KeyType KEY_END = GLUT_KEY_END;
KeyType KEY_F1 = GLUT_KEY_F1;
KeyType KEY_F10 = GLUT_KEY_F10;
KeyType KEY_F11 = GLUT_KEY_F11;
KeyType KEY_F12 = GLUT_KEY_F12;
KeyType KEY_F2 = GLUT_KEY_F2;
KeyType KEY_F3 = GLUT_KEY_F3;
KeyType KEY_F4 = GLUT_KEY_F4;
KeyType KEY_F5 = GLUT_KEY_F5;
KeyType KEY_F6 = GLUT_KEY_F6;
KeyType KEY_F7 = GLUT_KEY_F7;
KeyType KEY_F8 = GLUT_KEY_F8;
KeyType KEY_F9 = GLUT_KEY_F9;
KeyType KEY_HOME = GLUT_KEY_HOME;
KeyType KEY_INSERT = GLUT_KEY_INSERT;
KeyType KEY_LEFT = GLUT_KEY_LEFT;
KeyType KEY_PAGE_DOWN = GLUT_KEY_DOWN;
KeyType KEY_PAGE_UP = GLUT_KEY_PAGE_UP;
KeyType KEY_REPEAT_DEFAULT = GLUT_KEY_REPEAT_DEFAULT;
KeyType KEY_REPEAT_OFF = GLUT_KEY_REPEAT_OFF;
KeyType KEY_REPEAT_ON = GLUT_KEY_REPEAT_ON;
KeyType KEY_RIGHT = GLUT_KEY_RIGHT;
KeyType KEY_UP = GLUT_KEY_UP;
KeyType KEY_ESCAPE = 27;
KeyType KEY_ENTER = 13;

glm::mat4
	flua_viewMatrix,
	flua_projectionMatrix,
	flua_viewAndProjectionMatrix;

glm::vec3
	flua_xAxis(1, 0, 0),
	flua_yAxis(0, 1, 0),
	flua_zAxis(0, 0, 1);

glm::mat4 flua_identityMatrix(1.0f);

float flua_fovAngle = 45.0f;

// Global
GLint flua_currentProgram;
bool flua_glutRunFlag = false;
int flua_mouseX = 0;
int flua_mouseY = 0;
int flua_width, flua_height;

// glGetString(GL_VERSION)
bool flua_keys[256];

void flua_onClose() {
	flua_glutRunFlag = false;
}

void flua_onMouseMove(int x, int y) {
	flua_mouseX = x;
	flua_mouseY = y;
}

inline bool flua_isKeyDown(unsigned char key) {
	return flua_keys[key];
}

inline int flua_getMouseX() {
	return flua_mouseX;
}

inline int flua_getMouseY() {
	return flua_mouseY;
}

inline bool glutWindowOpen() {
	return flua_glutRunFlag;
}

inline void flua_onReshape(int width, int height) {
	flua_projectionMatrix = glm::perspective(flua_fovAngle, 1.0f * width / height, 0.1f, 1000.0f);
	glViewport(0, 0, width, height);

	flua_width = width;
	flua_height = height;

	//std::cout << "Reshape!" << std::endl;
}

inline void flua_onKeyDown(unsigned char key, int x, int y) {
	flua_keys[key] = true;
}

inline void flua_onKeyUp(unsigned char key, int x, int y) {
	flua_keys[key] = false;
}

inline void flua_onSpecialKeyDown(int key, int x, int y) {
	flua_keys[static_cast<unsigned char>(key)] = true;
}

inline void flua_onSpecialKeyUp(int key, int x, int y) {
	flua_keys[static_cast<unsigned char>(key)] = false;
}

inline void flua_initGLUT() {
	int argc = 0;
	glutInit(&argc, NULL);
	glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION);
}

inline void flua_setActiveProgram(GLint program) {
	if(program == flua_currentProgram)
		return;

	glUseProgram(program);
	flua_currentProgram = program;
}

inline void flua_setCamera(float x, float y, float z, float camAngleX, float camAngleY) {
	glm::vec3 lookat(0, 0, 0);

	lookat.x = sinf(camAngleX) * cosf(camAngleY);
	lookat.y = sinf(camAngleY);
	lookat.z = -cosf(camAngleX) * cosf(camAngleY);

	glm::vec3 camPos(x, y, z);
	glm::vec3 camUp(0.0, 1.0, 0.0);

#ifdef _WIN32
	int nWidth = glutGet(GLUT_WINDOW_WIDTH);
	int nHeight = glutGet(GLUT_WINDOW_HEIGHT);

	if(flua_width != nWidth || flua_height != nHeight) {
		flua_onReshape(nWidth, nHeight);
	}
#endif

	flua_viewMatrix = glm::lookAt(camPos, camPos + lookat, camUp);
	flua_viewAndProjectionMatrix = flua_projectionMatrix * flua_viewMatrix;
}

// TODO: Remove hardcoded values
inline void flua_setTransform(
		GLint flua_transformAttr,
		BPVector3<Float>* pos,
		BPVector3<Float>* rot)
{
	//float angle = glutGet(GLUT_ELAPSED_TIME) / 1000.0 * 15;  // 45° per second
	glm::vec3 axis_y(0.0, 1.0, 0.0);
	glm::mat4 rotation = \
	 glm::rotate(flua_identityMatrix, rot->_x, flua_xAxis) *  // X axis
	 glm::rotate(flua_identityMatrix, rot->_y, flua_yAxis) *  // Y axis
	 glm::rotate(flua_identityMatrix, rot->_z, flua_zAxis);   // Z axis

	glm::mat4 translation = glm::translate(flua_identityMatrix, glm::vec3(pos->_x, pos->_y, -pos->_z));
	glm::mat4 mvp = flua_viewAndProjectionMatrix * translation * rotation;

	glUniformMatrix4fv(flua_transformAttr, 1, GL_FALSE, glm::value_ptr(mvp));
}

inline GLuint flua_createGLSLProgram(GLuint vs, GLuint fs) {
	GLint link_ok = GL_FALSE;

	GLuint program = glCreateProgram();
	glAttachShader(program, vs);
	glAttachShader(program, fs);
	glLinkProgram(program);

	glGetProgramiv(program, GL_LINK_STATUS, &link_ok);
	if (!link_ok) {
		fprintf(stderr, "glLinkProgram:");
		return 0;
	}

	return program;
}

inline GLint flua_createGLSLProgramAttribute(GLuint program, char* attributeName) {
	GLint attrib = glGetAttribLocation(program, attributeName);

	if (attrib == -1) {
		fprintf(stderr, "Could not bind attribute '%s'\n", attributeName);
		return 0;
	}

	return attrib;
}

inline GLint flua_createGLSLProgramUniform(GLuint program, char* attributeName) {
	GLint attrib = glGetUniformLocation(program, attributeName);

	if (attrib == -1) {
		fprintf(stderr, "Could not bind uniform '%s'\n", attributeName);
		return 0;
	}

	return attrib;
}

inline UInt flua_getScreenWidth() {
	return glutGet(GLUT_SCREEN_WIDTH);
}

inline UInt flua_getScreenHeight() {
	return glutGet(GLUT_SCREEN_HEIGHT);
}

inline void flua_setVSync(bool vsync) {
	/*
#ifdef _WIN32
	glewWGL::wglSwapIntervalEXT(vsync);
#else
	glewGLX::glXSwapIntervalSGI(vsync);
#endif
	*/
}

inline Int flua_createGLUTWindow(char* title, int width, int height, bool fullscreen = false) {
	glutInitWindowPosition((flua_getScreenWidth() - width) / 2, (flua_getScreenHeight() - height) / 2);
	glutInitWindowSize(width, height);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_RGB | GLUT_DEPTH);

	int winId = glutCreateWindow(title);

	//flua_setVSync(true);

	// Force first call (not called automatically on Windows)
#ifdef _WIN32
	flua_onReshape(width, height);
#endif


	// Mouse
	glutMotionFunc(flua_onMouseMove);
	glutPassiveMotionFunc(flua_onMouseMove);
	glutReshapeFunc(flua_onReshape);

	// Keyboard
	glutKeyboardFunc(flua_onKeyDown);
	glutKeyboardUpFunc(flua_onKeyUp);
	glutSpecialFunc(flua_onSpecialKeyDown);
	glutSpecialUpFunc(flua_onSpecialKeyUp);

	glutCloseFunc(flua_onClose);
	flua_glutRunFlag = true;

	return winId;
}

inline BPUTF8String* flua_getLastGLError() {
	return _toString(reinterpret_cast<const Byte*>(gluErrorString(glGetError())));
}

void flua_printGLError(GLuint object) {
	GLint log_length = 0;

	if (glIsShader(object))
		glGetShaderiv(object, GL_INFO_LOG_LENGTH, &log_length);
	else if (glIsProgram(object))
		glGetProgramiv(object, GL_INFO_LOG_LENGTH, &log_length);
	else {
		fprintf(stderr, "printlog: Not a shader or a program\n");
		return;
	}

	char* error = (char*)malloc(log_length);

	if (glIsShader(object))
		glGetShaderInfoLog(object, log_length, NULL, error);
	else if (glIsProgram(object))
		glGetProgramInfoLog(object, log_length, NULL, error);

	fprintf(stderr, "%s", error);
	free(error);
}

GLuint flua_createShader(const GLchar* source, GLenum type) {
	if (source == NULL) {
		return 0;
	}

	GLuint res = glCreateShader(type);
	const GLchar* sources[] = {
#ifdef GL_ES_VERSION_2_0
		"#version 100\n"
		"#define GLES2\n",
#else
	  "#version 120\n"
#endif
		,
	    // GLES2 precision specifiers
#ifdef GL_ES_VERSION_2_0
	    // Define default float precision for fragment shaders:
	    (type == GL_FRAGMENT_SHADER) ?
	    "#ifdef GL_FRAGMENT_PRECISION_HIGH\n"
	    	"precision highp float;           \n"
	    "#else                            \n"
	    	"precision mediump float;         \n"
	    "#endif                           \n"
	    : ""
	    // Note: OpenGL ES automatically defines this:
	    // #define GL_ES
#else
	    // Ignore GLES 2 precision specifiers:
	    "#define lowp   \n"
	    "#define mediump\n"
	    "#define highp  \n"
#endif
		,
		source
	};

	glShaderSource(res, 3, sources, NULL);

	glCompileShader(res);
	GLint compileStatus = GL_FALSE;
	glGetShaderiv(res, GL_COMPILE_STATUS, &compileStatus);

	if (compileStatus == GL_FALSE) {
		flua_printGLError(res);
		glDeleteShader(res);
		return 0;
	}

	return res;
}

inline GLuint flua_createBuffer() {
	GLuint newVBO;
	glGenBuffers(1, &newVBO);
	return newVBO;
}

class BPTextureInfo: public gc {
public:
	inline BPTextureInfo(GLuint handle, UInt width, UInt height) : _handle(handle), _width(width), _height() {}

	GLuint _handle;
	UInt _width;
	UInt _height;
};

inline BPTextureInfo *flua_loadTexture(
		const char* filename,
		GLenum image_format,
		GLint internal_format,
		GLint level,
		GLint border
) {
	//image format
	FREE_IMAGE_FORMAT fif = FIF_UNKNOWN;

	//pointer to the image, once loaded
	FIBITMAP* dib(0);

	//pointer to the image data
	BYTE* bits(0);

	//image width and height
	unsigned int width(0), height(0);

	//OpenGL's image ID to map to
	GLuint gl_texID;

	//check the file signature and deduce its format
	fif = FreeImage_GetFileType(filename, 0);

	//if still unknown, try to guess the file format from the file extension
	if(fif == FIF_UNKNOWN)
		fif = FreeImage_GetFIFFromFilename(filename);

	//if still unkown, return failure
	if(fif == FIF_UNKNOWN)
		return NULL;

	//check that the plugin has reading capabilities and load the file
	if(FreeImage_FIFSupportsReading(fif)) {
		dib = FreeImage_Load(fif, filename);
	}

	//if the image failed to load, return failure
	if(!dib)
		return NULL;

	//retrieve the image data
	bits = FreeImage_GetBits(dib);

	//get the image width and height
	width = FreeImage_GetWidth(dib);
	height = FreeImage_GetHeight(dib);

	//get correct image_format
	switch(FreeImage_GetColorType(dib)) {
		case FIC_RGB:
			image_format = GL_BGR;
			break;
			
		case FIC_RGBALPHA:
			image_format = GL_BGRA;
			break;
			
		default:
			break;
	}
	
	//if somehow one of these failed (they shouldn't), return failure
	if((bits == 0) || (width == 0) || (height == 0))
		return NULL;

	//generate an OpenGL texture ID for this texture
	glGenTextures(1, &gl_texID);

	//bind to the new texture ID
	glBindTexture(GL_TEXTURE_2D, gl_texID);

	//store the texture data for OpenGL use
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	glTexImage2D(GL_TEXTURE_2D, level, internal_format, width, height, border, image_format, GL_UNSIGNED_BYTE, bits);

	gluBuild2DMipmaps(GL_TEXTURE_2D, internal_format, width, height, image_format, GL_UNSIGNED_BYTE, bits);

	//Free FreeImage's copy of the data
	// TODO: This needs to work instead of leading to a segfault at the end of the program.
	//#ifndef USING_GC
	//flua_gcPrintStats();
	//std::cout << "\nPointer address to FreeImage_Unload: " << dib << std::endl;
	//FreeImage_Unload(dib);
	free(dib);
	//#endif

	//return success
	return new (UseGC) BPTextureInfo(gl_texID, width, height);
}
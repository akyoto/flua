#define bp_glVertexAttribPointer(a, b, c, d, e, f) glVertexAttribPointer(a, b, c, d, e, reinterpret_cast<const GLvoid*>(f))

#include <public/Graphics/GLUT/C++/GLUT.hpp>

// ----------------------------------------------------
//  TODO: Replace all errors with exceptions
// ----------------------------------------------------

glm::mat4
	flua_viewMatrix,
	flua_projectionMatrix,
	flua_viewAndProjectionMatrix;

float flua_fovAngle = 45.0f;

// Global
bool flua_glutRunFlag = false;
int flua_mouseX = 0;
int flua_mouseY = 0;

// glGetString(GL_VERSION)

void flua_onClose() {
	flua_glutRunFlag = false;
}

void flua_onMouseMove(int x, int y) {
	flua_mouseX = x;
	flua_mouseY = y;
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
}

inline void flua_initGLUT() {
	int argc = 0;
	glutInit(&argc, NULL);
	glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION);
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

inline Int flua_createGLUTWindow(char* title, int width, int height, int depth, bool fullscreen = false) {
	glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) / 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) / 2);
	glutInitWindowSize(width, height);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_RGB | GLUT_DEPTH);
	
	int winId = glutCreateWindow(title);
	
	glutMotionFunc(flua_onMouseMove);
	glutPassiveMotionFunc(flua_onMouseMove);
	glutReshapeFunc(flua_onReshape);
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
	
	char* log = (char*)malloc(log_length);
	
	if (glIsShader(object))
		glGetShaderInfoLog(object, log_length, NULL, log);
	else if (glIsProgram(object))
		glGetProgramInfoLog(object, log_length, NULL, log);
	
	fprintf(stderr, "%s", log);
	free(log);
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

inline void flua_setActiveProgram(GLint program) {
	glUseProgram(program);
}

inline void flua_setCamera(float x, float y, float z, float camAngleX, float camAngleY) {
	glm::vec3 lookat(0, 0, 0);
	
	lookat.x = sinf(camAngleX) * cosf(camAngleY);
	lookat.y = sinf(camAngleY);
	lookat.z = -cosf(camAngleX) * cosf(camAngleY);
	
	glm::vec3 camPos(x, y, z);
	glm::vec3 camUp(0.0, 1.0, 0.0);
	
	flua_viewMatrix = glm::lookAt(camPos, camPos + lookat, camUp);
	flua_viewAndProjectionMatrix = flua_projectionMatrix * flua_viewMatrix;
}

// TODO: Remove hardcoded values
inline void flua_setTransform(
		GLint flua_transformAttr,
		float x, float y, float z)
{
	float angle = glutGet(GLUT_ELAPSED_TIME) / 1000.0 * 15;  // 45° per second
	glm::vec3 axis_y(0.0, 1.0, 0.0);
	glm::mat4 anim = \
	 glm::rotate(glm::mat4(1.0f), angle, glm::vec3(1, 0, 0)) *  // X axis
	 glm::rotate(glm::mat4(1.0f), angle, glm::vec3(0, 1, 0)) *  // Y axis
	 glm::rotate(glm::mat4(1.0f), angle, glm::vec3(0, 0, 1));   // Z axis
	
	glm::mat4 model = glm::translate(glm::mat4(1.0f), glm::vec3(x, y, -z));
	
	glm::mat4 mvp = flua_viewAndProjectionMatrix * model * anim;
	
	glUniformMatrix4fv(flua_transformAttr, 1, GL_FALSE, glm::value_ptr(mvp));
}

inline GLuint flua_loadTexture(const char* filename, GLenum image_format, GLint internal_format, GLint level, GLint border) {
	//image format
	FREE_IMAGE_FORMAT fif = FIF_UNKNOWN;
	
	//pointer to the image, once loaded
	FIBITMAP *dib(0);
	
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
		return false;

	//check that the plugin has reading capabilities and load the file
	if(FreeImage_FIFSupportsReading(fif))
		dib = FreeImage_Load(fif, filename);
	
	//if the image failed to load, return failure
	if(!dib)
		return false;

	//retrieve the image data
	bits = FreeImage_GetBits(dib);
	
	//get the image width and height
	width = FreeImage_GetWidth(dib);
	height = FreeImage_GetHeight(dib);
	
	//if this somehow one of these failed (they shouldn't), return failure
	if((bits == 0) || (width == 0) || (height == 0))
		return false;
	
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
	#ifndef USING_GC
		FreeImage_Unload(dib);
	#endif
	
	//return success
	return gl_texID;
}
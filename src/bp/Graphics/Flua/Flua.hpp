#define bp_glVertexAttribPointer(a, b, c, d, e, f) glVertexAttribPointer(a, b, c, d, e, reinterpret_cast<const GLvoid*>(f))

#include <public/Graphics/GLUT/C++/GLUT.hpp>

// ----------------------------------------------------
//  TODO: Replace all errors with exceptions
// ----------------------------------------------------

// Global
bool flua_glutRunFlag = false;

// glGetString(GL_VERSION)

void flua_onClose() {
	flua_glutRunFlag = false;
}

inline bool glutWindowOpen() {
	return flua_glutRunFlag;
}

inline void flua_onReshape(int width, int height) {
	/*fluaActiveWindow->_width = width;
	fluaActiveWindow->_height = height;*/
	
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

// TODO: Remove hardcoded values
inline void flua_testing(GLint transformAttr) {
	float angle = glutGet(GLUT_ELAPSED_TIME) / 1000.0 * 15;  // 45° per second
	glm::vec3 axis_y(0.0, 1.0, 0.0);
	glm::mat4 anim = \
	 glm::rotate(glm::mat4(1.0f), angle*3.0f, glm::vec3(1, 0, 0)) *  // X axis
	 glm::rotate(glm::mat4(1.0f), angle*2.0f, glm::vec3(0, 1, 0)) *  // Y axis
	 glm::rotate(glm::mat4(1.0f), angle*4.0f, glm::vec3(0, 0, 1));   // Z axis
	
	glm::mat4 model = glm::translate(glm::mat4(1.0f), glm::vec3(0.0, 0.0, -4.0));
	glm::mat4 view = glm::lookAt(glm::vec3(0.0, 2.0, 0.0), glm::vec3(0.0, 0.0, -4.0), glm::vec3(0.0, 1.0, 0.0));
	glm::mat4 projection = glm::perspective(45.0f, 1.0f * glutGet(GLUT_WINDOW_WIDTH) / glutGet(GLUT_WINDOW_HEIGHT), 0.1f, 10.0f);
	glm::mat4 mvp = projection * view * model * anim;
	
	glUniformMatrix4fv(transformAttr, 1, GL_FALSE, glm::value_ptr(mvp));
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
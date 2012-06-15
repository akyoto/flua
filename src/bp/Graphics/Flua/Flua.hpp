#include <public/Graphics/GLUT/C++/GLUT.hpp>

// Global
bool flua_glutRunFlag = false;

// glGetString(GL_VERSION)

void flua_closeFunc() {
	flua_glutRunFlag = false;
}

inline bool glutWindowOpen() {
	return flua_glutRunFlag;
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
		fprintf(stderr, "Could not bind attribute %s\n", attributeName);
		return 0;
	}
	
	return attrib;
}

inline Int flua_createGLUTWindow(char* title, int width, int height, int depth, bool fullscreen = false) {
	glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) / 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) / 2);
	glutInitWindowSize(width, height);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_RGB | GLUT_DEPTH);
	
	int winId = glutCreateWindow(title);
	
	glutCloseFunc(flua_closeFunc);
	flua_glutRunFlag = true;
	
	return winId;
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
	const GLchar* sources[2] = {
	#ifdef GL_ES_VERSION_2_0
		"#version 100\n"
		"#define GLES2\n",
	#else
	  "#version 120\n",
	#endif
	  source
	};
	
	glShaderSource(res, 2, sources, NULL);
	
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

inline GLuint flua_createVBO() {
	GLuint newVBO;
	glGenBuffers(1, &newVBO);
	return newVBO;
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
	glTexImage2D(GL_TEXTURE_2D, level, internal_format, width, height, border, image_format, GL_UNSIGNED_BYTE, bits);
	
	//Free FreeImage's copy of the data
	FreeImage_Unload(dib);
	
	//return success
	return gl_texID;
}
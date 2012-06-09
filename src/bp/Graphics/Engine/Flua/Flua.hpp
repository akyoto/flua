#include <public/Graphics/GLUT/C++/GLUT.hpp>

// Global
bool bp_glutRunFlag = false;

// glGetString(GL_VERSION)

void bp_closeFunc() {
	bp_glutRunFlag = false;
}

inline bool glutWindowOpen() {
	return bp_glutRunFlag;
}

inline void bp_initGLUT() {
	int argc = 0;
	glutInit(&argc, NULL);
	glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION);
}

inline GLuint bp_createGLSLProgram(GLuint vs, GLuint fs) {
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

inline GLint bp_createGLSLProgramAttribute(GLuint program, char* attributeName) {
	GLint attrib = glGetAttribLocation(program, attributeName);
	
	if (attrib == -1) {
		fprintf(stderr, "Could not bind attribute %s\n", attributeName);
		return 0;
	}
	
	return attrib;
}

inline Int bp_createGLUTWindow(char* title, int width, int height, int depth, bool fullscreen = false) {
	glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) / 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) / 2);
	glutInitWindowSize(width, height);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_RGB | GLUT_DEPTH);
	
	int winId = glutCreateWindow(title);
	
	glutCloseFunc(bp_closeFunc);
	bp_glutRunFlag = true;
	
	return winId;
}

void bp_printGLError(GLuint object) {
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

GLuint bp_createShader(const GLchar* source, GLenum type) {
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
		bp_printGLError(res);
		glDeleteShader(res);
		return 0;
	}
	
	return res;
}

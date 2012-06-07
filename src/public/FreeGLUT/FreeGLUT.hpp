#include "GL/freeglut.h"

// Global
bool bp_glutRunFlag = false;

// glGetString(GL_VERSION)

void bp_closeFunc() {
	bp_glutRunFlag = false;
}

inline bool glutWindowOpen() {
	return bp_glutRunFlag;
}

inline Int bp_createGLUTWindow(char* title, int width, int height, int depth, bool fullscreen = false) {
	int argc = 0;
	glutInit(&argc, NULL);
	
	glutInitWindowPosition((glutGet(GLUT_SCREEN_WIDTH) - width) / 2, (glutGet(GLUT_SCREEN_HEIGHT) - height) / 2);
	glutInitWindowSize(width, height);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
	
	int winId = glutCreateWindow(title);
	
	glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION);
	glutCloseFunc(bp_closeFunc);
	bp_glutRunFlag = true;
	
	return winId;
}
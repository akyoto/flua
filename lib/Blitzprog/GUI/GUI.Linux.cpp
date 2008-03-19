#include "GUI.Linux.hpp"

//XKeyMap
TMap<int, int> TWindow::keyMap;

//InitXKeyMap
void InitXKeyMap()
{
	/*
	 * Key codes from OIS - Object Oriented Input System
	 * TODO: Add link
	 * */
	
	//Debug info
	EngineLog4("Initializing key map...");
	
	//X Key Map to KeyCode
	TWindow::keyMap.Add(XK_1, KEY_1);
	TWindow::keyMap.Add(XK_2, KEY_2);
	TWindow::keyMap.Add(XK_3, KEY_3);
	TWindow::keyMap.Add(XK_4, KEY_4);
	TWindow::keyMap.Add(XK_5, KEY_5);
	TWindow::keyMap.Add(XK_6, KEY_6);
	TWindow::keyMap.Add(XK_7, KEY_7);
	TWindow::keyMap.Add(XK_8, KEY_8);
	TWindow::keyMap.Add(XK_9, KEY_9);
	TWindow::keyMap.Add(XK_0, KEY_0);
	
	TWindow::keyMap.Add(XK_BackSpace, KEY_BACK);
	
	TWindow::keyMap.Add(XK_minus, KEY_MINUS);
	TWindow::keyMap.Add(XK_equal, KEY_EQUALS);
	TWindow::keyMap.Add(XK_space, KEY_SPACE);
	TWindow::keyMap.Add(XK_comma, KEY_COMMA);
	TWindow::keyMap.Add(XK_period, KEY_PERIOD);
	
	TWindow::keyMap.Add(XK_backslash, KEY_BACKSLASH);
	TWindow::keyMap.Add(XK_slash, KEY_SLASH);
	TWindow::keyMap.Add(XK_bracketleft, KEY_LBRACKET);
	TWindow::keyMap.Add(XK_bracketright, KEY_RBRACKET);
	
	TWindow::keyMap.Add(XK_Escape,KEY_ESCAPE);
	TWindow::keyMap.Add(XK_Caps_Lock, KEY_CAPITAL);
	
	TWindow::keyMap.Add(XK_Tab, KEY_TAB);
	TWindow::keyMap.Add(XK_Return, KEY_RETURN);
	TWindow::keyMap.Add(XK_Control_L, KEY_LCONTROL);
	TWindow::keyMap.Add(XK_Control_R, KEY_RCONTROL);
	
	TWindow::keyMap.Add(XK_colon, KEY_COLON);
	TWindow::keyMap.Add(XK_semicolon, KEY_SEMICOLON);
	TWindow::keyMap.Add(XK_apostrophe, KEY_APOSTROPHE);
	TWindow::keyMap.Add(XK_grave, KEY_GRAVE);
	
	TWindow::keyMap.Add(XK_a, KEY_A);
	TWindow::keyMap.Add(XK_b, KEY_B);
	TWindow::keyMap.Add(XK_c, KEY_C);
	TWindow::keyMap.Add(XK_d, KEY_D);
	TWindow::keyMap.Add(XK_e, KEY_E);
	TWindow::keyMap.Add(XK_f, KEY_F);
	TWindow::keyMap.Add(XK_g, KEY_G);
	TWindow::keyMap.Add(XK_h, KEY_H);
	TWindow::keyMap.Add(XK_i, KEY_I);
	TWindow::keyMap.Add(XK_j, KEY_J);
	TWindow::keyMap.Add(XK_k, KEY_K);
	TWindow::keyMap.Add(XK_l, KEY_L);
	TWindow::keyMap.Add(XK_m, KEY_M);
	TWindow::keyMap.Add(XK_n, KEY_N);
	TWindow::keyMap.Add(XK_o, KEY_O);
	TWindow::keyMap.Add(XK_p, KEY_P);
	TWindow::keyMap.Add(XK_q, KEY_Q);
	TWindow::keyMap.Add(XK_r, KEY_R);
	TWindow::keyMap.Add(XK_s, KEY_S);
	TWindow::keyMap.Add(XK_t, KEY_T);
	TWindow::keyMap.Add(XK_u, KEY_U);
	TWindow::keyMap.Add(XK_v, KEY_V);
	TWindow::keyMap.Add(XK_w, KEY_W);
	TWindow::keyMap.Add(XK_x, KEY_X);
	TWindow::keyMap.Add(XK_y, KEY_Y);
	TWindow::keyMap.Add(XK_z, KEY_Z);
	
	TWindow::keyMap.Add(XK_F1, KEY_F1);
	TWindow::keyMap.Add(XK_F2, KEY_F2);
	TWindow::keyMap.Add(XK_F3, KEY_F3);
	TWindow::keyMap.Add(XK_F4, KEY_F4);
	TWindow::keyMap.Add(XK_F5, KEY_F5);
	TWindow::keyMap.Add(XK_F6, KEY_F6);
	TWindow::keyMap.Add(XK_F7, KEY_F7);
	TWindow::keyMap.Add(XK_F8, KEY_F8);
	TWindow::keyMap.Add(XK_F9, KEY_F9);
	TWindow::keyMap.Add(XK_F10, KEY_F10);
	TWindow::keyMap.Add(XK_F11, KEY_F11);
	TWindow::keyMap.Add(XK_F12, KEY_F12);
	TWindow::keyMap.Add(XK_F13, KEY_F13);
	TWindow::keyMap.Add(XK_F14, KEY_F14);
	TWindow::keyMap.Add(XK_F15, KEY_F15);
	
	//Keypad
	TWindow::keyMap.Add(XK_KP_0, KEY_NUMPAD0);
	TWindow::keyMap.Add(XK_KP_1, KEY_NUMPAD1);
	TWindow::keyMap.Add(XK_KP_2, KEY_NUMPAD2);
	TWindow::keyMap.Add(XK_KP_3, KEY_NUMPAD3);
	TWindow::keyMap.Add(XK_KP_4, KEY_NUMPAD4);
	TWindow::keyMap.Add(XK_KP_5, KEY_NUMPAD5);
	TWindow::keyMap.Add(XK_KP_6, KEY_NUMPAD6);
	TWindow::keyMap.Add(XK_KP_7, KEY_NUMPAD7);
	TWindow::keyMap.Add(XK_KP_8, KEY_NUMPAD8);
	TWindow::keyMap.Add(XK_KP_9, KEY_NUMPAD9);
	TWindow::keyMap.Add(XK_KP_Add, KEY_ADD);
	TWindow::keyMap.Add(XK_KP_Subtract, KEY_SUBTRACT);
	TWindow::keyMap.Add(XK_KP_Decimal, KEY_DECIMAL);
	TWindow::keyMap.Add(XK_KP_Equal, KEY_NUMPADEQUALS);
	TWindow::keyMap.Add(XK_KP_Divide, KEY_DIVIDE);
	TWindow::keyMap.Add(XK_KP_Multiply, KEY_MULTIPLY);
	TWindow::keyMap.Add(XK_KP_Enter, KEY_NUMPADENTER);
	
	//Keypad with numlock off
	TWindow::keyMap.Add(XK_KP_Home, KEY_NUMPAD7);
	TWindow::keyMap.Add(XK_KP_Up, KEY_NUMPAD8);
	TWindow::keyMap.Add(XK_KP_Page_Up, KEY_NUMPAD9);
	TWindow::keyMap.Add(XK_KP_Left, KEY_NUMPAD4);
	TWindow::keyMap.Add(XK_KP_Begin, KEY_NUMPAD5);
	TWindow::keyMap.Add(XK_KP_Right, KEY_NUMPAD6);
	TWindow::keyMap.Add(XK_KP_End, KEY_NUMPAD1);
	TWindow::keyMap.Add(XK_KP_Down, KEY_NUMPAD2);
	TWindow::keyMap.Add(XK_KP_Page_Down, KEY_NUMPAD3);
	TWindow::keyMap.Add(XK_KP_Insert, KEY_NUMPAD0);
	TWindow::keyMap.Add(XK_KP_Delete, KEY_DECIMAL);
	
	TWindow::keyMap.Add(XK_Up, KEY_UP);
	TWindow::keyMap.Add(XK_Down, KEY_DOWN);
	TWindow::keyMap.Add(XK_Left, KEY_LEFT);
	TWindow::keyMap.Add(XK_Right, KEY_RIGHT);
	
	TWindow::keyMap.Add(XK_Page_Up, KEY_PGUP);
	TWindow::keyMap.Add(XK_Page_Down, KEY_PGDOWN);
	TWindow::keyMap.Add(XK_Home, KEY_HOME);
	TWindow::keyMap.Add(XK_End, KEY_END);
	
	TWindow::keyMap.Add(XK_Num_Lock, KEY_NUMLOCK);
	TWindow::keyMap.Add(XK_Print, KEY_SYSRQ);
	TWindow::keyMap.Add(XK_Scroll_Lock, KEY_SCROLL);
	TWindow::keyMap.Add(XK_Pause, KEY_PAUSE);
	
	TWindow::keyMap.Add(XK_Shift_R, KEY_RSHIFT);
	TWindow::keyMap.Add(XK_Shift_L, KEY_LSHIFT);
	TWindow::keyMap.Add(XK_Alt_R, KEY_RMENU);
	TWindow::keyMap.Add(XK_Alt_L, KEY_LMENU);
	
	TWindow::keyMap.Add(XK_Insert, KEY_INSERT);
	TWindow::keyMap.Add(XK_Delete, KEY_DELETE);
	
	TWindow::keyMap.Add(XK_Super_L, KEY_LWIN);
	TWindow::keyMap.Add(XK_Super_R, KEY_RWIN);
	TWindow::keyMap.Add(XK_Menu, KEY_APPS);
	
	//Debug info
	EngineLog4("Key map initialized.");
}

//GUIMain
void GUIMain()
{
	EngineLog4("System thread runs.");
	
	InitXKeyMap();
	
	int argc = 0;
	char **argv = Null;
	
	EngineLog4("Initializing GDK threads...");
	g_thread_init(Null);
	gdk_threads_init();
	EngineLog4("GDK threads initialized.");
	
	EngineLog4("Compiled with GTK version " << GTK_MAJOR_VERSION << "." << GTK_MINOR_VERSION << "." << GTK_MICRO_VERSION);
	EngineLog4("Initializing GTK...");
	GUIStartUp::bpGtkInitialized = gtk_init_check(&argc, &argv);
	EngineLog4("GTK initialized.");
	EngineLog4("Using GTK version " << gtk_major_version << "." << gtk_minor_version << "." << gtk_micro_version);
	Delay(0);
	
	while(1)
	{
		PollSystem();
		Delay(20);
	}
}

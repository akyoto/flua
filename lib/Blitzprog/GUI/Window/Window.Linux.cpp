#include "Window.Linux.hpp"

//Constructor
TWindow::TWindow(const String &title, int x, int y, int width, int height)
{
	//Debug info
	EngineLogNew("Window");
	
	//Create new window
	gdk_threads_enter();
	handle = GTK_WINDOW(gtk_window_new(GTK_WINDOW_TOPLEVEL));
	gdk_threads_leave();
	
	//Title
	SetText(title);
	
	//Size
	SetSize(width, height);
	
	//X
	if(x == -1)
	{
		x = ScreenWidth() / 2 - width / 2;
	}
	
	//Y
	if(y == -1)
	{
		y = ScreenHeight() / 2 - height / 2;
	}
	
	//Position
	SetPosition(x, y);
	
	//Enter critical section
	gdk_threads_enter();
	
	//VBox
	vbox = GTK_VBOX(gtk_vbox_new(false, 0));
	gtk_widget_show(GTK_WIDGET(vbox));
	
	//Create layout
	fixedLayout = GTK_FIXED(gtk_fixed_new());
	gtk_widget_show(GTK_WIDGET(fixedLayout));
	gtk_box_pack_start(GTK_BOX(vbox), GTK_WIDGET(fixedLayout), true, true, 0);
	
	//Add VBox
	gtk_container_add(GTK_CONTAINER(handle), GTK_WIDGET(vbox));
	
	//Activate events
	gtk_widget_set_events(GTK_WIDGET(handle), 	gtk_widget_get_events(GTK_WIDGET(handle))
												| GDK_BUTTON_PRESS_MASK 
												| GDK_BUTTON_RELEASE_MASK 
												| GDK_POINTER_MOTION_MASK 
												//| GDK_POINTER_MOTION_HINT_MASK 
												| GDK_BUTTON_RELEASE_MASK);
	
	//Callbacks
	g_signal_connect(handle, "delete-event", G_CALLBACK(delete_event), Null);				//Delete window
	g_signal_connect(handle, "key_press_event", G_CALLBACK(key_press_event), Null);			//Press key
	g_signal_connect(handle, "key_release_event", G_CALLBACK(key_release_event), Null);		//Release key
	g_signal_connect(handle, "motion_notify_event", G_CALLBACK(motion_notify_event), static_cast<gpointer>(this));	//Move mouse
	
	//Increment reference counter
	g_object_ref(handle);
	
	//Leave critical section
	gdk_threads_leave();
}

//Destructor
TWindow::~TWindow()
{
	//Debug info
	EngineLogDelete("Window");
	
	//Destroy widget
	if(GTK_IS_WINDOW(handle))
	{
		EngineLog3("Destroying widget handle");
		gdk_threads_enter();
		gtk_widget_destroy(GTK_WIDGET(handle));
		//g_object_unref(handle);
		gdk_threads_leave();
	}
}

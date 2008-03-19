#include "Button.Linux.hpp"

//Destructor
TButton::~TButton()
{
	//Debug info
	EngineLogDelete("Button");
	
	//Destroy widget
	if(GTK_IS_BUTTON(handle))
	{
		EngineLog3("Destroying widget handle");
		gdk_threads_enter();
		gtk_widget_destroy(GTK_WIDGET(handle));
		//g_object_unref(handle);
		gdk_threads_leave();
	}
}

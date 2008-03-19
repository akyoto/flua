////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.GUI.Window.Linux
// Author:				Eduard Urbach
// Description:			Window class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GUI_WINDOW_LINUX_HPP_
#define BLITZPROG_GUI_WINDOW_LINUX_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Input/Input.hpp>
#include <Blitzprog/GUI/GUI.Linux.hpp>
#include <Blitzprog/GUI/Widget/Widget.hpp>
#include <Blitzprog/Collection/Map/Map.hpp>

//GTK
#include <gtk/gtk.h>

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//SharedPtr<TWindow>
class TWindow;
typedef SharedPtr<TWindow> Window;

//Window
class TWindow: public TWidget
{
	public:
		
		//Public static vars
		static TMap<int, int> keyMap;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TWindow(const String &title = "", int x = -1, int y = -1, int width = 640, int height = 480);
		
		//Destructor
		~TWindow();
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Show
		inline void Show()
		{
			gdk_threads_enter();
			gtk_widget_show_all(GTK_WIDGET(handle));
			gdk_threads_leave();
		}
		
		//Hide
		inline void Hide()
		{
			gdk_threads_enter();
			gtk_widget_hide_all(GTK_WIDGET(handle));
			gdk_threads_leave();
		}
		
		//Enable
		inline void Enable()
		{
			gdk_threads_enter();
			gtk_widget_set_sensitive(GTK_WIDGET(handle), true);
			gdk_threads_leave();
		}
		
		//Disable
		inline void Disable()
		{
			gdk_threads_enter();
			gtk_widget_set_sensitive(GTK_WIDGET(handle), false);
			gdk_threads_leave();
		}
		
		//Redraw
		inline void Redraw()
		{
			gdk_threads_enter();
			gtk_widget_queue_draw(GTK_WIDGET(handle));
			gdk_threads_leave();
			//TODO: gtk_widget_queue_draw_area(GTK_WIDGET(handle));
		}
		
		//SetText
		inline void SetText(const String &title)
		{
			gdk_threads_enter();
			gtk_window_set_title(handle, title);
			gdk_threads_leave();
		}
		
		//GetText
		inline String GetText() const
		{
			return gtk_window_get_title(handle);
		}
		
		//SetShape
		inline void SetShape(const Rect &rect)
		{
			SetShape(rect.x, rect.y, rect.width, rect.height);
		}
		
		//SetShape
		inline void SetShape(int x, int y, int width, int height)
		{
			gdk_threads_enter();
			gtk_window_move(handle, x, y);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetShape
		inline Rect GetShape() const
		{
			//TODO: Optimize this
			Rect rect;
			gdk_threads_enter();
			gtk_window_get_position(handle, &rect.x, &rect.y);
			gtk_window_get_size(handle, &rect.width, &rect.height);
			gdk_threads_leave();
			return rect;
		}
		
		//SetPosition
		inline void SetPosition(int x, int y)
		{
			gdk_threads_enter();
			gtk_window_move(handle, x, y);
			gdk_threads_leave();
		}
		
		//GetPosition
		inline Point GetPosition() const
		{
			Point temp;
			gdk_threads_enter();
			gtk_window_get_position(handle, &temp.x, &temp.y);
			gdk_threads_leave();
			return temp;
		}
		
		//SetX
		inline void SetX(int x)
		{
			int y;
			gdk_threads_enter();
			gtk_window_get_position(handle, Null, &y);
			gtk_window_move(handle, x, y);
			gdk_threads_leave();
		}
		
		//GetX
		inline int GetX() const
		{
			int x;
			gdk_threads_enter();
			gtk_window_get_position(handle, &x, Null);
			gdk_threads_leave();
			return x;
		}
		
		//SetY
		inline void SetY(int y)
		{
			int x;
			gdk_threads_enter();
			gtk_window_get_position(handle, &x, Null);
			gtk_window_move(handle, x, y);
			gdk_threads_leave();
		}
		
		//GetY
		inline int GetY() const
		{
			int y;
			gdk_threads_enter();
			gtk_window_get_position(handle, Null, &y);
			gdk_threads_leave();
			return y;
		}
		
		//SetSize
		inline void SetSize(int width, int height)
		{
			gdk_threads_enter();
			//gtk_window_resize(handle, width, height);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetSize
		inline Vector2D GetSize() const
		{
			Vector2D temp;
			gdk_threads_enter();
			gtk_window_get_size(handle, &temp.x, &temp.y);
			gdk_threads_leave();
			return temp;
		}
		
		//SetWidth
		inline void SetWidth(int width)
		{
			int height;
			gdk_threads_enter();
			gtk_window_get_size(handle, Null, &height);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetWidth
		inline int GetWidth() const
		{
			int width;
			gdk_threads_enter();
			gtk_window_get_size(handle, &width, Null);
			gdk_threads_leave();
			return width;
		}
		
		//SetHeight
		inline void SetHeight(int height)
		{
			int width;
			gdk_threads_enter();
			gtk_window_get_size(handle, &width, Null);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetHeight
		inline int GetHeight() const
		{
			int height;
			gdk_threads_enter();
			gtk_window_get_size(handle, Null, &height);
			gdk_threads_leave();
			return height;
		}
		
		//IsAlive
		inline bool IsAlive() const
		{
			Delay(0);
			return G_OBJECT(handle)->ref_count >= 2;
		}
		
		//IsDestroyed
		inline bool IsDestroyed() const
		{
			return !IsAlive();
		}
		
		//IsHidden
		inline bool IsHidden() const
		{
			return (GTK_WIDGET_FLAGS(handle) & GTK_VISIBLE) == 0;
		}
		
		//IsVisible
		inline bool IsVisible() const
		{
			return GTK_WIDGET_VISIBLE(handle);
		}
		
		//IsEnabled
		inline bool IsEnabled() const
		{
			return GTK_WIDGET_SENSITIVE(handle);
		}
		
		//IsDisabled
		inline bool IsDisabled() const
		{
			return (GTK_WIDGET_FLAGS(handle) & GTK_SENSITIVE) == 0;
		}
		
		//SetFont
		inline void SetFont(Font font)
		{
			//TODO:
			gdk_threads_enter();
			gdk_threads_leave();
			//gtk_widget_modify_font(handle, )
		}
		
		//GetFont
		inline Font GetFont() const
		{
			return Null;	//TODO:
		}
		
		//SetLayout
		inline void SetLayout(EdgePosition left, EdgePosition right, EdgePosition top, EdgePosition bottom)
		{
			
		}
		
		//Dock
		inline void Dock(DockPosition dockMode)
		{
			
		}
		
		//SetFocus
		inline void SetFocus()
		{
			//gtk_widget_activate(GTK_WIDGET(handle));
			//gtk_widget_grab_focus(GTK_WIDGET(handle));
		}
		
		//HasFocus
		inline bool HasFocus() const
		{
			return gtk_window_is_active(handle);
			//GTK_WIDGET_HAS_FOCUS(handle);
			//gtk_widget_is_focus(handle);
		}
		
		//Maximize
		inline void Maximize()
		{
			gdk_threads_enter();
			gtk_window_maximize(handle);
			gdk_threads_leave();
		}
		
		//Unmaximize
		inline void Unmaximize()
		{
			gdk_threads_enter();
			gtk_window_unmaximize(handle);
			gdk_threads_leave();
		}
		
		//Minimize
		inline void Minimize()
		{
			//TODO: Implement this
			gdk_threads_enter();
			gdk_threads_leave();
		}
		
		//SetMinSize
		inline void SetMinSize(int width, int height)
		{
			//TODO: Implement this
			gdk_threads_enter();
			gdk_threads_leave();
		}
		
		//SetMaxSize
		inline void SetMaxSize(int width, int height)
		{
			//TODO: Implement this
			gdk_threads_enter();
			gdk_threads_leave();
		}
		
		//GetMouseX
		inline int GetMouseX() const
		{
			return mouseX;
		}
		
		//GetMouseY
		inline int GetMouseY() const
		{
			return mouseY;
		}
		
		//ToString
		inline String ToString() const
		{
			return GetText();
		}
		
		//GetHandle
		inline GtkWidget *GetHandle() const
		{
			return GTK_WIDGET(handle);
		}
		
		//GetGtkFixed
		inline GtkFixed *GetGtkFixed() const
		{
			return fixedLayout;
		}
		
		//delete_event
		static inline bool delete_event(GtkWidget *widget, GdkEvent *event, gpointer data)
		{
			if(G_IS_OBJECT(widget))
				g_object_unref(widget);
			return true;
		}
		
		//key_press_event
		static inline bool key_press_event(GtkWidget *widget, GdkEventKey *event, gpointer data)
		{
			EngineLog5("key_press_event: " << event->keyval << " : " << event->hardware_keycode);
			int index = keyMap[event->keyval];
			TInput::buttonsHit[index] = TInput::buttons[index] = 1.0f;
			return false;
		}
		
		//key_release_event
		static inline bool key_release_event(GtkWidget *widget, GdkEventKey *event, gpointer data)
		{
			EngineLog5("key_release_event: " << event->keyval << " : " << event->hardware_keycode);
			int index = keyMap[event->keyval];
			TInput::buttonsHit[index] = TInput::buttons[index] = 0.0f;
			return false;
		}
		
		//motion_notify_event
		static inline bool motion_notify_event(GtkWindow *widget, GdkEventMotion *event, gpointer data)
		{
			EngineLog5("motion_notify_event: " << event->x << ", " << event->y);
			TWindow *tmp = static_cast<TWindow*>(data);
			tmp->mouseX = static_cast<int>(event->x);
			tmp->mouseY = static_cast<int>(event->y);
			return false;
		}
		
	protected:
		GtkWindow *handle;
		GtkVBox *vbox;
		GtkFixed *fixedLayout;
		int mouseX;
		int mouseY;
};
#define CreateWindow new TWindow

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



#endif /*BLITZPROG_GUI_WINDOW_LINUX_HPP_*/

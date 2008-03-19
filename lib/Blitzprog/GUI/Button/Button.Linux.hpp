////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.GUI.Button.Linux
// Author:				Eduard Urbach
// Description:			-
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GUI_BUTTON_LINUX_HPP_
#define BLITZPROG_GUI_BUTTON_LINUX_HPP_

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

//Default values
const int DEFAULT_BUTTON_WIDTH = 96;
const int DEFAULT_BUTTON_HEIGHT = 24;

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//SharedPtr<TButton>
class TButton;
typedef SharedPtr<TButton> Button;

//Button
class TButton: public TWidget
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		template <typename WidgetType>
		TButton(const String &title = "", int x = -1, int y = -1, int width = DEFAULT_BUTTON_WIDTH, int height = DEFAULT_BUTTON_HEIGHT, WidgetType nParent = Null)
		{
			//Debug info
			EngineLogNew("Button: " << title);
			
			//Create new window
			gdk_threads_enter();
			handle = GTK_BUTTON(gtk_button_new_with_label(title));
			gtk_widget_show(GTK_WIDGET(handle));
			gdk_threads_leave();
			
			//Set parent
			SetParent(nParent);
			
			//Size
			SetSize(width, height);
			
			//X
			if(x == -1)
			{
				x = parent->GetWidth() / 2 - width / 2;
			}
			
			//Y
			if(y == -1)
			{
				y = parent->GetHeight() / 2 - height / 2;
			}
			
			//Position
			SetPosition(x, y);
			
			//Increment reference counter
			//gdk_threads_enter();
			//g_object_ref(handle);
			//gdk_threads_leave();
		}

		//Destructor
		~TButton();
		
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
			gtk_widget_show(GTK_WIDGET(handle));
			gdk_threads_leave();
		}
		
		//Hide
		inline void Hide()
		{
			gdk_threads_enter();
			gtk_widget_hide(GTK_WIDGET(handle));
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
		}
		
		//SetText
		inline void SetText(const String &title)
		{
			gdk_threads_enter();
			gtk_button_set_label(handle, title);
			gdk_threads_leave();
		}
		
		//GetText
		inline String GetText() const
		{
			return gtk_button_get_label(handle);
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
			gtk_fixed_move(parent->GetGtkFixed(), GTK_WIDGET(handle), x, y);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetShape
		inline Rect GetShape() const
		{
			//TODO: Optimize this
			Rect rect;
			rect.x = x;
			rect.y = y;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), &rect.width, &rect.height);
			gdk_threads_leave();
			return rect;
		}
		
		//SetPosition
		inline void SetPosition(int nX, int nY)
		{
			x = nX;
			y = nY;
			gdk_threads_enter();
			gtk_fixed_move(parent->GetGtkFixed(), GTK_WIDGET(handle), x, y);
			gdk_threads_leave();
		}
		
		//GetPosition
		inline Point GetPosition() const
		{
			return Point(x, y);
		}
		
		//SetX
		inline void SetX(int nX)
		{
			x = nX;
			gdk_threads_enter();
			gtk_fixed_move(parent->GetGtkFixed(), GTK_WIDGET(handle), x, y);
			gdk_threads_leave();
		}
		
		//GetX
		inline int GetX() const
		{
			return x;
		}
		
		//SetY
		inline void SetY(int nY)
		{
			y = nY;
			gdk_threads_enter();
			gtk_fixed_move(parent->GetGtkFixed(), GTK_WIDGET(handle), x, y);
			gdk_threads_leave();
		}
		
		//GetY
		inline int GetY() const
		{
			return y;
		}
		
		//SetSize
		inline void SetSize(int width, int height)
		{
			gdk_threads_enter();
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetSize
		inline Vector2D GetSize() const
		{
			Vector2D temp;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), &temp.x, &temp.y);
			gdk_threads_leave();
			return temp;
		}
		
		//SetWidth
		inline void SetWidth(int width)
		{
			int height;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), Null, &height);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetWidth
		inline int GetWidth() const
		{
			int width;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), &width, Null);
			gdk_threads_leave();
			return width;
		}
		
		//SetHeight
		inline void SetHeight(int height)
		{
			int width;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), &width, Null);
			gtk_widget_set_size_request(GTK_WIDGET(handle), width, height);
			gdk_threads_leave();
		}
		
		//GetHeight
		inline int GetHeight() const
		{
			int height;
			gdk_threads_enter();
			gtk_widget_get_size_request(GTK_WIDGET(handle), Null, &height);
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
			gtk_widget_grab_focus(GTK_WIDGET(handle));
		}
		
		//HasFocus
		inline bool HasFocus() const
		{
			return GTK_WIDGET_HAS_FOCUS(handle);
			//gtk_widget_is_focus(handle);
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
			return Null;
		}
		
	protected:
		GtkButton *handle;
		int x;
		int y;
};
#define CreateButton new TButton

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



#endif /*BLITZPROG_GUI_BUTTON_LINUX_HPP_*/

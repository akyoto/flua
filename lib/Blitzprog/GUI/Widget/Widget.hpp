////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.GUI.Window
// Author:				Eduard Urbach
// Description:			Window class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_GUI_WIDGET_HPP_
#define BLITZPROG_GUI_WIDGET_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/Math/Vector2D/Vector2D.hpp>
#include <Blitzprog/Math/Rect/Rect.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//EdgePosition
enum EdgePosition
{
	EDGE_CENTERED = 0,
	EDGE_ALIGNED = 1,
	EDGE_RELATIVE = 2
};

//DockPosition
enum DockPosition
{
	DOCK_LEFT = 0,
	DOCK_RIGHT = 1,
	DOCK_TOP = 2,
	DOCK_BOTTOM = 3
};

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//TODO: Remove this
typedef int* Font;

//SharedPtr<TWidget>
class TWidget;
typedef SharedPtr<TWidget> Widget;

//Widget
class TWidget: public TPrintable
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Destructor
		virtual ~TWidget()
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		//Show
		virtual void Show() = 0;
		
		//Hide
		virtual void Hide() = 0;
		
		//Enable
		virtual void Enable() = 0;
		
		//Disable
		virtual void Disable() = 0;
		
		//Redraw
		virtual void Redraw() = 0;
		
		//SetText
		virtual void SetText(const String &title) = 0;
		
		//GetText
		virtual String GetText() const = 0;
		
		//SetShape
		virtual void SetShape(const Rect &rect) = 0;
		
		//SetShape
		virtual void SetShape(int x, int y, int width, int height) = 0;
		
		//GetShape
		virtual Rect GetShape() const = 0;
		
		//SetPosition
		virtual void SetPosition(int x, int y) = 0;
		
		//GetPosition
		virtual Point GetPosition() const = 0;
		
		//SetX
		virtual void SetX(int x) = 0;
		
		//GetX
		virtual int GetX() const = 0;
		
		//SetY
		virtual void SetY(int y) = 0;
		
		//GetY
		virtual int GetY() const = 0;
		
		//SetSize
		virtual void SetSize(int width, int height) = 0;
		
		//GetSize
		virtual Vector2D GetSize() const = 0;
		
		//SetWidth
		virtual void SetWidth(int width) = 0;
		
		//GetWidth
		virtual int GetWidth() const = 0;
		
		//SetHeight
		virtual void SetHeight(int height) = 0;
		
		//GetHeight
		virtual int GetHeight() const = 0;
		
		//IsAlive
		virtual bool IsAlive() const = 0;
		
		//IsDestroyed
		virtual bool IsDestroyed() const = 0;
		
		//IsHidden
		virtual bool IsHidden() const = 0;
		
		//IsVisible
		virtual bool IsVisible() const = 0;
		
		//IsEnabled
		virtual bool IsEnabled() const = 0;
		
		//IsDisabled
		virtual bool IsDisabled() const = 0;
		
		//TODO: IsContainer
		
		//SetFont
		virtual void SetFont(Font font) = 0;
		
		//GetFont
		virtual Font GetFont() const = 0;
		
		//SetLayout
		virtual void SetLayout(EdgePosition left, EdgePosition right, EdgePosition top, EdgePosition bottom) = 0;
		
		//Dock
		virtual void Dock(DockPosition dockMode) = 0;
		
		//SetFocus
		virtual void SetFocus() = 0;
		
		//HasFocus
		virtual bool HasFocus() const = 0;
		
		//GetHandle
		#ifdef WIN32
			virtual HWND GetHandle() const = 0;
		#elif defined(LINUX)
			virtual GtkWidget *GetHandle() const = 0;
			virtual GtkFixed *GetGtkFixed() const
			{
				return Null;
			}
		#elif defined(MACOS)
			//TODO: 
		#endif
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//SetParent
		template <typename WidgetType>
		inline void SetParent(WidgetType widget)
		{
			//TODO: Set parent
			//gtk_widget_set_parent(GTK_WIDGET(GetHandle()), GTK_WIDGET(widget->GetGtkFixed()));
			parent = widget;
			gtk_fixed_put(widget->GetGtkFixed(), GetHandle(), GetX(), GetY());
		}
		
		//GetParent
		inline Widget GetParent() const
		{
			return parent;
		}
		
	protected:
		Widget parent;
};

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif /*BLITZPROG_GUI_WIDGET_HPP_*/

#include <SFML/Window.hpp>
#include <bp/Core/String/C++/UTF8String.hpp>

#define BPSFVideoMode sf::VideoMode

/*class BPSFVideoMode: public sf::VideoMode {
	
};*/

class BPSFWindow: public sf::Window {
public:
	inline BPSFWindow(sf::VideoMode* vm, BPUTF8String* title) : sf::Window(*vm, title->data) {
		
	}
	
	inline bool GetEvent(sf::Event *event) {
		return sf::Window::GetEvent(*event);
	}
};

class BPSFEvent: public sf::Event {
public:
	inline bool isClosed() {
		return sf::Event::Type == sf::Event::Closed;
	}
};
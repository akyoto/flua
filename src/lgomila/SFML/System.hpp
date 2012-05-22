#include <SFML/System.hpp>

void bp_sfmlTest() {
	sf::Clock Clock;
	
	while(Clock.GetElapsedTime() < 5.f) {
		std::cout << Clock.GetElapsedTime() << std::endl;
		sf::Sleep(0.5f);
	}
}
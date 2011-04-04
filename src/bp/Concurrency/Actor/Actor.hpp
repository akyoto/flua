#ifndef bp_Actor_hpp
#define bp_Actor_hpp

#define THERON_USE_BOOST_THREADS 1

#include <Theron/Framework.h>
#include <Theron/Actor.h>
#include <Theron/Receiver.h>

Theron::Framework theronFramework;
Theron::Receiver theronReceiver;

inline void bp_waitActorMsg() {
	theronReceiver.Wait();
}

/*template <typename TClass>
inline Theron::ActorRef theronCreateActor() {
	std::cout << "Creating actor..." << std::endl;
	return theronFramework.CreateActor<TClass>();
}*/

#endif

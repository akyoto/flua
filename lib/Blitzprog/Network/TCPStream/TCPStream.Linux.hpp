////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Network.TCPStream.Linux
// Author:				Eduard Urbach
// Description:			Stream that uses the TCP/IP protocol
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_NETWORK_TCPSTREAM_LINUX_HPP_
#define BLITZPROG_NETWORK_TCPSTREAM_LINUX_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Stream/Stream.hpp>

//C++
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <signal.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <cerrno>

/*
#ifdef MACOS
	#include <sys/sockio.h>
#else
	#include <linux/sockios.h>
#endif
*/

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//SocketCanRead
inline bool SocketCanRead(int checkSocket, int timeoutMillis)
{
	//Socket set
	fd_set fdsRead;
	FD_ZERO(&fdsRead);
	FD_SET(checkSocket, &fdsRead);
	
	//Timeout
	struct timespec tsTimeout;
	tsTimeout.tv_sec  = timeoutMillis / 1000;
	tsTimeout.tv_nsec = (timeoutMillis % 1000) * 1000000;
	
	//Mask
	sigset_t signalMask;
	sigfillset(&signalMask);
	
	int result = pselect(checkSocket + 1, &fdsRead, Null, Null, &tsTimeout, &signalMask);
	EngineLog5("pselect result: " << result);
	
	if(result == -1)
	{
		EngineLogError("pselect error: " << errno);
	}
	
	return result == 1;
}

//SocketCanWrite
inline bool SocketCanWrite(int checkSocket, int timeoutMillis)
{
	//Socket set
	fd_set fdsWrite;
	FD_ZERO(&fdsWrite);
	FD_SET(checkSocket, &fdsWrite);
	
	//Timeout
	struct timespec tsTimeout;
	tsTimeout.tv_sec  = timeoutMillis / 1000;
	tsTimeout.tv_nsec = (timeoutMillis % 1000) * 1000000;
	
	//Mask
	sigset_t signalMask;
	sigfillset(&signalMask);
	
	int result = pselect(checkSocket + 1, Null, &fdsWrite, Null, &tsTimeout, &signalMask);
	EngineLog5("pselect result: " << result);
	
	if(result == -1)
	{
		EngineLogError("pselect error: " << errno);
	}
	
	return result == 1;
}

#endif /*BLITZPROG_NETWORK_TCPSTREAM_LINUX_HPP_*/

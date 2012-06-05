// C++
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

// bp
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>

// TODO: IPv6

inline int genericResolve(const char* hostname, struct sockaddr** addr, socklen_t* addr_len, int* af) {
	struct addrinfo hints;
	struct addrinfo *result;
	
	memset(&hints, 0, sizeof (struct addrinfo));
	hints.ai_family = AF_UNSPEC;
	
	getaddrinfo(hostname, NULL, &hints, &result);
	
	*addr = reinterpret_cast<struct sockaddr*>(GC_MALLOC(*addr_len = sizeof(result->ai_addrlen)));
	memcpy (*addr, result->ai_addr, result->ai_addrlen);
	*af = result->ai_family;
	
	freeaddrinfo(result);
	
	return true;
}

inline Int32 bp_getHostIP(BPUTF8String* hostName) {
	hostent *host = gethostbyname(hostName->_data);
	
	if(host == NULL)
		return 0;
	
	return (**(reinterpret_cast<struct in_addr **>(host->h_addr_list))).s_addr;
}

inline BPUTF8String* bp_intIPToString(Int32 intIP) {
	// TODO: IPv6
	char* buf = new (UseGC) char[INET_ADDRSTRLEN];
	inet_ntop(AF_INET, &intIP, buf, INET_ADDRSTRLEN);
	
	return _toString(buf);
}
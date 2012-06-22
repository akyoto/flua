// C++
#ifdef WIN32
	#include <windows.h>
	#include <winsock2.h>
	#include <sys/types.h>
	#include <signal.h>
	#include <cerrno>
#else
	#include <sys/types.h>
	#include <sys/socket.h>
	#include <sys/ioctl.h>
	#include <sys/select.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>
	#include <netdb.h>
	#include <signal.h>
	#include <net/if.h>
	#include <cerrno>
	
	#ifdef __APPLE__
		#include <sys/sockio.h>
	#else
		#include <linux/sockios.h>
	#endif
#endif

// bp
#include <bp/Core/String/UTF8String/C++/UTF8String.hpp>

// Macros
#define castIPv4(x) reinterpret_cast<struct sockaddr_in *>(x)
#define castIPv6(x) reinterpret_cast<struct sockaddr_in6 *>(x)

inline BPUTF8String* bp_IPv4ToString(Int32 intIP) {
	char* buf = new (UseGC) char[INET_ADDRSTRLEN];
	inet_ntop(AF_INET, &intIP, buf, INET_ADDRSTRLEN);
	
	return _toString(buf);
}

inline BPUTF8String* bp_IPv6ToString(uint8_t* ptr) {
	char* buf = new (UseGC) char[INET6_ADDRSTRLEN];
	inet_ntop(AF_INET6, &ptr, buf, INET6_ADDRSTRLEN);
	
	return _toString(buf);
}

// IPInfo
class BPIPInfo: public gc {
public:
	inline BPUTF8String* toUTF8String() {
		if(af == AF_INET) {
			return bp_IPv4ToString(castIPv4(addr)->sin_addr.s_addr);
		} else {
			return bp_IPv6ToString(castIPv6(addr)->sin6_addr.s6_addr);
		}
	}
	
	inline int createTCPSocket() {
		if(af == AF_INET6)
			return socket(PF_INET6, SOCK_STREAM, IPPROTO_TCP);
		else
			return socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
	}
	
	inline int createUDPSocket() {
		if(af == AF_INET6)
			return socket(PF_INET6, SOCK_DGRAM, IPPROTO_UDP);
		else
			return socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP);
	}
	
	inline bool connect(int sock, short port) {
		// Copy it for thread-safety
		struct sockaddr localAddr = *addr;
		
		// Set port
		if(af == AF_INET6)
			castIPv6(&localAddr)->sin6_port = htons(port); // TODO: Is htons correct for IPv6?
		else
			castIPv4(&localAddr)->sin_port = htons(port);
		
		// Connect
		return ::connect(sock, &localAddr, addrLen) != -1;
	}
	
	// Members
	struct sockaddr* addr;
	socklen_t addrLen;
	int af;
};

inline bool genericResolve(const char* hostname, struct sockaddr** addr, socklen_t* addr_len, int* af) {
	struct addrinfo hints;
	struct addrinfo *result;
	int error;
	
	memset(&hints, 0, sizeof (struct addrinfo));
	hints.ai_family = AF_UNSPEC;
	
	error = getaddrinfo(hostname, NULL, &hints, &result);
	
	if(error != 0)
		return false;
	
	*addr = reinterpret_cast<struct sockaddr*>(GC_MALLOC(*addr_len = result->ai_addrlen)); //sizeof(result->ai_addrlen)
	memcpy(*addr, result->ai_addr, result->ai_addrlen);
	*af = result->ai_family;
	
	freeaddrinfo(result);
	
	return true;
}

// bp_getHostIP
inline BPIPInfo* bp_getHostIP(BPUTF8String* hostName) {
	BPIPInfo* ipInfo = new (UseGC) BPIPInfo();
	
	if(!genericResolve(hostName->_data, &ipInfo->addr, &ipInfo->addrLen, &ipInfo->af)) {
		return NULL;	
	}
	
	return ipInfo;
}

#ifdef _WIN32

#else

// socketCanRead
inline bool socketCanRead(int checkSocket, int timeoutMillis) {
	// Socket set
	fd_set fdsRead;
	FD_ZERO(&fdsRead);
	FD_SET(checkSocket, &fdsRead);
	
	// Timeout
	struct timespec tsTimeout;
	tsTimeout.tv_sec  = timeoutMillis / 1000;
	tsTimeout.tv_nsec = (timeoutMillis % 1000) * 1000000;
	
	// Mask
	sigset_t signalMask;
	sigfillset(&signalMask);
	
	int result = pselect(checkSocket + 1, &fdsRead, NULL, NULL, &tsTimeout, &signalMask);
	
	if(result == -1) {
		std::cout << "pselect error: " << strerror(errno);
	}
	
	return result == 1;
}

// socketCanWrite
inline bool socketCanWrite(int checkSocket, int timeoutMillis) {
	// Socket set
	fd_set fdsWrite;
	FD_ZERO(&fdsWrite);
	FD_SET(checkSocket, &fdsWrite);
	
	// Timeout
	struct timespec tsTimeout;
	tsTimeout.tv_sec  = timeoutMillis / 1000;
	tsTimeout.tv_nsec = (timeoutMillis % 1000) * 1000000;
	
	// Mask
	sigset_t signalMask;
	sigfillset(&signalMask);
	
	int result = pselect(checkSocket + 1, NULL, &fdsWrite, NULL, &tsTimeout, &signalMask);
	
	if(result == -1) {
		std::cout << "pselect error: " << strerror(errno);
	}
	
	return result == 1;
}

#endif
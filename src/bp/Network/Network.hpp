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
			return bp_IPv4ToString(reinterpret_cast<struct sockaddr_in *>(addr)->sin_addr.s_addr);
		} else {
			return bp_IPv6ToString(reinterpret_cast<struct sockaddr_in6 *>(addr)->sin6_addr.s6_addr);
		}
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
	
	*addr = reinterpret_cast<struct sockaddr*>(GC_MALLOC(*addr_len = sizeof(result->ai_addrlen)));
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

/*inline Int32 bp_getHostIPv4(BPUTF8String* hostName) {
	hostent *host = gethostbyname(hostName->_data);
	
	if(host == NULL)
		return 0;
	
	return (**(reinterpret_cast<struct in_addr **>(host->h_addr_list))).s_addr;
}*/
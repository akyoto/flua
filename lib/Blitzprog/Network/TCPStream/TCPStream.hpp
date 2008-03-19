////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Network.TCPStream
// Author:				Eduard Urbach
// Description:			Stream that uses the TCP/IP protocol
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_NETWORK_TCPSTREAM_HPP_
#define BLITZPROG_NETWORK_TCPSTREAM_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Math/Math.hpp>

//Others
#ifdef WIN32
	#include "TCPStream.Win32.hpp"
#elif defined(LINUX)
	#include "TCPStream.Linux.hpp"
#elif defined(MACOS)
	#include "TCPStream.MacOS.hpp"
#endif

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//SD
#define SD_BOTH 2

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//GetErrorDescriptionSocket
CharString GetErrorDescriptionSocket(int error);

//GetErrorDescriptionConnect
CharString GetErrorDescriptionConnect(int error);

//GetErrorDescriptionBind
CharString GetErrorDescriptionBind(int error);

//GetErrorDescriptionGetSockName
CharString GetErrorDescriptionGetSockName(int error);

//GetErrorDescriptionRecv
CharString GetErrorDescriptionRecv(int error);

//GetErrorDescriptionSend
CharString GetErrorDescriptionSend(int error);

//GetErrorDescriptionGetHost
CharString GetErrorDescriptionGetHost(int error);

//GetErrorDescriptionListen
CharString GetErrorDescriptionListen(int error);

//GetErrnoDescriptionSocket
inline String GetErrnoDescriptionSocket()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionSocket(errno);
}

//GetErrnoDescriptionConnect
inline String GetErrnoDescriptionConnect()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionConnect(errno);
}

//GetErrnoDescriptionBind
inline String GetErrnoDescriptionBind()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionBind(errno);
}

//GetErrnoDescriptionGetSockName
inline String GetErrnoDescriptionGetSockName()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionGetSockName(errno);
}

//GetErrnoDescriptionRecv
inline String GetErrnoDescriptionRecv()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionRecv(errno);
}

//GetErrnoDescriptionSend
inline String GetErrnoDescriptionSend()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionSend(errno);
}

//GetErrnoDescriptionGetHost
inline String GetErrnoDescriptionGetHost()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionGetHost(h_errno);
}

//GetErrnoDescriptionListen
inline String GetErrnoDescriptionListen()
{
	return String(strerror(errno)) + ": " + GetErrorDescriptionListen(h_errno);
}

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//IP
class TIP: public TPrintable
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TIP()
		{
			
		}
		
		//Constructor
		TIP(CharString stringIP)
		{
			if(inet_pton(AF_INET, stringIP, &ip) == 0)
			{
				hostent *host = gethostbyname(stringIP);
				
				if(host == Null)
				{
					EngineLogError("Failed to resolve host name " << stringIP << " -> " << GetErrnoDescriptionGetHost());
					ip = 0;
					return;
				}
				
				ip = (**(reinterpret_cast<struct in_addr **>(host->h_addr_list))).s_addr;
				
				EngineLog3("host2ip: " << stringIP << " -> " << ToString());
			}
		}
		
		//Constructor
		TIP(String &stringIP)
		{
			if(inet_pton(AF_INET, stringIP, &ip) == 0)
			{
				hostent *host = gethostbyname(stringIP);
				
				if(host == Null)
				{
					EngineLogError("Failed to resolve host name " << stringIP << " -> " << GetErrnoDescriptionGetHost());
					ip = 0;
					return;
				}
				
				ip = (**(reinterpret_cast<struct in_addr **>(host->h_addr_list))).s_addr;
				
				EngineLog3("host2ip: " << stringIP << " -> " << ToString());
			}
		}
		
		//Constructor
		TIP(int32 intIP) : ip(intIP)
		{
			
		}
		
		//Destructor
		~TIP()
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator: =
		inline void operator=(int32 intIP)
		{
			ip = intIP;
		}
		
		//Operator: ->
		inline TIP *operator->()
		{
			return this;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: int32
		inline operator int32()
		{
			return ip;
		}
		
		//Cast: String
		inline operator String()
		{
			return ToString();
		}
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////

		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//ToInt
		inline int32 ToInt()
		{
			return ip;
		}
		
		//ToString
		inline String ToString() const
		{
			//NOTE: IPv4
			char buf[16];
			inet_ntop(AF_INET, &ip, buf, 16);
			return buf;
		}
		
	public:
		int32 ip;
};
typedef TIP IP;

//SharedPtr
class TTCPStream;
typedef SharedPtr<TTCPStream> TCPStream;

//TCPStream
class TTCPStream: public TStream
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TTCPStream() : TStream("")
		{
			//Debug info
			EngineLogNew("TCPStream");
			
			//TODO: IPv6
			if((mySocket = socket(AF_INET, SOCK_STREAM, 0)) == -1)
			{
				EngineLogError("Failed to create a TCP stream. " << GetErrnoDescriptionSocket());
			}
			
			int size = (1 << 16) - 1;
			if(	setsockopt(mySocket, SOL_SOCKET, SO_RCVBUF, &size, 4) == -1 || \
				setsockopt(mySocket, SOL_SOCKET, SO_SNDBUF, &size, 4) == -1)
			{
				this->Close();
			}
		}
		
		//Destructor
		~TTCPStream()
		{
			//Debug info
			EngineLogDelete("TCPStream");
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

		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Open
		inline void Open(const String &url)
		{
			
		}
		
		//Close
		inline void Close()
		{
			if(mySocket != -1)
			{
				shutdown(mySocket, SD_BOTH);
				#ifdef WIN32
					closesocket(mySocket);
				#else
					close(mySocket);
				#endif
				mySocket = -1;
			}
		}
		
		//Eof
		inline bool Eof()
		{
			if(readPos < bytesCollected)
				return false;
			
			Reset();
			return true;
		}
		
		//Flush
		inline void Flush()
		{
			
		}
		
		//SetPosition
		inline void SetPosition(streampos positionInBytes)
		{
			readPos = positionInBytes;
		}
		
		//GetPosition
		inline streampos GetPosition()
		{
			return readPos;
		}
		
		//WriteBytes
		inline void WriteBytes(const char *bytes, int count)
		{
			sendString.append(bytes, count);
		}
		
		//WriteBytes
		inline void WriteBytes(byte *bytes, int count)
		{
			this->WriteBytes(reinterpret_cast<const char*>(bytes), count);
		}
		
		//ReadBytes
		inline streamsize ReadBytes(char *bytes, int count)
		{
			MemCopy(recvString.data() + readPos, bytes, count);
			readPos += count;
			if(readPos < bytesCollected)
				return count;
			
			return count - (readPos - bytesCollected);	//TODO: Check this (+ 1 ?)
		}
		
		//WriteLine
		inline void WriteLine(const String &str)
		{
			sendString += str;
			sendString += "\r\n";
		}
		
		//ReadLine
		inline void ReadLine(String &var)
		{
			size_t nlPosR = recvString.find('\r', readPos);
			size_t nlPosN = recvString.find('\n', readPos);
			
			size_t nlPos = Min(nlPosN, nlPosR);
			
			if(nlPos == CPPString::npos)
			{
				EngineLog5("Trying to find \\0");
				if((nlPos = recvString.find('\0', readPos)) == CPPString::npos)
				{
					EngineLog5("End of string.");
					nlPos = recvString.length() - 1;
				}
			}
			
			var = recvString.substr(readPos, nlPos - readPos);
			readPos = nlPos + 1 + (recvString[nlPos + 1] == '\n');
		}
		
		//ReadLine
		inline String ReadLine()
		{
			String line;
			this->ReadLine(line);
			return line;
		}
		
		// Network functions //
		
		//SetLocalPort
		inline bool SetLocalPort(short port)
		{
			sockaddr_in addr;
			
			//Bind to port
			if(bind(mySocket, reinterpret_cast<sockaddr*>(&addr), port) == -1)
			{
				EngineLogError("Could not bind socket to port " << port << ". " << GetErrnoDescriptionBind());
				return false;
			}
			
			socklen_t nameLen = 16;
			
			//Get socket name
			if(getsockname(mySocket, reinterpret_cast<sockaddr*>(&addr), &nameLen) == -1)
			{
				EngineLogError("Failed to get the socket name. " << GetErrnoDescriptionGetSockName());
				return false;
			}
			
			localIP = ntohl(addr.sin_addr.s_addr);
			localPort = ntohs(addr.sin_port);
			
			return true;
		}
		
		//SetRemotePort
		inline void SetRemotePort(short port)
		{
			remotePort = port;
		}
		
		//SetRemoteIP
		inline void SetRemoteIP(IP ip)
		{
			remoteIP = ip;
		}
		
		//SetHost
		inline void SetHost(String wwwHost)
		{
			remoteIP = wwwHost;
		}
		
		//GetLocalIP
		inline IP GetLocalIP()
		{
			return localIP;
		}
		
		//GetLocalPort
		inline short GetLocalPort()
		{
			return localPort;
		}
		
		//GetRemoteIP
		inline IP GetRemoteIP()
		{
			return remoteIP;
		}
		
		//GetRemotePort
		inline short GetRemotePort()
		{
			return remotePort;
		}
		
		//Connect
		inline bool Connect()
		{
			sockaddr_in addr;
			addr.sin_family = AF_INET;
			addr.sin_port = htons(remotePort);
			addr.sin_addr.s_addr = remoteIP;
			
			if(connect(mySocket, reinterpret_cast<sockaddr*>(&addr), sizeof(sockaddr)) == -1)
			{
				EngineLogError("Connect() function failed. " << remoteIP << " @" << remotePort << " -> " << GetErrnoDescriptionConnect());
				return false;
			}
			
			return true;
		}
		
		//Listen
		inline bool Listen(int maxClients = 32)
		{
			if(listen(mySocket, maxClients) == -1)
			{
				EngineLogError("Listen() function failed. Port: " << localPort << " -> " << GetErrnoDescriptionListen());
				return false;
			}
			
			return true;
		}
		
		//Accept
		inline TCPStream Accept()
		{
			if(!SocketCanRead(mySocket, acceptTimeout))
				return Null;
			
			sockaddr_in addr;
			socklen_t addrLen = sizeof(addr);
			int clientSocket;
			
			if((clientSocket = accept(mySocket, reinterpret_cast<sockaddr*>(&addr), &addrLen)) == -1)
			{
				EngineLogError("Accept() function failed. Port: " << localPort); //TODO: GetErrnoDescriptionAccept()
				return Null;
			}
			
			TCPStream client = new TTCPStream();
			client->mySocket = clientSocket;
			client->localIP = ntohl(addr.sin_addr.s_addr);
			client->localPort = ntohs(addr.sin_port);
			
			addrLen = sizeof(addr);
			if(getsockname(mySocket, reinterpret_cast<sockaddr*>(&addr), &addrLen) == -1)
			{
				EngineLogError("Failed to get the socket name. " << GetErrnoDescriptionGetSockName());
				client->Close();
				return Null;
			}
			
			client->remoteIP = ntohl(addr.sin_addr.s_addr);
			client->remotePort = ntohs(addr.sin_port);
			
			return client;
		}
		
		//RecvMsg
		inline int RecvMsg()
		{
			EngineLog4("Check RecvMsg #1");
			if(!SocketCanRead(mySocket, recvTimeout))
			{
				bytesCollected = 0;
				return 0;
			}
			
			EngineLog4("Check RecvMsg #2");
			int size;
			if(ioctl(mySocket, FIONREAD, &size) == -1)
				return 0;
			
			EngineLog4("Check RecvMsg #3");
			if(size <= 0)
				return 0;
			
			if(recvString.length() < bytesCollected + static_cast<size_t>(size))
			{
				EngineLog3("Resizing buffer: " << bytesCollected << " + " << size << " = " << bytesCollected + size << " bytes.");
				recvString.resize(bytesCollected + size);
			}
			
			EngineLog3("Receiving data...");
			int bytesReceived = recv(mySocket, const_cast<char*>(recvString.data()) + bytesCollected, size, 0);
			EngineLog3("Received " << bytesReceived << " bytes.");
			
			if(bytesReceived == -1)
			{
				EngineLogError("recv() failed: " << GetErrnoDescriptionRecv());
				return 0;
			}
			
			if(bytesReceived == 0)
			{
				EngineLogError("Disconnected");
				return 0;
			}
			
			bytesCollected += bytesReceived;
			return bytesReceived;
		}
		
		//SendMsg
		inline int SendMsg()
		{
			EngineLog4("Check SendMsg #1");
			if(sendString.length() == 0)
				return 0;
			
			EngineLog4("Check SendMsg #2");
			if(!SocketCanWrite(mySocket, sendTimeout))
				return 0;
			
			EngineLog3("Sending data...");
			int bytesSent = send(mySocket, sendString.c_str(), sendString.length(), 0);
			EngineLog3("Sent.");
			
			if(bytesSent == -1)
			{
				EngineLogError("send() failed: " << GetErrnoDescriptionSend());
				return 0;
			}
			
			sendString.erase(0, bytesSent);
			
			return bytesSent;
		}
		
		//SendAll
		inline void SendAll()
		{
			while(this->SendMsg());
		}
		
		//RecvAll
		inline void RecvAll()
		{
			while(this->RecvMsg());
		}
		
		//SetTimeouts
		inline void SetTimeouts(int timeout)
		{
			recvTimeout = timeout;
			sendTimeout = timeout;
			acceptTimeout = timeout;
		}
		
		//SetTimeouts
		inline void SetTimeouts(int timeoutRecv, int timeoutSend)
		{
			recvTimeout = timeoutRecv;
			sendTimeout = timeoutSend;
		}
		
		//SetTimeouts
		inline void SetTimeouts(int timeoutRecv, int timeoutSend, int timeoutAccept)
		{
			recvTimeout = timeoutRecv;
			sendTimeout = timeoutSend;
			acceptTimeout = timeoutAccept;
		}
		
		//GetAvail
		inline int GetAvail()
		{
			int avail;
			
			if(ioctl(mySocket, FIONREAD, &avail) == -1)
			{
				EngineLogError("Socket error");
				return -1;
			}
			
			return avail;
		}
		
		//GetState
		inline bool GetState()
		{
			if(SocketCanRead(mySocket, 0))
			{
				if(GetAvail() > 0)
						return true;
				
				this->Close();
				return false;
			}
			
			this->Close();
			return false;
		}
		
		//GetBuffer
		inline const char *GetBuffer() const
		{
			return recvString.data();
		}
		
		//GetBufferSize
		inline size_t GetBufferSize() const
		{
			return recvString.length();
		}
		
		//ResizeBuffer
		inline void ResizeBuffer(size_t size)
		{
			recvString.resize(size);
		}
		
		//Reset
		inline void Reset()
		{
			readPos = 0;
			bytesCollected = 0;
			recvString.resize(0);
			sendString.resize(0);
		}
		
	protected:
		int mySocket;
		short localPort;
		short remotePort;
		IP localIP;
		IP remoteIP;
		int recvTimeout;
		int sendTimeout;
		int acceptTimeout;
		CPPString sendString;
		CPPString recvString;
		size_t bytesCollected;
		size_t readPos;
};
#define CreateTCPStream new TTCPStream

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//GetHostIP
inline IP GetHostIP(String hostName)
{
	hostent *host = gethostbyname(hostName);
	
	if(host == Null)
	{
		EngineLogError("Failed to resolve host name " << hostName << " -> " << GetErrnoDescriptionGetHost());
		return 0;
	}
	
	return (**(reinterpret_cast<struct in_addr **>(host->h_addr_list))).s_addr;
}

//GetHostName
inline String GetHostName(IP ip)
{
	hostent *host = gethostbyaddr(&ip.ip, 4, AF_INET);
	
	if(host == Null)
	{
		EngineLogError("Failed to resolve host ip " << ip->ToString() << " -> " << GetErrnoDescriptionGetHost());
		return "";
	}
	
	return host->h_name;
}

//Operator << (ostream, IP)
inline std::ostream &operator<<(std::ostream &stream, IP ip)
{
	return stream << ip.ToString();
}

#endif /*BLITZPROG_NETWORK_TCPSTREAM_HPP_*/

#include "TCPStream.hpp"

/*
 * Error descriptions from http://www.opengroup.org
 * */

//TODO: Add error descriptions for other functions

//GetErrorDescriptionSocket
CharString GetErrorDescriptionSocket(int error)
{
	switch(error)
	{
		case EAFNOSUPPORT:
			return "The implementation does not support the specified address family.";
		case EMFILE:
			return "No more file descriptors are available for this process.";
		case ENFILE:
			return "No more file descriptors are available for the system.";
		case EPROTONOSUPPORT:
			return "The protocol is not supported by the address family, or the protocol is not supported by the implementation.";
		case EPROTOTYPE:
			return "The socket type is not supported by the protocol.";
		case EACCES:
			return "The process does not have appropriate privileges.";
		case ENOBUFS:
			return "Insufficient resources were available in the system to perform the operation.";
		case ENOMEM:
			return "Insufficient memory was available to fulfill the request. ";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionConnect
CharString GetErrorDescriptionConnect(int error)
{
	switch(error)
	{
		case EADDRNOTAVAIL:
			return "The specified address is not available from the local machine.";
		case EAFNOSUPPORT:
			return "The specified address is not a valid address for the address family of the specified socket.";
		case EALREADY:
			return "A connection request is already in progress for the specified socket.";
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case ECONNREFUSED:
			return "The target address was not listening for connections or refused the connection request.";
		case EINPROGRESS:
			return "O_NONBLOCK is set for the file descriptor for the socket and the connection cannot be immediately established; the connection shall be established asynchronously.";
		case EINTR:
			return "The attempt to establish a connection was interrupted by delivery of a signal that was caught; the connection shall be established asynchronously.";
		case EISCONN:
			return "The specified socket is connection-mode and is already connected.";
		case ENETUNREACH:
			return "No route to the network is present.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EPROTOTYPE:
			return "The specified address has a different type than the socket bound to the specified peer address.";
		case ETIMEDOUT:
			return "The attempt to connect timed out before a connection was made.";
		case EIO:
			return "An I/O error occurred while reading from or writing to the file system.";
		case ELOOP:
			return "A loop exists in symbolic links encountered during resolution of the pathname in address.";
		case ENAMETOOLONG:
			return "A component of a pathname exceeded {NAME_MAX} characters, or an entire pathname exceeded {PATH_MAX} characters.";
		case ENOENT:
			return "A component of the pathname does not name an existing file or the pathname is an empty string.";
		case ENOTDIR:
			return "A component of the path prefix of the pathname in address is not a directory.";
		case EACCES:
			return "Search permission is denied for a component of the path prefix; or write access to the named socket is denied.";
		case EADDRINUSE:
			return "Attempt to establish a connection that uses addresses that are already in use.";
		case ECONNRESET:
			return "Remote host reset the connection request.";
		case EHOSTUNREACH:
			return "The destination host cannot be reached (probably because the host is down or a remote router cannot reach it).";
		case EINVAL:
			return "The address_len argument is not a valid length for the address family; or invalid address family in the sockaddr structure.";
		//case ELOOP:
		//	return "More than {SYMLOOP_MAX} symbolic links were encountered during resolution of the pathname in address.";
		//case ENAMETOOLONG:
		//	return "Pathname resolution of a symbolic link produced an intermediate result whose length exceeds {PATH_MAX}.";
		case ENETDOWN:
			return "The local network interface used to reach the destination is down.";
		case ENOBUFS:
			return "No buffer space is available.";
		case EOPNOTSUPP:
			return "The socket is listening and cannot be connected.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionBind
CharString GetErrorDescriptionBind(int error)
{
	switch(error)
	{
		case EADDRINUSE:
			return "The specified address is already in use.";
		case EADDRNOTAVAIL:
			return "The specified address is not available from the local machine.";
		case EAFNOSUPPORT:
			return "The specified address is not a valid address for the address family of the specified socket.";
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case EINVAL:
			return "The socket is already bound to an address, and the protocol does not support binding to a new address; or the socket has been shut down.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EOPNOTSUPP:
			return "The socket type of the specified socket does not support binding to an address.";
		case EACCES:
			return "A component of the path prefix denies search permission, or the requested name requires writing in a directory with a mode that denies write permission.";
		case EDESTADDRREQ:
		case EISDIR:
			return "The address argument is a null pointer.";
		case EIO:
			return "An I/O error occurred.";
		case ELOOP:
			return "A loop exists in symbolic links encountered during resolution of the pathname in address.";
		case ENAMETOOLONG:
			return "A component of a pathname exceeded {NAME_MAX} characters, or an entire pathname exceeded {PATH_MAX} characters.";
		case ENOENT:
			return "A component of the pathname does not name an existing file or the pathname is an empty string.";
		case ENOTDIR:
			return "A component of the path prefix of the pathname in address is not a directory.";
		case EROFS:
			return "The name would reside on a read-only file system.";
		//case EACCES:
		//	return "The specified address is protected and the current user does not have permission to bind to it.";
		//case EINVAL:
		//	return "The address_len argument is not a valid length for the address family.";
		case EISCONN:
			return "The socket is already connected.";
		//case ELOOP:
		//	return "More than {SYMLOOP_MAX} symbolic links were encountered during resolution of the pathname in address.";
		//case ENAMETOOLONG:
		//	return "Pathname resolution of a symbolic link produced an intermediate result whose length exceeds {PATH_MAX}.";
		case ENOBUFS:
			return "Insufficient resources were available to complete the call.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionGetSockName
CharString GetErrorDescriptionGetSockName(int error)
{
	switch(error)
	{
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EOPNOTSUPP:
			return "The operation is not supported for this socket's protocol.";
		case EINVAL:
			return "The socket has been shut down.";
		case ENOBUFS:
			return "Insufficient resources were available in the system to complete the function.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionRecv
CharString GetErrorDescriptionRecv(int error)
{
	switch(error)
	{
		case EAGAIN:
		//case EWOULDBLOCK:
			return "The socket's file descriptor is marked O_NONBLOCK and no data is waiting to be received; or MSG_OOB is set and no out-of-band data is available and either the socket's file descriptor is marked O_NONBLOCK or the socket does not support blocking to await out-of-band data.";
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case ECONNRESET:
			return "A connection was forcibly closed by a peer.";
		case EINTR:
			return "The recv() function was interrupted by a signal that was caught, before any data was available.";
		case EINVAL:
			return "The MSG_OOB flag is set and no out-of-band data is available.";
		case ENOTCONN:
			return "A receive is attempted on a connection-mode socket that is not connected.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EOPNOTSUPP:
			return "The specified flags are not supported for this socket type or protocol.";
		case ETIMEDOUT:
			return "The connection timed out during connection establishment, or due to a transmission timeout on active connection.";
		case EIO:
			return "An I/O error occurred while reading from or writing to the file system.";
		case ENOBUFS:
			return "Insufficient resources were available in the system to perform the operation.";
		case ENOMEM:
			return "Insufficient memory was available to fulfill the request.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionSend
CharString GetErrorDescriptionSend(int error)
{
	switch(error)
	{
		case EAGAIN:
		//case EWOULDBLOCK:
			return "The socket's file descriptor is marked O_NONBLOCK and the requested operation would block.";
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case ECONNRESET:
			return "A connection was forcibly closed by a peer.";
		case EDESTADDRREQ:
			return "The socket is not connection-mode and no peer address is set.";
		case EINTR:
			return "A signal interrupted send() before any data was transmitted.";
		case EMSGSIZE:
			return "The message is too large to be sent all at once, as the socket requires.";
		case ENOTCONN:
			return "The socket is not connected or otherwise has not had the peer pre-specified.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EOPNOTSUPP:
			return "The socket argument is associated with a socket that does not support one or more of the values set in flags.";
		case EPIPE:
			return "The socket is shut down for writing, or the socket is connection-mode and is no longer connected. In the latter case, and if the socket is of type SOCK_STREAM, the SIGPIPE signal is generated to the calling thread.";
		case EACCES:
			return "The calling process does not have the appropriate privileges.";
		case EIO:
			return "An I/O error occurred while reading from or writing to the file system.";
		case ENETDOWN:
			return "The local network interface used to reach the destination is down.";
		case ENETUNREACH:
			return "No route to the network is present.";
		case ENOBUFS:
			return "Insufficient resources were available in the system to perform the operation.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionGetHost
CharString GetErrorDescriptionGetHost(int error)
{
	switch(error)
	{
		case HOST_NOT_FOUND:
			return "No such host is known.";
		case NO_DATA:
			return "The server recognised the request and the name but no address is available. Another type of request to the name server for the domain might return an answer.";
		case NO_RECOVERY:
			return "An unexpected server failure occurred which can not be recovered.";
		case TRY_AGAIN:
			return "A temporary and possibly transient error occurred, such as a failure of a server to respond.";
		default:
			return "Unknown error.";
	}
}

//GetErrorDescriptionListen
CharString GetErrorDescriptionListen(int error)
{
	switch(error)
	{
		case EBADF:
			return "The socket argument is not a valid file descriptor.";
		case EDESTADDRREQ:
			return "The socket is not bound to a local address, and the protocol does not support listening on an unbound socket.";
		case EINVAL:
			return "The socket is either already connected or it has been shut down.";
		case ENOTSOCK:
			return "The socket argument does not refer to a socket.";
		case EOPNOTSUPP:
			return "The socket protocol does not support listen().";
		case EACCES:
			return "The calling process does not have the appropriate privileges.";
		case ENOBUFS:
			return "Insufficient resources are available in the system to complete the call.";
		default:
			return "Unknown error.";
	}
}

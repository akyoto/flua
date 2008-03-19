#include "Network.hpp"

//Download
bool Download(String url, String toFile, int timeout, short port)
{
	if(url.StartsWith("http://"))
	{
		url.EraseLeft(7);
	}
	
	String host = url.Until('/');
	String path = url.From('/');
	
	TCPStream stream = CreateTCPStream();
	stream->SetTimeouts(timeout, timeout);
	stream->SetRemoteIP(host);
	stream->SetRemotePort(port);
	
	if(stream->GetRemoteIP() == 0)
		return false;
	
	EngineLog3("Trying to connect to " << stream->GetRemoteIP() << "...");
	if(!stream->Connect())
	{
		EngineLogError("Can't connect to " << stream->GetRemoteIP());
		return false;
	}
	EngineLog3("Connected.");
	
	EngineLog3("Sending HTTP query...");
	stream->WriteLine("GET " + path + " HTTP/1.0");	//TODO: Update to HTTP/1.1
	stream->WriteLine("Host: " + host);
	stream->WriteLine("Connection: close");
	stream->WriteLine("");
	stream->SendAll();
	EngineLog3("Sent.");
	
	EngineLog3("Waiting for messages...");
	int startWaiting = MilliSecs();
	int avail;
	while((avail = stream->GetAvail()) == 0)
	{
		Delay(1);
		if(MilliSecs() - startWaiting > timeout)
		{
			EngineLogError("Timeout");
			return false;
		}
	}
	EngineLog3("Done. " << avail << " bytes available in the first package.");
	
	EngineLog3("Receiving...");
	stream->RecvAll();
	EngineLog3("Received.");
	
	String line = "-";
	if(toFile.IsEmpty() && (toFile = StripDir(url)).IsEmpty())
	{
		EngineLog3("Reading HTTP response...");
		while(!stream->Eof() && line != "")
		{
			stream->ReadLine(line);
			if(line.StartsWith("Content-Type:"))
			{
				toFile = "index." + line.Mid(14).From('/', 1);
			}
			EngineLog3(line);
		}
		EngineLog3("Done.");
		
		if(toFile.IsEmpty())
			toFile = "index.html";
	}
	else
	{
		EngineLog3("Ignoring HTTP response...");
		while(!stream->Eof() && line != "")
		{
			stream->ReadLine(line);
			EngineLog3(line);
		}
		EngineLog3("Done.");
	}
	
	EngineLog3("Writing content to file " << toFile << "...");
	FileWriteStream fileStream = CreateFileWriteStream(toFile);
	fileStream->WriteStreamContent(stream);
	EngineLog3("Written.");
	
	return true;
}

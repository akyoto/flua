////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.FileSystem
// Author:				Eduard Urbach
// Description:			-
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_FILESYSTEM_HPP_
#define BLITZPROG_FILESYSTEM_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/Stream/Stream.hpp>
#include <Blitzprog/Collection/Array/Array.hpp>

//C++
#include <fstream>
#include <cerrno>
#include <sys/stat.h>
#include <dirent.h>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//FileWriteStream
class TFileWriteStream: public TStream, public CPPOFStream
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TFileWriteStream(const String &url) : TStream(url), CPPOFStream(url.ToCharString())
		{
			EngineLogNew("FileWriteStream: " << streamURL);
		}
		
		//Destructor
		~TFileWriteStream()
		{
			EngineLogDelete("FileWriteStream: " << streamURL);
			this->Close();
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

		//Open
		inline void Open(const String &url)
		{
			this->open(url.ToCharString());
		}
		
		//Close
		inline void Close()
		{
			this->close();
		}
		
		//Eof
		inline bool Eof()
		{
			return this->eof();
		}
		
		//Flush
		inline void Flush()
		{
			this->flush();
		}
		
		//SetPosition
		inline void SetPosition(streampos posInBytes)
		{
			this->seekp(posInBytes);
		}
		
		//GetPosition
		inline streampos GetPosition()
		{
			return this->tellp();
		}
				
		//WriteBytes
		inline void WriteBytes(const char *bytes, int count)
		{
			this->write(bytes, count);
		}
		
		//WriteBytes
		inline void WriteBytes(byte *bytes, int count)
		{
			this->WriteBytes(reinterpret_cast<const char*>(bytes), count);
		}
		
		//ReadBytes
		inline streamsize ReadBytes(char *bytes, int count)
		{
			return 0;
		}
		
		//WriteLine
		inline void WriteLine(const String &str)
		{
			*this << str << '\n';	//TODO: " or '
		}
		
		//ReadLine
		inline void ReadLine(String &var)
		{
			
		}
		
		//ReadLine
		inline String ReadLine()
		{
			return "";
		}
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		
		
	protected:
		
};
typedef SharedPtr<TFileWriteStream> FileWriteStream;
#define CreateFileWriteStream new TFileWriteStream

//FileReadStream
class TFileReadStream: public TStream, public CPPIFStream
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TFileReadStream(const String &url) : TStream(url), CPPIFStream(url.ToCharString())
		{
			//TODO: FileNotFoundException(url);
			if(!(*this))
				this->setstate(this->rdstate() | eofbit);
		}
		
		//Destructor
		~TFileReadStream()
		{
			this->Close();
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

		//Open
		inline void Open(const String &url)
		{
			this->open(url.ToCharString());
		}
		
		//Close
		inline void Close()
		{
			this->close();
		}
		
		//Eof
		inline bool Eof()
		{
			return this->eof();
		}
		
		//Flush
		inline void Flush()
		{
			
		}
		
		//SetPosition
		inline void SetPosition(streampos posInBytes)
		{
			this->seekg(posInBytes);
		}
		
		//GetPosition
		inline streampos GetPosition()
		{
			return this->tellg();
		}
				
		//WriteBytes
		inline void WriteBytes(const char *bytes, int count)
		{
			
		}
		
		//WriteBytes
		inline void WriteBytes(byte *bytes, int count)
		{
			
		}
		
		//ReadBytes
		inline streamsize ReadBytes(char *bytes, int count)
		{
			this->read(bytes, count);
			return this->gcount();
		}
		
		//WriteLine
		inline void WriteLine(const String &str)
		{
			
		}
		
		//ReadLine
		inline void ReadLine(String &var)
		{
			std::getline(*this, var);
		}
		
		//ReadLine
		inline String ReadLine()
		{
			String line;
			std::getline(*this, line);
			return line;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		
		
	protected:
		
};
typedef SharedPtr<TFileReadStream> FileReadStream;
#define CreateFileReadStream new TFileReadStream

/*
//TODO: There ist a bug because FileStream overwrites the existing file (FileWriteStream)
//FileStream
class TFileStream: public TFileWriteStream, public TFileReadStream
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TFileStream(const String &fileName) : TFileWriteStream(fileName), TFileReadStream(fileName)
		{
			//Debug info
			EngineLogNew("FileStream: " << fileName);
		}
		
		//Destructor
		~TFileStream()
		{
			//Debug info
			EngineLogDelete("FileStream: " << TFileWriteStream::streamURL);
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
			TFileWriteStream::Open(url.ToCharString());
			TFileReadStream::Open(url.ToCharString());
		}
		
		//Close
		inline void Close()
		{
			TFileWriteStream::Close();
			TFileReadStream::Close();
		}
		
		//Eof
		inline bool Eof()
		{
			return TFileReadStream::Eof();
		}
		
		//Flush
		inline void Flush()
		{
			TFileWriteStream::Flush();
		}
		
		//SetPosition
		inline void SetPosition(size_t posInBytes)
		{
			TFileWriteStream::SetPosition(posInBytes);
			TFileReadStream::SetPosition(posInBytes);
		}
		
		//GetPosition
		inline size_t GetPosition()
		{
			return TFileReadStream::GetPosition();
		}
				
		//WriteBytes
		inline void WriteBytes(const char *bytes, int count)
		{
			TFileWriteStream::WriteBytes(bytes, count);
			TFileReadStream::SetPosition(TFileWriteStream::GetPosition());
		}
		
		//ReadBytes
		inline void ReadBytes(char *bytes, int count)
		{
			TFileReadStream::ReadBytes(bytes, count);
			TFileWriteStream::SetPosition(TFileReadStream::GetPosition());
		}
		
		//WriteLine
		inline void WriteLine(const String &str)
		{
			TFileWriteStream::WriteLine(str);
			TFileReadStream::SetPosition(TFileWriteStream::GetPosition());
		}
		
		//ReadLine
		inline void ReadLine(String &var)
		{
			TFileReadStream::ReadLine(var);
			TFileWriteStream::SetPosition(TFileReadStream::GetPosition());
		}
		
		//ReadLine
		inline String ReadLine()
		{
			String temp;
			this->ReadLine(temp);
			return temp;
		}
};
typedef SharedPtr<TFileStream> FileStream;
#define CreateFileStream new TFileStream
*/

//Directory
class TDirectory: public TPrintable
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TDirectory(const String &url) : dirHandle(opendir(url)), streamURL(url)
		{
			//Debug info
			EngineLogNew("Directory");
		}
		
		//Destructor
		~TDirectory()
		{
			//Debug info
			EngineLogDelete("Directory");
			
			if(dirHandle)
				closedir(dirHandle);
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
		
		//GetNextFile
		String GetNextFile();
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Open
		inline void Open(const String &url)
		{
			opendir(url);
			streamURL = url;
		}
		
		//Close
		inline void Close()
		{
			closedir(dirHandle);
			dirHandle = Null;	//TODO: Do we need this?
		}
		
		//GetNextVisibleFile
		inline String GetNextVisibleFile()
		{
			String tmp = GetNextFile();
			return tmp.GetFirstChar() != '.' ? tmp : GetNextVisibleFile();
		}
		
		//GetNextFileDirty
		inline String GetNextFileDirty()
		{
			if(!dirHandle)
				return NullString;
			
			struct dirent *ent = readdir(dirHandle);
			return ent ? ent->d_name : NullString;
		}
		
		//Rewind
		inline void Rewind()
		{
			rewinddir(dirHandle);
		}
		
		//ToString
		inline String ToString() const
		{
			return streamURL;
		}
		
	protected:
		DIR *dirHandle;
		String streamURL;
};
typedef SharedPtr<TDirectory> Directory;
typedef Directory Dir;
#define OpenDirectory new TDirectory
#define OpenDir OpenDirectory

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Slash
#ifdef WIN32
	#define WRONG_SLASH '/'
	#define RIGHT_SLASH "\\"
#else
	#define WRONG_SLASH '\\'
	#define RIGHT_SLASH "/"
#endif

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//CopyFile
bool CopyFile(const String &from, const String &to);

//FileSize
off_t FileSize(const String &file);

//FileSize2
streampos FileSize2(const String &file);

//FileTime
time_t FileTime(const String &file);

//PrintFile
void PrintFile(const String &url);

//LoadDir
Array<String> LoadDir(const String &url, bool onlyVisibleFiles = false, bool skipDots = true);

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//ChangeDir
inline bool ChangeDir(const String &url)
{
	return !chdir(url);
}

//DeleteFile
inline bool DeleteFile(const String &filename)
{
	return !remove(filename);
}

//RenameFile
inline bool RenameFile(const String &oldFile, const String &newFile)
{
	return !rename(oldFile, newFile); 
}

//FileExists
inline bool FileExists(String fileName)
{
	struct stat fileInfo;
	if(stat(fileName, &fileInfo))
		return false;
	return true;
}

//FixPath
inline String &FixPath(String &url)
{
	size_t found = 0;
	while((found = url.find(WRONG_SLASH, found)) != String::npos)
	{
		url.replace(found, 1, RIGHT_SLASH);
		found += 1;
	}
	return url;
}

#endif /*BLITZPROG_FILESYSTEM_HPP_*/

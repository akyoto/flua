////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Stream
// Author:				Eduard Urbach
// Description:			Abstract stream class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_STREAM_HPP_
#define BLITZPROG_STREAM_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/String/String.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Stream
class TStream
{
	public:
		
		//Typedefs
		typedef SharedPtr<TStream> SPStream;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TStream(const String &url) : streamURL(url)
		{
			
		}
				
		//Constructor
		virtual ~TStream()
		{
			
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
		virtual void Open(const String &url) = 0;
		
		//Close
		virtual void Close() = 0;
		
		//Eof
		virtual bool Eof() = 0;
		
		//Flush
		virtual void Flush() = 0;
		
		//SetPosition
		virtual void SetPosition(streampos positionInBytes) = 0;
		
		//GetPosition
		virtual streampos GetPosition() = 0;
		
		//WriteBytes
		virtual void WriteBytes(const char *bytes, int count) = 0;
		
		//WriteBytes
		virtual void WriteBytes(byte *bytes, int count) = 0;
		
		//ReadBytes
		virtual streamsize ReadBytes(char *bytes, int count) = 0;
		
		//WriteLine
		virtual void WriteLine(const String &str) = 0;
		
		//ReadLine
		virtual void ReadLine(String &var) = 0;
		
		//ReadLine
		virtual String ReadLine() = 0;
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		/*
		//Write
		template <typename T>
		inline void Write(T &var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));
		}
		
		//Write (SharedPtr)
		template <typename T>
		inline void Write(SharedPtr<T> &sp)
		{
			this->WriteBytes(reinterpret_cast<char*>(sp.get()), sizeof(T));
		}
		
		//Write (CharString)
		inline void Write(CharString ptr)
		{
			this->WriteBytes(ptr, strlen(ptr));
		}
		
		//Write (int)
		inline void Write(int var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));
		}
		
		//Write (size_t)
		inline void Write(size_t var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));
		}
		
		//Write (float)
		inline void Write(float var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));
		}
		
		//Read
		template <typename T>
		inline void Read(T &var)
		{
			this->ReadBytes(reinterpret_cast<char*>(&var), sizeof(var));
		}
		
		//WriteArray
		template <typename T>
		inline void WriteArray(T *arrayPtr, int count)
		{
			this->WriteBytes(reinterpret_cast<char*>(arrayPtr), sizeof(T) * count);
		}
		
		//ReadArray
		template <typename T>
		inline void ReadArray(T *arrayPtr, int count)
		{
			for(int i=0; i < count; ++i)
			{
				this->Read(arrayPtr[i]);
			}
		}
		*/
		
		//WriteLong
		inline void WriteLong(long var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteDouble
		inline void WriteDouble(double var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteInt
		inline void WriteInt(int var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteFloat
		inline void WriteFloat(float var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteShort
		inline void WriteShort(short var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteByte
		inline void WriteByte(byte var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteByte
		inline void WriteByte(char var)
		{
			this->WriteBytes(reinterpret_cast<char*>(&var), sizeof(var));	//TODO: BES/LES
		}
		
		//WriteStreamContent
		template <typename streamType>
		inline void WriteStreamContent(streamType &stream, int bufferSize = 4096)
		{
			char *buffer = new char[bufferSize];
			while(!stream->Eof())
			{
				this->WriteBytes(buffer, stream->ReadBytes(buffer, bufferSize));
			}
			delete [] buffer;
		}
		
		//GetURL
		inline String GetURL() const
		{
			return streamURL;
		}
		
	protected:
		String streamURL;
};
typedef SharedPtr<TStream> Stream;

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



#endif /*BLITZPROG_STREAM_HPP_*/

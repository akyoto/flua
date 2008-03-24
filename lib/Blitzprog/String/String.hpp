////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.String
// Author:				Eduard Urbach
// Description:			String class
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_STRING_HPP_
#define BLITZPROG_STRING_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>

//Standard C++ Library Header Files
#include <string>
#include <sstream>
#include <iostream>

//Namespaces
using namespace std;

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Unicode
typedef std::wstring CPPStringW;
#ifndef GCC
	typedef std::wstringstream CPPStringStreamW;
	typedef std::wostringstream CPPOStringStreamW;
	typedef std::wistringstream CPPIStringStreamW;
	typedef std::wofstream CPPOFStreamW;
	typedef std::wifstream CPPIFStreamW;
#endif
typedef const wchar_t *CharStringW;

//ASCII
typedef std::string CPPString;
typedef std::stringstream CPPStringStream;
typedef std::ostringstream CPPOStringStream;
typedef std::istringstream CPPIStringStream;
typedef std::ofstream CPPOFStream;
typedef std::ifstream CPPIFStream;
typedef const char *CharString;

//CharStringWToCPPString
inline std::string CharStringWToCPPString(CharStringW ptr)
{
	CPPStringW tmp(ptr);
	return CPPString(tmp.begin(), tmp.end());
}

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//String
class TString: public CPPString
{
	public:
		
		//Typedefs
		typedef CPPString::iterator iterator;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////

		//Constructor (empty)
		TString()
		{
			
		}
		
		//Constructor (CharString)
		TString(CharString ptr) : CPPString(ptr)
		{
			
		}
		
		//Constructor (const char)
		TString(const char singleChar) : CPPString(&singleChar, 1)
		{
			
		}
		
		//Constructor (const unsigned char)
		TString(unsigned char singleChar) : CPPString("-")
		{
			operator[](0) = static_cast<char>(singleChar);
		}
		
		//Constructor (char *)
		TString(char *ptr) : CPPString(ptr)
		{
			
		}
		
		//Constructor (CharStringW)
		TString(CharStringW ptr) : CPPString(CharStringWToCPPString(ptr))
		{
			
		}
		
		//Constructor (CPPString)
		TString(const CPPString &str) : CPPString(str)
		{
			
		}
		
		//Constructor (CPPStringW)
		TString(CPPStringW &str)
		{
			this->assign(str.begin(), str.end());
		}
		
		//Constructor (String)
		TString(const TString &str) : CPPString(str)
		{
			
		}
		
		//Constructor (System::String^)
#ifdef MS_DOT_NET
		TString(System::String^ str)	//TODO: Implement this
		{
			
		}
#endif
		
		//Constructor (numerics)
		template <typename T>
		TString(T num)
		{
			EngineLog5("Using std::stringstream to convert a value to a string.");
			CPPOStringStream strStream;
			strStream << num;
			CPPString::operator=(strStream.str());
		}
		
		//Destructor
		~TString()
		{
			
		}

		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		// = //
		
		//Operator = (CPPString &)
		inline TString &operator = (const CPPString &str)
		{
			CPPString::operator=(str);
			return *this;
		}
		
		//Operator = (CPPStringW &)
		inline TString &operator = (const CPPStringW &str)
		{
			this->assign(str.begin(), str.end());
			return *this;
		}
		
		//Operator = (CharString)
		inline TString &operator = (CharString ptr)
		{
			CPPString::operator=(ptr);
			return *this;
		}
		
		//Operator = (CharStringW)
		inline TString &operator = (CharStringW ptr)
		{
			CPPStringW tmp(ptr);
			this->assign(tmp.begin(), tmp.end());
			return *this;
		}
		
		//Operator = (TString &)
		inline TString &operator = (const TString &str)
		{
			CPPString::operator=(str);
			return *this;
		}
		
		//Operator = (const unsigned char *)
		inline TString &operator = (const unsigned char *ptr)
		{
			return operator=(reinterpret_cast<const char *>(ptr));
		}
		
		//Operator = (numerics)
		template <typename T>
		inline TString &operator = (T num)
		{
			EngineLog5("Using std::stringstream to convert a value to a string.");
			CPPOStringStream strStream;
			strStream << num;
			CPPString::operator=(strStream.str());
			return *this;
		}
		
		// + //
		
		//Operator + (numerics)
		template <typename T>
		inline TString operator + (T num) const
		{
			return TString(*this) += TString(num);	//TODO: This could be optimized
		}
		
		//Operator + (CharString)
		inline TString operator + (CharString ptr) const
		{
			return TString(*this) += ptr;	//Must perform a copy
		}
		
		//Operator + (TString &)
		inline TString operator + (TString &str) const
		{
			return CPPString(*this) += str;
		}
		
		// += //
		
		//Operator += (CharString)
		inline TString &operator += (CharString ptr)
		{
			CPPString::operator+=(ptr);
			return *this;
		}

		//Operator += (TString)
		inline TString &operator += (const TString &str)
		{
			CPPString::operator+=(str);
			return *this;
		}

		//Operator += (int)
		//TODO: Convert to template
		inline TString &operator += (int num)
		{
			CPPString::operator+=(TString(num));
			return *this;
		}
		
		//Operator += (char)
		inline TString &operator += (char singleChar)
		{
			CPPString::push_back(singleChar);
			return *this;
		}
		
		// == //
		
		//Operator == (CharString)
		inline bool operator == (CharString ptr) const
		{
			//TODO: Can this be optimized?
			return std::operator==(*this, ptr);
		}
		
		//Operator == (TString &)
		inline bool operator == (const TString &str) const
		{
			return std::operator==(*this, str);
		}
		
		// -= //
		
		//Operator -= (CharString)
		inline void operator -= (CharString ptr)
		{
			EraseAll(ptr);
		}
		
		// < //
		
		//Operator < (TString &)
		inline bool operator < (const TString &str) const
		{
			return ::operator<(*this, str);
		}
		
		// . -> //
		
		//Operator ->
		inline TString *operator -> ()
		{
			return this;
		}
		
		//Operator []
		inline char &operator[](int index)// const
		{
			return this->at(index);
		}

		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: CharString
		inline operator CharString() const
		{
			return c_str();
		}
		
		//Cast: char*
		inline operator char*() const
		{
			return const_cast<char*>(c_str());
		}
		
		//Cast: CPPStringW
		inline operator CPPStringW() const
		{
			return CPPStringW(this->begin(), this->end());
		}
		
		//Cast: bool
		inline operator bool() const
		{
			return !IsEmpty();
		}
		
		/*
		//Cast: int
		inline operator int()
        {
			return ToInt();
		}

		//Cast: double
		inline operator float()
        {
			return ToFloat();
		}*/
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////

		//Replace
		void Replace(const TString &searchFor, const TString &replWith);
		
		//ReplaceStandalone
		void ReplaceStandalone(const TString &searchFor, const TString &replWith);
		
		//EraseAll
		void EraseAll(const TString &searchFor);
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////

		//GetLength
		inline CPPString::size_type GetLength() const
		{
			return this->length();
		}
		
		//GetFirstChar
		inline char &GetFirstChar()// const
		{
			return operator[](0);
		}
		
		//GetLastChar
		inline char &GetLastChar()// const
		{
			return operator[](this->length() - 1);	//TODO: *(end-1)
		}
		
		//GetMaxSize
		inline size_t GetMaxSize() const
		{
			return this->max_size();
		}
		
		//IsEmpty
		inline bool IsEmpty() const
		{
			return this->empty();
		}
		
		//IsSurroundedBy
		inline bool IsSurroundedBy(char chr)// const
		{
			return GetFirstChar() == chr && GetLastChar() == chr;
		}
		
		//IsSurroundedBy
		inline bool IsSurroundedBy(const TString &str)// const
		{
			return this->StartsWith(str) && this->EndsWith(str);
		}
		
		//LSet
		template <typename T1>
		inline TString &LSet(T1 length)
		{
			this->resize(length, ' ');
			return *this;
		}
		
		//LSet
		template <typename T1, typename T2>
		inline TString &LSet(T1 length, T2 chr = ' ')
		{
			this->resize(length, chr);
			return *this;
		}
		
		//RSet
		template <typename T1>
		inline TString &RSet(T1 length)
		{
			//TODO: Check this
			CPPString tmp;
			size_t rlen = length - this->length();
			if(rlen > 0)
			{
				tmp.resize(rlen, ' ');
				this->insert(0, tmp);
			}
			else if(rlen < 0)
			{
				this->erase(0, length);
			}
			return *this;
		}
		
		//RSet
		template <typename T1, typename T2>
		inline TString &RSet(T1 length, T2 chr = ' ')
		{
			//TODO: Check this
			CPPString tmp;
			size_t rlen = length - this->length();
			if(rlen > 0)
			{
				tmp.resize(rlen, chr);
				this->insert(0, tmp);
			}
			else if(rlen < 0)
			{
				this->erase(0, length);
			}
			return *this;
		}
		
		//Mid
		inline TString Mid(size_t start, size_t len = CPPString::npos) const
		{
			return this->substr(start, len);
		}
		
		//Left
		inline TString Left(size_t len) const
		{
			return this->substr(0, len);
		}
		
		//Right
		inline TString Right(size_t len) const
		{
			if(len > this->length())
				return TString(*this).RSet(len);
			return this->substr(this->length() - len, len);
		}
		
		//Trim
		inline TString &Trim()
		{
			size_t found = this->find_first_not_of(" \t\n\r\v");
			if(found != CPPString::npos)
			{
				size_t foundEnd = this->find_last_not_of(" \t\n\r\v");
				if(foundEnd == CPPString::npos)
				{
					this->erase(0, found);
				}
				else
				{
					this->erase(foundEnd + 1, CPPString::npos);
					this->erase(0, found);
				}
			}
			else
			{
				this->clear();
			}
			return *this;
		}
		
		//Erase
		inline void Erase(size_t start, size_t len = CPPString::npos)
		{
			this->erase(start, len);
		}
		
		//EraseLeft
		inline void EraseLeft(size_t len)
		{
			this->erase(0, len);
		}
		
		//EraseRight
		inline void EraseRight(size_t len)
		{
			this->erase(this->length() - len, len);
		}
		
		//Until
		inline TString Until(char aChar) const
		{
			return this->substr(0, this->find(aChar, 0));
		}
		
		//Until
		inline TString Until(const TString &str) const
		{
			return this->substr(0, this->find(str, 0));
		}
		
		//UntilLast
		inline TString UntilLast(char aChar) const
		{
			return this->substr(0, this->find_last_of(aChar));
		}
		
		//From
		inline TString From(char aChar, size_t offset = 0) const
		{
			size_t found = this->find(aChar, 0);
			return found != CPPString::npos ? this->substr(found + offset) : CPPString(&aChar, 1);
		}
		
		//From
		inline TString From(const TString &str, size_t offset = 0) const
		{
			size_t found = this->find(str, 0);
			return found != CPPString::npos ? this->Mid(found + offset) : str;
		}
		
		//FromTo
		inline TString FromTo(size_t index, size_t index2) const
		{
			return this->substr(index, index2 - index + 1);
		}
		
		//Find
		inline CPPString::size_type Find(char aChar, size_t pos = 0) const
		{
			return this->find(aChar, pos);
		}
		
		//Find
		inline CPPString::size_type Find(const TString &findStr, size_t pos = 0) const
		{
			return this->find(findStr, pos);
		}
		
		//FindLast
		inline CPPString::size_type FindLast(char aChar) const
		{
			return this->find_last_of(aChar);
		}
		
		//StartsWith
		inline bool StartsWith(const TString &str) const
		{
			return str == this->Left(str.length());
		}
		
		//EndsWith
		inline bool EndsWith(const TString &str) const
		{
			return str == this->Right(str.length());
		}
		
		//Insert
		inline TString &Insert(CharString ptr, size_t index)
        {
			this->insert(index, ptr);
			return *this;
		}
		
		//AddLeft
		inline TString AddLeft(CharString ptr)
        {
			return this->insert(0, ptr);
		}
		
		//AddLeft
		inline TString AddLeft(CPPString stdStr)
        {
			return this->insert(0, stdStr);
		}
		
		//AddRight
		inline TString AddRight(CharString ptr)
        {
			return CPPString::operator+=(ptr);
		}
		
		//AddRight
		inline TString AddRight(CPPString stdStr)
        {
			return CPPString::operator+=(stdStr);
		}
		
		//ToString
		inline TString ToString() const
		{
			return *this;
		}
		
		//ToCharString
		inline CharString ToCharString() const
		{
			return this->c_str();
		}
		
		//ToCharStringW
		inline CharStringW ToCharStringW() const
		{
			CPPStringW tmp(this->begin(), this->end());
			return tmp.c_str();
		}

		//ToCPPString
		inline CPPString &ToCPPString()
		{
			return *this;
		}
		
		//ToUpperCase
		inline TString ToUpperCase() const
		{
			TString tmp(*this);
			for(iterator it = tmp.begin(); it != tmp.end(); ++it)
			{
				*it = toupper(*it);
			}
			return tmp;
		}
		
		//ToLowerCase
		inline TString ToLowerCase() const
		{
			TString tmp(*this);
			for(iterator it = tmp.begin(); it != tmp.end(); ++it)
			{
				*it = tolower(*it);
			}
			return tmp;
		}
		
		//ToInt
		inline int ToInt() const
		{
			//TODO: Optimize this
			int a;
			static CPPStringStream stream(CPPStringStream::in | CPPStringStream::out);
			stream << *this;
			stream >> a;
			return a;
		}
		
		//ToFloat
		inline float ToFloat() const
		{
			//TODO: Optimize this
			float a;
			static CPPStringStream stream(CPPStringStream::in | CPPStringStream::out);
			stream << *this;
			stream >> a;
			return a;
		}
};
typedef TString String;
typedef TString Str;

//Printable
class TPrintable
{
	public:
		//Destructor
		virtual ~TPrintable()
		{
			
		}
		
		//ToString
		virtual String ToString() const = 0;
		
		//Cast: String
		virtual operator String() const
		{
			return ToString();
		}
		
		//Cast: CharString
		virtual operator CharString() const
		{
			return ToString().ToCharString();
		}
};
typedef TPrintable *Printable;

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////

//NullString
static String NullString = "";

////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//DecodeXMLEntities
inline String DecodeXMLEntities(String text)
{
	text.Replace("&amp;", "&");			//Must be first
	text.Replace("&quot;", "\"");
	text.Replace("&apos;", "'");
	text.Replace("&lt;", "<");
	text.Replace("&gt;", ">");
	return text;
}

//EncodeXMLEntities
inline String EncodeXMLEntities(String text)
{
	text.Replace("&", "&amp;");			//Must be first
	text.Replace("\"", "&quot;");
	text.Replace("'", "&apos;");
	text.Replace("<", "&lt;");
	text.Replace(">", "&gt;");
	return text;
}

//RSet
template <typename indexType>
inline String RSet(String str, indexType x, char chr = ' ')
{
	return str.RSet(x, chr);
}

//LSet
template <typename indexType>
inline String LSet(String str, indexType x, char chr = ' ')
{
	return str.LSet(x, chr);
}

//Replace
inline String Replace(String str, const String &searchFor, const String &replWith)
{
	str.Replace(searchFor, replWith);
	return str;
}

//StripDir
inline String StripDir(const String &url)
{
	return url.Mid(url.FindLast('/') + 1);
}

//StripExt
inline String StripExt(const String &url)
{
	return url.UntilLast('.');
}

//ExtractExt
inline String ExtractExt(const String &url)
{
	return url.Mid(url.FindLast('.') + 1);
}

//ExtractDir
inline String ExtractDir(const String &url, bool keepLastSlash = true)
{
	size_t found = url.FindLast('/');
	if(found != CPPString::npos)
		return url.Mid(0, found + keepLastSlash);
	if(keepLastSlash)
		return "./";
	return '.';
}

//ExtractName
inline String ExtractName(const String &url)
{
	size_t found = url.FindLast('/') + 1;
	return url.Mid(found, url.FindLast('.') - found);
}

//Implode
inline String Implode(char **array, int count, const String &separator = "")
{
	String temp = count > 0 ? array[0] : "";
	for(int i=1; i < count; ++i)
	{
		temp += separator;
		temp += array[i];
	}
	return temp;
}
/*
//Asc
inline unsigned int Asc(const String &firstChar)	//Not char because Print(Asc("A")); would not do what the user expects
{
	return static_cast<unsigned char>(firstChar[0]);
}*/

//Chr
inline String Chr(unsigned char asc)
{
	return "";	//TODO: Implement this
}

//nl2br
inline String nl2br(String str)
{
	return Replace(str, "\n", "<br />");
}

//Operator + (const char *, TString)
inline TString operator+(const char * ptr, const TString &str)
{
	return TString(ptr) += str;
}

//Operator + (CPPString, TString)
inline TString operator+(CPPString &stdStr, String &str)
{
	return str.AddLeft(stdStr);
}

//Operator == (CPPString, TString)
inline TString operator==(CPPString &stdStr, String &str)
{
	return stdStr == str.ToCPPString();
}

//TODO: istream >> TString

//Operator << (ostream, String)
inline std::ostream &operator<<(std::ostream &stream, const TString &data)
{
	return stream << data.ToCharString();
}

//Operator << (ostream, Printable)
inline std::ostream &operator<<(std::ostream &stream, const TPrintable &data)
{
	return stream << data.ToString();
}

#endif /*BLITZPROG_STRING_HPP_*/

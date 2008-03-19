#ifndef PRGMLANG_HPP_
#define PRGMLANG_HPP_

//Includes
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/FileSystem/XML/XML.hpp>

//Others
#include "Operator.hpp"

//CompileError
#define CompileError(msg) cerr << msg << endl//cerr << "[" << lineCounter << "] " << msg << endl;
#define CompileLog(msg) cout << msg << endl//cout << "[" << lineCounter << "] " << msg << endl;

//TPrgmLang
class TPrgmLang
{
	public:
		
		//Public static vars
		static TArray<TPrgmLang*> langs;
		static TArray<XMLNode> functions;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TPrgmLang()
		{
			langs.Add(this);
		}
		
		//Destructor
		virtual ~TPrgmLang()
		{
			//langs.Remove(this);
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
		
		//Init
		virtual void Init(bool debug = true) = 0;
		
		//ConvertToXML
		virtual XMLNode ConvertToXML(const String &file) = 0;
		
		//GetName
		virtual String GetName() const = 0;
		
		//GetHeader
		virtual String GetHeader(XMLNode header) = 0;
		
		//GetExpr
		virtual String GetExpr(XMLNode node) = 0;
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//IsPrgmLangWithName
		inline bool IsPrgmLangWithName(const String &name) const
		{
			for(TArray<String>::const_iterator it = names.begin(); it != names.end(); ++it)
			{
				if(*it == name)
					return true;
			}
			return false;
		}
		
		//IsPrgmLangWithExtension
		inline bool IsPrgmLangWithExtension(const String &ext) const
		{
			for(TArray<String>::const_iterator it = exts.begin(); it != exts.end(); ++it)
			{
				if(*it == ext)
					return true;
			}
			return false;
		}
		
		//GetOperator
		inline Operator GetOperator(const String &sign) const
		{
			for(TArray<Array<Operator> >::const_iterator itl = opLevels.begin(); itl != opLevels.end(); ++itl)
			{
				for(TArray<Operator>::const_iterator it = (*itl)->begin(); it != (*itl)->end(); ++it)
				{
					if((*it)->GetString() == sign)
						return *it;
				}
			}
			return Null;
		}
		
		//GetExprChilds
		inline String GetExprChilds(XMLNode node)
		{
			String expr;
			for(TArray<XMLNode>::const_iterator it = node->begin(); it != node->end(); ++it)
			{
				expr += GetExpr(*it);
			}
			return expr;
		}
		
	protected:
		TArray<String> names;
		TArray<String> exts;
		TArray<Array<Operator> > opLevels;
};

//Static vars
#ifdef BLITZPROG_MDA
	TArray<TPrgmLang*> TPrgmLang::langs;
	TArray<XMLNode> TPrgmLang::functions;
#endif

//GetPrgmLangByName
inline TPrgmLang *GetPrgmLangByName(const String &name)
{
	for(TArray<TPrgmLang*>::iterator it = TPrgmLang::langs.begin(); it != TPrgmLang::langs.end(); ++it)
	{
		if((*it)->IsPrgmLangWithName(name))
			return *it;
	}
	return Null;
}

//GetPrgmLangByExtension
inline TPrgmLang *GetPrgmLangByExtension(const String &ext)
{
	for(TArray<TPrgmLang*>::iterator it = TPrgmLang::langs.begin(); it != TPrgmLang::langs.end(); ++it)
	{
		if((*it)->IsPrgmLangWithExtension(ext))
			return *it;
	}
	return Null;
}

//GetVersion
inline String GetVersion(XMLNode version)
{
	return Str(version[0][0]) + "." + version[1][0] + "." + version[2][0] + "." + version[3][0];
}

//IsWhitespace
inline bool IsWhitespace(char chr)
{
	return isspace(chr);
}

//ConvertToLang
inline void ConvertToLang(const String &fileName, const String &toFile)
{
	//Info
	Print("Blitzprog -> Code");
	
	//Vars
	String ext = ExtractExt(toFile);
	
	//TODO: It should be possible to generate the file name from the name of the programing language
	String newFilePath = ExtractDir(fileName) + toFile;
	
	//Load XML file
	XMLFile bp = LoadXMLFile(fileName);
	XMLNode root = bp->GetRootNode();
	
	//Could not load file
	if(!root)
		return;
	
	//Header & Code
	XMLNode header = root->Find("header");
	XMLNode code = root->Find("code");
	
	//Find language
	TPrgmLang *lang = GetPrgmLangByExtension(ext);
	if(!lang)
	{
		CompileError("Can't find module for file extension " << ext);
		return;
	}
	
	//Info
	Print("Source: " << fileName);
	Print("Target: " << toFile << " (" << lang->GetName() << ")");
	Print("Path: " << newFilePath);
	
	//Check
	//bp->Save(fileName + ".xml");
	
	//Create new stream
	FileWriteStream stream = CreateFileWriteStream(newFilePath);
	stream->WriteLine(lang->GetHeader(header));
	
	//Code
	stream->WriteLine(lang->GetExprChilds(code));
}

//ConvertToXML
inline TPrgmLang *ConvertToXML(const String &fileName, const String &toFile = "", TPrgmLang *lang = Null)
{
	//Info
	Print("Code -> Blitzprog");
	
	//Vars
	String ext = ExtractExt(fileName);
	String newFileName = toFile.IsEmpty() ? (ExtractName(fileName) + ".bp") : toFile;
	String newFilePath = ExtractDir(fileName) + newFileName;
	
	//Programming language
	if(!lang)
	{
		lang = GetPrgmLangByExtension(ext);
		if(!lang)
		{
			CompileError("Can't find module for file extension " << ext);
			return lang;
		}
	}
	
	//Info
	Print("Source: " << StripDir(fileName));
	Print("Target: " << newFileName);
	Print("Module: " << lang->GetName());
	
	//Init module
	CompileLog("Initializing module...");
	lang->Init();
	CompileLog("Initialized.");
	
	//Load
	CompileLog("Converting to XML...");
	XMLNode root = lang->ConvertToXML(fileName);
	CompileLog("Converted.");
	
	//Save
	CompileLog("Saving file...");
	XMLFile fileOut = CreateXMLFile(newFilePath);
	fileOut->SetRootNode(root);
	fileOut->Save(newFilePath);
	CompileLog("Saved.");
	
	return lang;
}

#endif /*PRGMLANG_HPP_*/

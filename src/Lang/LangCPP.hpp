#ifndef LANGCPP_HPP_
#define LANGCPP_HPP_

//Includes
#include "../Interface/PrgmLang.hpp"

//Const vars
const String el = "\n";
const String separator = "//---------------------------------------------------------------------------" + el;
const String oneLineComment = "//" + el;

//TPrgmLangCPP
class TPrgmLangCPP: public TPrgmLang
{
	public:
		
		//TabLevel
		static String tabLevel;
		static int isInline;
		static bool inClassTopLevel;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TPrgmLangCPP()
		{
			names.Add("C++");
			names.Add("c++");
			names.Add("cxx");
			names.Add("cpp");
			names.Add("hpp");
			names.Add("CPP");
			names.Add("cplusplus");
			
			exts.Add("cpp");
			exts.Add("cxx");
			exts.Add("hpp");
			exts.Add("cc");
			exts.Add("h");
		}
		
		//Destructor
		~TPrgmLangCPP()
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
		
		//Init
		inline void Init(bool debug = true)
		{
			//TODO: Debug
		}
		
		//ConvertToXML
		inline XMLNode ConvertToXML(const String &file)
		{
			return Null;
		}
		
		//GetName
		inline String GetName() const
		{
			return "C++";
		}
		
		//GetHeader
		inline String GetHeader(XMLNode header)
		{
			String tmp;
			String descStr;
			XMLNode title = header->Find("title");
			XMLNode desc = header->Find("description");
			XMLNode version = header->Find("version");
			XMLNode license = header->Find("license");
			XMLNode strings = header->Find("strings");
			
			//Title and description
			if(title && desc)
			{
				tmp += separator;
				for(TArray<XMLNode>::const_iterator it = title->begin(); it != title->end(); ++it)
				{
					//Title
					tmp += "// Title (";
					tmp += (*it)->GetName();
					tmp += "):             ";
					tmp += (*it)[0]->GetName();
					tmp += el;
					
					//Desc
					tmp += separator;
					tmp += "// Description (";
					tmp += (*it)->GetName();
					tmp += "):       ";
					
					descStr = desc->Find(*it)[0];
					tmp += LSet(descStr, 50);
					tmp += el;
					descStr.Erase(0, 50);
					while(!descStr.empty())
					{
						tmp += "//                         ";
						tmp += LSet(descStr, 50);
						tmp += el;
						descStr.Erase(0, 50);
					}
					tmp += separator;
				}
			}
			
			//Version
			if(version)
			{
				tmp += "// Version:                ";
				tmp += GetVersion(version);
				tmp += el;
			}
			
			//License
			if(license)
			{
				tmp += "// License:                ";
				tmp += license[0];
				tmp += el;
			}
			
			if(title || desc || version || license)
				tmp += separator;
			
			//Counter (size_t?)
			int count = 1;
			
			//Include string declaration/definition
			tmp += "#include <Blitzprog/String/String.hpp>" + el + el;
			
			tmp += separator;
			tmp += "// Strings";
			tmp += el;
			tmp += separator;
			
			//String pool
			for(TArray<XMLNode>::const_iterator it = strings->begin(); it != strings->end(); ++it)
			{
				tmp += "const String Str__";
				tmp += count;
				tmp += " = \"";
				tmp += (*it)[0]->GetAttribute("string");
				tmp += "\";";
				tmp += el;
				
				++count;
			}
			
			return tmp;
		}
		
		//ClassToString
		inline String ClassToString(XMLNode node)
		{
			String expr = "//" + node->GetAttribute("name") + el + "class " + node->GetAttribute("name");
			XMLNode ext = node->Find("extends");
			
			if(ext)
			{
				expr += ": public ";
				expr += ext[0];
				
				//Extends
				for(TArray<XMLNode>::const_iterator it = node->begin() + 1; it != node->end(); ++it)
				{
					if((*it)->GetName() != "extends")
						break;
					expr += ", public ";
					expr += (*it)[0];
				}
			}
			
			//Public, protected, private
			XMLNode nPublic = node->Find("public");
			XMLNode nProtected = node->Find("protected");
			XMLNode nPrivate = node->Find("private");
			
			expr += el;
			expr += '{';
			expr += el;
			
			if(nPublic)
			{
				tabLevel += '\t';
				expr += tabLevel + "public:" + el;
				tabLevel += '\t';
				expr += GetExprChilds(nPublic);
			}
			
			if(nProtected)
			{
				if(nPublic)
					tabLevel.EraseRight(1);
				else
					tabLevel += '\t';
				
				expr += tabLevel + "protected:" + el;
				tabLevel += '\t';
				expr += GetExprChilds(nProtected);
			}
			
			if(nPrivate)
			{
				if(nPublic || nProtected)
					tabLevel.EraseRight(1);
				else
					tabLevel += '\t';
				
				expr += tabLevel + "private:" + el;
				tabLevel += '\t';
				expr += GetExprChilds(nPrivate);
			}
			
			expr += "};";
			expr += el;
			tabLevel.EraseRight(2);
			expr += tabLevel + el;
			
			return expr;
		}
		
		//ParseTextNode
		inline String ParseTextNode(String text)
		{
			text.ReplaceStandalone("Self", "(*this)");
			return text;
		}
		
		//GetType
		inline String GetType(XMLNode type)
		{
			if(!type)
				return "void";
			String ret;
			if(type->GetAttribute("const") == "true")
				ret += "const ";
			ret += type[0];
			if(type->GetAttribute("callby") == "reference")
				ret += '&';
			return ret;
		}
		
		//GetCallParameters
		inline String GetCallParameters(XMLNode node)
		{
			String expr;
			for(TArray<XMLNode>::const_iterator it = node->begin(); it != node->end(); )
			{
				if((*it)->GetName() == "parameter")
				{
					expr += GetExprChilds(*it);
					if(++it != node->end())
						expr += ", ";
				}
				else
				{
					++it;
				}
			}
			return expr;
		}
		
		//GetFuncParameters
		inline String GetFuncParameters(XMLNode node)
		{
			String expr;
			for(TArray<XMLNode>::const_iterator it = node->begin(); it != node->end(); )
			{
				expr += GetExpr(*it);
				if(++it != node->end())
					expr += ", ";
			}
			return expr;
		}
		
		//GetExprByElement
		inline String GetExprByElement(XMLNode element)
		{
			//Get name
			String e = element->GetName();
			
			//Switch
			if(e == "class")
			{
				inClassTopLevel = true;
				return ClassToString(element);
			}
			else if(e == "var")
			{
				int wasInline = isInline;
				String tmp;
				
				if(!wasInline)
					tmp += tabLevel;
				tmp += GetType(element->Find("type")) + " " + element->GetAttribute("name");
				
				++isInline;
				if(!inClassTopLevel && element->Find("value") && !element->Find("value")->IsEmpty())
					tmp += " = " + GetExprChilds(element->Find("value"));
				else
					;//TODO: Add inits to constructor
				
				if(!wasInline)
					tmp += ";" + el;
				--isInline;
				return tmp;
			}
			else if(e == "define")
			{
				return tabLevel + "typedef " + GetType(element->Find("alias")) + " " + GetType(element->Find("term")) + ";" + el;
			}
			else if(e == "function" || e == "method")
			{
				inClassTopLevel = false;
				String name = element->GetAttribute("name");
				String tmp = tabLevel + "//" + name + el + tabLevel + "inline ";
				tmp += GetType(element->Find("type")) + " ";
				tmp += name + "(";
				if(element->Find("parameters"))
				{
					++isInline;
					tmp += GetFuncParameters(element->Find("parameters"));
					--isInline;
				}
				tmp += ")" + el + tabLevel + "{" + el;
				tabLevel += '\t';
				tmp += GetExprChilds(element->Find("code"));
				tabLevel.EraseRight(1);
				tmp += tabLevel + "}" + el + tabLevel + el;
				return tmp;
			}
			else if(e == "return")
			{
				++isInline;
				String tmp = tabLevel + "return";
				if(element->IsEmpty())
					tmp += ";" + el;
				else
					tmp += " " + GetExprChilds(element) + ";" + el;
				--isInline;
				return tmp;
			}
			else if(e == "call")
			{
				String tmp;
				
				if(!isInline)
					tmp += tabLevel;
				
				if(element->Find("function"))
				{
					tmp += GetExprChilds(element->Find("function")) + "(";
					tmp += GetCallParameters(element);						//TODO: GetCallParameters
					tmp += ')';
				}
				else
				{
					tmp += GetExprChilds(element[0]) + "." + GetExprChilds(element[1]);
				}
				
				if(!isInline)
					tmp += ";" + el;
				
				return tmp;
			}
			else if(e == "assign")
			{
				String tmp;
				
				if(!isInline)
					tmp += tabLevel;
				
				++isInline;
				tmp += GetExprChilds(element->Find("var")) + " = " + GetExprChilds(element->Find("value"));
				--isInline;
				
				if(!isInline)
					tmp += ";" + el;
				
				return tmp;
			}
			else if(e == "divide" || e == "multiply" || e == "add" || e == "subtract")
			{
				String tmp = tabLevel;
				tmp += GetExprChilds(element->Find("operand"));
				
				//Operator
				if(e == "divide")
					tmp += " /= ";
				else if(e == "multiply")
					tmp += " *= ";
				else if(e == "add")
					tmp += " += ";
				else if(e == "subtract")
					tmp += " -= ";
				
				++isInline;
				tmp += GetExprChilds(element->Find("value")) + ";" + el;
				--isInline;
				
				return tmp;
			}
			else if(e == "if")
			{
				++isInline;
				String tmp = tabLevel + "if(" + GetExprChilds(element->Find("condition")) + ")" + el + tabLevel + "{" + el;
				--isInline;
				tabLevel += '\t';
				tmp += GetExprChilds(element->Find("code"));
				tabLevel.EraseRight(1);
				return tmp;
			}
			else if(e == "if-block")
			{
				return GetExprChilds(element) + tabLevel + "}" + el;
			}
			else if(e == "import")
			{
				String imp = GetExprChilds(element);
				imp.Replace(".", "/");
				return tabLevel + "#include <" + imp + "/" + imp.Mid(imp.FindLast('/') + 1) + ".hpp" + ">" + el;
			}
			else if(e == "dependencies")
			{
				return tabLevel + separator + tabLevel + "// Includes" + el + tabLevel + separator + tabLevel + el + GetExprChilds(element) + tabLevel + el;
			}
			else if(e == "methods")
			{
				return tabLevel + separator + tabLevel + "// Methods" + el + tabLevel + separator + tabLevel + el + GetExprChilds(element) + tabLevel + el;
			}
			else if(e == "definitions")
			{
				return tabLevel + separator + tabLevel + "// Definitions" + el + tabLevel + separator + tabLevel + el + GetExprChilds(element) + tabLevel + el;
			}
			else if(e == "vars")
			{
				return tabLevel + separator + tabLevel + "// Variables" + el + tabLevel + separator + tabLevel + el + GetExprChilds(element) + tabLevel + el;
			}
			
			return NullString;
		}
		
		//GetExpr
		inline String GetExpr(XMLNode node)
		{
			if(node->IsTextNode())
				return ParseTextNode(node->GetName());
			else
				return GetExprByElement(node);
		}
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		
		
	protected:
		
};

//Instance
#ifdef BLITZPROG_MDA
	TPrgmLangCPP instanceCPP;
	String TPrgmLangCPP::tabLevel;
	int TPrgmLangCPP::isInline;
	bool TPrgmLangCPP::inClassTopLevel;
#endif

#endif /*LANGCPP_HPP_*/

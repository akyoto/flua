////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.XMLFile
// Author:				Eduard Urbach
// Description:			XML file
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_FILESYSTEM_XMLFILE_HPP_
#define BLITZPROG_FILESYSTEM_XMLFILE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/FileSystem/FileSystem.hpp>
#include <Blitzprog/FileSystem/XML/XMLNode.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//XMLFile
class TXMLFile;
typedef SharedPtr<TXMLFile> XMLFile;

//XMLFile
class TXMLFile
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TXMLFile(const String &nURL) : url(nURL), rootNode(Null)
		{
			EngineLogNew("XMLFile: " << url);
		}
		
		//Destructor
		~TXMLFile()
		{
			EngineLogDelete("XMLFile: " << url);
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
		
		//Load
		inline void Load()
		{
			//Vars
			String line;
			String tmpline;
			size_t index;
			String currentText;
			String attrName;
			String attrValue;
			XMLNode currentNode = Null;
			
			//Create stream
			FileReadStream stream = CreateFileReadStream(url);
			
			//Create one big string
			while(!stream->Eof())
			{
				stream->ReadLine(tmpline);
				tmpline.Trim();
				if(!tmpline.StartsWith("<") && !tmpline.StartsWith("\"") && !tmpline.StartsWith("'") && !line.EndsWith(">") && !line.EndsWith("\"") && !line.EndsWith("'"))	//TODO: && !tmpline.empty()
					line += ' ';
				line += tmpline;	//TODO: Add stringstream
			}
			
			for(size_t i = 0; i < line.length(); ++i)
			{
				switch(line[i])
				{
					//Open tag
					case '<':
						index = i + 1;
						
						//Text nodes
						if(!currentText.empty())
						{
							currentText.Trim();
							if(!currentText.empty())
							{
								if(currentNode)
									currentNode->Add(CreateXMLTextNode(currentText));
								currentText.clear();
							}
						}
						
						//Is PI?
						if(line[index] == '?')
						{
							while(line[++index] != '?');
							i = index + 1;
							continue;
						}
						
						//TODO: CDATA
						//Is Doctype?
						if(line[index] == '!')
						{
							while(line[++index] != '>');
							i = index;
							continue;
						}
						
						//Is close tag?
						if(line[index] == '/')
						{
							while(line[++index] != '>');
							if(currentNode)
							{
								EngineLog5("Found close tag: " << currentNode->GetName() << " <- " << (currentNode->GetParent() ? currentNode->GetParent()->GetName() : "Null"));
								currentNode = currentNode->GetParent();
								EngineLog5("Changed currentNode");
							}
							i = index;
							continue;
						}
						
						//Find whitespace (get tag name)
						while(isgraph(line[++i]) && line[i] != '>');
						
						//Element that includes both: open and close tag
						if(line[i - 1] == '/')
						{
							//Debug info
							EngineLog5("Found node: " << line->FromTo(index, i - 2));
							
							//Just add the node, do not change the current node
							AddNode(currentNode, CreateXMLNode(line->FromTo(index, i - 2)));
						}
						else if(line[i + 1] == '/')		//Whitespaces in the tag
						{
							//Debug info
							EngineLog5("Found node: " << line->FromTo(index, i - 1));
							
							//Just add the node, do not change the current node
							AddNode(currentNode, CreateXMLNode(line->FromTo(index, i - 1)));
							
							//Adjust 'i'
							i += 2;
						}
						else if(currentNode)	//Add node
						{
							//Debug info
							EngineLog5("Found node: " << currentNode->GetName() << " -> " << line->FromTo(index, i - 1));
							
							//Add the node and set it as the current node
							XMLNode node = CreateXMLNode(line->FromTo(index, i - 1));
							AddNode(currentNode, node);
							currentNode = node;
						}
						else	//Root node
						{
							//Debug info
							EngineLog5("Found root node: " << line->FromTo(index, i - 1));
							
							if(!rootNode)
								rootNode = CreateXMLNode(line->FromTo(index, i - 1));
							currentNode = rootNode;
						}
						
						//Attributes
						while(line[i] != '>')
						{
							//Debug info
							EngineLog5("Found attribute");
							
							//Whitespace position plus 1
							//if(!isgraph(line[i]))
							//	while(!isgraph(line[++i]));		//TODO: iswhitespace or something else
							while(!isgraph(line[i])) ++i;
							index = i;
							
							//Find =
							while(line[++i] != '=');
							attrName = DecodeXMLEntities(line.FromTo(index, i-1));
							
							//TODO: The ' character, too ('"')
							
							//Find first "
							while(line[++i] != '\"');
							index = i + 1;
							
							//Find second "
							while(line[++i] != '\"');
							attrValue = line.FromTo(index, i-1);
							
							//Add attribute
							currentNode->AddAttribute(attrName, attrValue);
							
							//More attributes
							while(!isgraph(line[++i]));		//TODO: iswhitespace or something else
							
							//Both: open/close tag
							if(line[i] == '/')
							{
								++i;
								currentNode = currentNode->GetParent();
								break;
							}
						}
						
						break;
						
					//Close tag
					case '>':
						break;
						
					default:
						currentText += line[i];
				}
			}
		}
		
		//GetRootNode
		inline XMLNode GetRootNode()
		{
			return rootNode;
		}
		
		//SetRootNode
		inline void SetRootNode(XMLNode node)
		{
			rootNode = node;
		}
		
		//Save
		inline void Save(const String &file)
		{
			FileWriteStream stream = CreateFileWriteStream(file);
			stream->WriteLine("<?xml version=\"1.0\"?>");
			stream->WriteLine("");
			if(rootNode)
			{
				stream->WriteLine("<" + rootNode->GetName() + rootNode->GetAttributeString() + ">");
				rootNode->WriteNodesToStream(stream);
				stream->WriteLine("</" + rootNode->GetName() + ">");
			}
			stream->WriteLine("");
		}
		
		//PrintNodes
		inline void PrintNodes()
		{
			if(rootNode)
			{
				Print("<" << rootNode->GetName() << rootNode->GetAttributeString() << ">");
				rootNode->PrintNodes();
				Print("</" << rootNode->GetName() << ">");
			}
		}
		
	protected:
		String url;
		XMLNode rootNode;
};
#define CreateXMLFile new TXMLFile

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

//LoadXMLFile
inline XMLFile LoadXMLFile(const String &url)
{
	XMLFile file = CreateXMLFile(url);
	file->Load();
	return file;
}

#endif /*BLITZPROG_FILESYSTEM_XMLNODE_HPP_*/

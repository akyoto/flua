////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.XMLNode
// Author:				Eduard Urbach
// Description:			XML node
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_FILESYSTEM_XMLNODE_HPP_
#define BLITZPROG_FILESYSTEM_XMLNODE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/FileSystem/FileSystem.hpp>
#include <Blitzprog/Collection/Collection.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//XMLNode
class XMLNode;
class TXMLNode;
//class TXMLNode;
//typedef TXMLNode *XMLNode;
//typedef SharedPtr<TXMLNode> XMLNode;
typedef WeakPtr<TXMLNode> XMLParentNode;

//XMLNode
class XMLNode: public SharedPtr<TXMLNode>
{
	public:
		
		typedef SharedPtr<TXMLNode> refNode;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		XMLNode() : SharedPtr<TXMLNode>()
		{
			
		}
		
		/*
		//Constructor
		XMLNode(const String &nName, bool nIsTextNode = false) : SharedPtr<TXMLNode>(new TXMLNode(nName, nIsTextNode))
		{
			
		}
		*/
		
		//Constructor
		XMLNode(TXMLNode *ptr) : SharedPtr<TXMLNode>(ptr)
		{
			
		}
		
		//Constructor
		XMLNode(WeakPtr<TXMLNode> ref) : SharedPtr<TXMLNode>(ref.lock())
		{
			
		}
		
		/*
		//Constructor
		XMLNode(XMLNode &ref) : SharedPtr<TXMLNode>(ref)
		{
			
		}*/
		
		//Destructor
		~XMLNode();

		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator []
		//XMLNode operator[](size_t index) const;
		XMLNode operator[](int index) const;
		
		//Operator []
		//const XMLNode operator[](size_t index) const;
		
		//Operator =
		inline XMLNode operator=(const XMLNode &node)
		{
			SharedPtr<TXMLNode>::operator=(node);
			return *this;
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		//Cast: String
		operator String();
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//ToString
		inline String ToString() const
		{
			return this->operator[](0);
		}
		
	protected:
		
};

//XMLNode
class TXMLNode: public TArray<XMLNode>, public TPrintable
{
	public:
		
		//Public static vars
		static String tabLevel;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TXMLNode(const String &nName, bool nIsTextNode = false) : name(nName), isTextNode(nIsTextNode)
		{
			EngineLogNew("XMLNode: " << name);
		}
		
		//Destructor
		~TXMLNode()
		{
			EngineLogDelete("XMLNode: " << name);
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
		
		//Contains
		bool Contains(const String &name) const;
		
		//Find
		XMLNode Find(const String &name) const;
		
		//DetachChildNodes
		void DetachChildNodes();
		
		//SetParent
		void SetParent(XMLParentNode nParent);
		
		//GetParent
		XMLParentNode GetParent() const;
		
		//PrintNodes
		void PrintNodes() const;
		
		//WriteNodesToStream
		void WriteNodesToStream(FileWriteStream stream) const;
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//TODO: 'Add' function, if possible
		
		//AddAttribute
		inline void AddAttribute(const String &key, const String &value)
		{
			//Debug info
			EngineLog5("Attribute: " << key << " = " << value);
			
			attributes.Add(key, value);
		}
		
		//GetAttribute
		inline String &GetAttribute(const String &key)
		{
			return attributes[key];
		}
		
		//SetAttribute
		inline void SetAttribute(const String &key, const String &value)
		{
			attributes[key] = value;
		}
		
		//GetName
		inline const String &GetName() const
		{
			return name;
		}
		
		//GetAttributeString
		inline String GetAttributeString()
		{
			String tmp;
			for(map<String, String>::const_iterator it = attributes.begin(); it != attributes.end(); ++it)
			{
				tmp += ' ';
				tmp += it->first;
				tmp += "=\"";
				tmp += EncodeXMLEntities(it->second);
				tmp += '\"';
			}
			return tmp;
		}
		
		//IsTextNode
		inline bool IsTextNode() const
		{
			return isTextNode;
		}
		
		//ToString
		inline String ToString() const
		{
			return name;
		}
		
		//ToDecodedString
		inline String ToDecodedString() const
		{
			return DecodeXMLEntities(name);
		}
		
		//ToEncodedString
		inline String ToEncodedString() const
		{
			return EncodeXMLEntities(name);
		}
		
		//Friends
		friend inline void AddNode(XMLNode parent, XMLNode childNode);
		
	protected:
		String name;
		TMap<String, String> attributes;
		XMLParentNode parent;
		bool isTextNode;
};

//Static vars
#ifndef BLITZPROG_LIB
	String TXMLNode::tabLevel;
#endif

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

//CreateXMLNode
inline XMLNode CreateXMLNode(const String &elementName, bool isTextNode = false)
{
	return new TXMLNode(elementName, isTextNode);
}

//CreateXMLTextNode
inline XMLNode CreateXMLTextNode(const String &text)
{
	return CreateXMLNode(text, true);
}

//AddNode
inline void AddNode(XMLNode parent, XMLNode childNode)
{
	if(!parent || !childNode)
		return;
	if(childNode->parent)
		childNode->parent->Remove(childNode);
	childNode->parent = parent;
	parent->Add(childNode);
}

//String +=
inline void operator+=(String &str, XMLNode node)
{
	str += static_cast<String>(node);
}

#endif /*BLITZPROG_FILESYSTEM_XMLNODE_HPP_*/

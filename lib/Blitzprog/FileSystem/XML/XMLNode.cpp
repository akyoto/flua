#include "XMLNode.hpp"

//Contains
bool TXMLNode::Contains(const String &name) const
{
	for(const_iterator it = this->begin(); it != this->end(); ++it)
	{
		if(name == (*it)->name)
			return true;
	}
	return false;
}

//Find
XMLNode TXMLNode::Find(const String &name) const
{
	for(const_iterator it = this->begin(); it != this->end(); ++it)
	{
		if(name == (*it)->name)
			return (*it);
	}
	return Null;
}

//DetachChildNodes
void TXMLNode::DetachChildNodes()
{
	for(iterator it = this->begin(); it != this->end(); ++it)
	{
		(*it)->parent = Null;	//.reset();
		(*it).reset();
	}
}

//PrintNodes
void TXMLNode::PrintNodes() const
{
	tabLevel += "\t";
	for(const_iterator it = this->begin(); it != this->end(); ++it)
	{
		if((*it)->IsTextNode())
		{
			Print(tabLevel << (*it)->ToEncodedString());
		}
		else
		{
			Print(tabLevel << "<" << (*it)->name << (*it)->GetAttributeString() + ">");
			if((*it)->GetSize() != 0)
				(*it)->PrintNodes();
			Print(tabLevel << "</" << (*it)->name << ">");
		}
	}
	tabLevel->Erase(tabLevel->GetLength() - 1);
}

//WriteNodesToStream
void TXMLNode::WriteNodesToStream(FileWriteStream stream) const
{
	tabLevel += "\t";
	for(const_iterator it = this->begin(); it != this->end(); ++it)
	{
		if((*it)->IsTextNode())
		{
			stream->WriteLine(tabLevel + (*it)->ToEncodedString());
		}
		else
		{
			if(!((*it)->IsEmpty()))
			{
				stream->WriteLine(tabLevel + "<" + (*it)->name + (*it)->GetAttributeString() + ">");
				(*it)->WriteNodesToStream(stream);
				stream->WriteLine(tabLevel + "</" + (*it)->name + ">");
			}
			else	//TODO: ...
			{
				stream->WriteLine(tabLevel + "<" + (*it)->name + (*it)->GetAttributeString() + "/>");
			}
		}
	}
	tabLevel->Erase(tabLevel->GetLength() - 1);
}

//SetParent
void TXMLNode::SetParent(XMLParentNode nParent)
{
	parent = nParent;
}

//GetParent
XMLParentNode TXMLNode::GetParent() const
{
	return parent;
}

//XMLNode

//Destructor
XMLNode::~XMLNode()	//TODO: Remove this function, it causes overhead
{
	if(*this)
	{
		//Debug info
		EngineLog5("Delete XMLNode manager: " << (*this)->GetName());
	}
}

/*
//Operator []
XMLNode XMLNode::operator[](size_t index) const
{
	return (*this)->GetElementByIndex(index);
}
*/

//Operator []
XMLNode XMLNode::operator[](int index) const
{
	return (*this)->GetElementByIndex(index);
}

/*
//Operator []
const XMLNode XMLNode::operator[](size_t index) const
{
	return (*this)->GetElementByIndex(index);
}*/

//Cast: String
XMLNode::operator String()
{
	return (*this)->GetName();
}

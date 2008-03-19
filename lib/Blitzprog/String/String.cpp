#include "String.hpp"

//Replace
void TString::Replace(const TString &searchFor, const TString &replWith)
{
	CPPString::size_type searchForLength = searchFor.GetLength();
	CPPString::size_type replWithLength = replWith.GetLength();
	CPPString::size_type lastFound = 0;
	
	while((lastFound = this->find(searchFor, lastFound)) != CPPString::npos)
	{
		this->replace(lastFound, searchForLength, replWith);
		lastFound += replWithLength;
	}
}

//ReplaceStandalone
void TString::ReplaceStandalone(const TString &searchFor, const TString &replWith)
{
	CPPString::size_type searchForLength = searchFor.GetLength();
	CPPString::size_type replWithLength = replWith.GetLength();
	CPPString::size_type lastFound = 0;
	
	while((lastFound = this->find(searchFor, lastFound)) != CPPString::npos)
	{
		if( (lastFound == 0 || isspace((*this)[lastFound - 1])) && (lastFound + searchForLength == this->GetLength() || isspace((*this)[lastFound + searchForLength])) )
			this->replace(lastFound, searchForLength, replWith);
		lastFound += replWithLength;
	}
}

//EraseAll
void TString::EraseAll(const String &searchFor)
{
	CPPString::size_type searchForLength = searchFor.GetLength();
	CPPString::size_type lastFound = 0;
	
	while((lastFound = this->find(searchFor, lastFound)) != CPPString::npos)
	{
		this->erase(lastFound, searchForLength);
	}
}

#ifndef OPERATOR_HPP_
#define OPERATOR_HPP_

//Includes
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/FileSystem/XML/XML.hpp>

//Operator
class TOperator
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TOperator(const String &opStr, const String &xmlNodeNameDesc, bool ltr = true) : str(opStr), xmlNodeName(xmlNodeNameDesc)//, leftToRight(ltr)
		{
			
		}
		
		//Destructor
		~TOperator()
		{
			
		}
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//GetString
		inline const String &GetString() const
		{
			return str;
		}
		
		/*//IsLeftToRight
		inline bool IsLeftToRight() const
		{
			return leftToRight;
		}*/
		
		//GetNodeName
		inline const String &GetNodeName() const
		{
			return xmlNodeName;
		}
		
	protected:
		String str;
		String xmlNodeName;
		//bool leftToRight;
};
typedef SharedPtr<TOperator> Operator;

#endif  /*OPERATOR_HPP_*/

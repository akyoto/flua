#include "Array.hpp"

//Implode
String Implode(Array<String> &array, const String &separator)
{
	int count = array->GetLength();
	String temp = count > 0 ? array[0] : "";
	for(int i=1; i < count; ++i)
	{
		temp += separator;
		temp += array[i];
	}
	return temp;
}

//Explode
Array<String> Explode(const String &implodedString, const String &separator)
{
	Array<String> array = CreateArray<String>();
	size_t lastFound = 0;
	size_t found = 0;
	while((found = implodedString.Find(separator, lastFound)) != CPPString::npos)
	{
		array->Add(implodedString.Mid(lastFound, found - lastFound));
		lastFound = found + separator.GetLength();
	}
	array->Add(implodedString.Mid(lastFound));
	return array;
}

////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Collection.Array
// Author:				Eduard Urbach
// Description:			Simple vector wrapper
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_COLLECTION_ARRAY_HPP_
#define BLITZPROG_COLLECTION_ARRAY_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/Collection/Interface.hpp>

//Standard C++ Library Header Files
#include <vector>
#include <algorithm>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//List
template <typename T>
class TArray: public vector<T>, public TCollection<T>//, public TPrintable
{
	public:
		
		//Typedefs
		typedef SharedPtr<TArray<T> > SPArray;
		typedef typename vector<T>::iterator iterator;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TArray()
		{
			//Debug info
			EngineLogNew("Array");
		}
		
		//Destructor
		~TArray()
		{
			//Debug info
			EngineLogDelete("Array");
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator []
		inline T &operator[](size_t index)
		{
			return vector<T>::operator[](index);
		}
		
		//Operator []
		inline const T &operator[](size_t index) const
		{
			return vector<T>::operator[](index);
		}
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//Add
		inline void Add(const T &element)
		{
			this->push_back(element);
		}
		
		//TODO: AddArray
		/*
		//Add
		inline void Add(const SPArray &c)
		{
			for(iterator it = c->begin(); it != c->end(); ++it)
			{
				this->push_back(*it);
			}
		}*/
		
		//Remove
		inline bool Remove(const T &element)
		{
			for(iterator it = this->begin(); it != this->end(); ++it)
			{
				if(*it == element)
				{
					this->erase(it);
					return true;
				}
			}
			return false;
		}
		
		//RemoveAll
		inline size_t RemoveAll(const T &value)
		{
			size_t removed = 0;
			for(iterator it = this->begin(); it != this->end(); ++it)
			{
				if(*it == value)
				{
					this->erase(it);
					++removed;
				}
			}
			return removed;
		}
		
		//RemoveAll
		inline size_t RemoveAll(const SPArray c)
		{
			size_t removed = 0;
			for(iterator it = c->begin(); it != c->end(); ++it)
			{
				Remove(*it);
			}
			return removed;
		}
		
		//RemoveElementByIndex
		inline void RemoveElementByIndex(size_t index)
		{
#ifdef DEBUG
			if(index >= this->GetSize())
			{
				EngineLogError("Array index out of bounds. Tried to access element at position " << index+1 << " but the array has only " << this->GetSize() << " elements.");
				return;
			}
#endif
			this->erase(this->begin() + index);
		}
		
		//RetainAll
		inline size_t RetainAll(const SPArray c)
		{
			size_t removed = 0;
			for(iterator it = this->begin(); it != this->end(); ++it)
			{
				if(!c->Contains(*it))
				{
					this->erase(it);
					++removed;
				}
			}
			return removed;
		}
		
		//Insert
		inline void Insert(const T &element, size_t at)
		{
			this->insert(this->begin() + at, element);
		}
		
		//InsertBefore
		inline void InsertBefore(const T &element, const T &before)
		{
			this->insert(find(this->begin(), this->end(), before), element);
		}
		
		//InsertAfter
		inline void InsertAfter(const T &element, const T &after)
		{
			this->insert(find(this->begin(), this->end(), after) + 1, element);
		}
		
		//GetElementByIndex
		inline T &GetElementByIndex(size_t index)
		{
			return vector<T>::operator[](index);
		}
		
		//GetElementByIndex
		inline const T &GetElementByIndex(size_t index) const
		{
			return vector<T>::operator[](index);
		}
		
		//CountOccurenceOf
		inline size_t CountOccurenceOf(const T &value) const
		{
			return count(this->begin(), this->end(), value);
		}
		
		//Clear
		inline void Clear()
		{
			this->clear();
		}
		
		//Sort
		inline void Sort(bool ascending = true)
		{
			if(ascending)
				sort(this->begin(), this->end());
			else
				sort(this->rbegin(), this->rend());
		}
		
		//Reverse
		inline void Reverse(size_t from = 0, size_t to = 0)
		{
			iterator theEnd;
			if(to == 0)
				theEnd = this->end();
			else
				theEnd = this->begin() + to;
			reverse(this->begin() + from, this->begin() + to);
		}
		
		//Reverse
		inline void Reverse(const T &from, const T &to)
		{
			Reverse(Find(from), Find(to));
		}
		
		//Erase
		inline void Erase(size_t index)
		{
			this->erase(this->begin() + index);
		}
		
		//Erase
		inline void Erase(size_t from, size_t to)
		{
			this->erase(this->begin() + from, this->begin() + to);
		}
		
		//GetSize
		inline size_t GetSize() const
		{
			return this->size();
		}
		
		//Find
		inline int Find(const T &element, size_t from=0) const
		{
			for(size_t i = from; i < this->size(); ++i)
			{
				if(vector<T>::operator[](i) == element)
					return i;
			}
			return -1;
		}
		
		//Contains
		inline bool Contains(const T &element) const
		{
			return find(this->begin(), this->end(), element) != this->end();
		}
		
		//ContainsAll
		inline bool ContainsAll(const SPArray c) const
		{
			for(iterator it = c->begin(); it != c->end(); ++it)
			{
				if(!Contains(*it))
					return false;
			}
			return true;
		}
		
		//IsEmpty
		inline bool IsEmpty() const
		{
			return this->empty();
		}
		
		//GetFirstElement
		inline T &GetFirstElement()	//TODO:	Should this be const?
		{
			return this->front();
		}
		
		//GetLastElement
		inline T &GetLastElement()	//TODO:	Should this be const?
		{
			return this->back();
		}
		
		//GetBegin
		inline iterator GetBegin() const
		{
			return this->begin();
		}
		
		//GetEnd
		inline iterator GetEnd() const
		{
			return this->end();
		}
		
		// // // //
		
		//GetLength
		inline size_t GetLength() const
		{
			return this->size();
		}
		
		//GetSizeInBytes
		inline size_t GetSizeInBytes() const
		{
			return this->size() * sizeof(T);
		}
		
		//ToCPPVector
		inline vector<T> &ToCPPVector()
		{
			return *this;
		}
		
		/*
		//ToString
		inline String ToString() const
		{
			int size = this->size();
			String temp = size > 0 ? String(vector<T>::operator[](0)) : "";
			for(int i=1; i < size; ++i)
			{
				temp += ", ";
				temp += String(vector<T>::operator[](i));	//TODO: Optimize this, if possible
			}
			return temp;
		}
		*/
};

//Array
template <typename T>
class Array: public SharedPtr<TArray<T> >
{
	private:
		typedef SharedPtr<TArray<T> > refArray;
		
	public:
		
		//Typedefs
		typedef typename vector<T>::iterator iterator;
		
		//Constructor
		Array() : refArray()
		{
			
		}
		
		//Constructor
		Array(TArray<T> *ptr) : refArray(ptr)
		{
			
		}
		
		//Operator []
		template <typename indexType>
		inline T &operator[](indexType index)
		{
			return (*this)->GetElementByIndex(index);
		}
		
		//Operator []
		template <typename indexType>
		inline const T &operator[](indexType index) const
		{
			return (*this)->GetElementByIndex(index);
		}
};
#define CreateArray new TArray

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//Implode
template <typename T>
inline String Implode(Array<T> &array, const String &separator)
{
	int count = array->GetLength();
	String temp = count > 0 ? static_cast<String>(array[0]) : "";
	for(int i=1; i < count; ++i)
	{
		temp += separator;
		temp += array[i];
	}
	return temp;
}

//Implode
String Implode(Array<String> &array, const String &separator);

//Explode
Array<String> Explode(const String &implodedString, const String &separator);

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//Operator == (TArray &)
template <typename T>
inline bool operator==(Array<T> &thisArray, Array<T> &nArray)
{
	return thisArray->ToCPPVector() == nArray->ToCPPVector();
}

//Operator == (std::vector &)
template <typename T>
inline bool operator==(Array<T> &thisArray, vector<T> &nArray)
{
	return thisArray->ToCPPVector() == nArray;
}

//Operator +=
template <typename T>
inline void operator+=(Array<T> &thisArray, T element)		//NOTE: Maybe references are possible, too.
{
	thisArray->push_back(element);
}

//Operator +=
inline void operator+=(Array<String> &thisArray, CharString element)
{
	thisArray->push_back(element);
}

#endif /*BLITZPROG_COLLECTION_ARRAY_HPP_*/

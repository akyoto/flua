////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Collection.List
// Author:				Eduard Urbach
// Description:			Lists for storing data
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_COLLECTION_LIST_HPP_
#define BLITZPROG_COLLECTION_LIST_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/Collection/Interface.hpp>

//Standard C++ Library Header Files
#include <list>
#include <algorithm>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//List
template <typename T>
class TList: public list<T>
{
	public:
		
		//Typedefs
		typedef SharedPtr<TList<T> > SPList;
		typedef typename list<T>::iterator IteratorType;
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TList()
		{
			//Debug info
			EngineLogNew("List");
		}
		
		//Destructor
		~TList()
		{
			//Debug info
			EngineLogDelete("List");
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
		
		//Add
		inline void Add(T element)		//NOTE: Maybe references are possible, too.
		{
			this->push_back(element);
		}
		
		//Remove
		inline void Remove(const T &value)
		{
			this->remove(value);
		}
		
		//RemoveElementByIndex
		inline void RemoveElementByIndex(size_t index)
		{
#ifdef DEBUG
			if(index >= this->GetSize())
			{
				EngineLogError("List index out of bounds. Tried to access element at position " << index+1 << " but the list has only " << this->GetSize() << " elements.");
				return;
			}
#endif
			size_t i = 0;
			for(IteratorType iter = this->begin(); iter != this->end(); ++iter)
			{
				if(++i == index)
				{
					this->erase(iter);
					return;
				}
			}
		}
		
		//Clear
		inline void Clear()
		{
			this->clear();
		}
		
		//Sort
		inline void Sort()
		{
			this->sort();
		}
		
		//GetElementByIndex
		inline const T GetElementByIndex(size_t index)
		{
			size_t i = 0;
			for(IteratorType iter = this->begin(); iter != this->end(); ++iter)
			{
				if(++i == index)
					return *iter;
			}
			return 0;
		}
		
		//GetSize
		inline size_t GetSize() const
		{
			return this->size();
		}
		
		//GetSizeInBytes
		inline size_t GetSizeInBytes() const
		{
			return this->size() * sizeof(T);
		}
		
		//ToCPPList
		inline list<T> &ToCPPList()
		{
			return *this;
		}
};
#define CreateList new TList

//List
template <typename T>
class List : public SharedPtr<TList<T> >
{
	private:
		typedef SharedPtr<TList<T> > refList;
		
	public:
		
		//Typedefs
		typedef typename list<T>::iterator IteratorType;
		
		//Constructor
		List() : refList()
		{
			
		}
		
		//Constructor
		List(TList<T> *ptr) : refList(ptr)
		{
			
		}
		
		//Operator []
		inline const T operator[](int index) const
		{
			return (*this)->GetElementByIndex(index);
		}
};

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//Operator == (TList &)
template <typename T>
inline bool operator==(List<T> &thisList, List<T> &nList)
{
	return thisList->ToCPPList() == nList->ToCPPList();
}

//Operator == (std::vector &)
template <typename T>
inline bool operator==(List<T> &thisList, list<T> &nList)
{
	return thisList->ToCPPList() == nList;
}

//Operator +=
template <typename T>
inline void operator+=(List<T> &thisList, T element)		//NOTE: Maybe references are possible, too.
{
	thisList->push_back(element);
}

#endif /*BLITZPROG_COLLECTION_LIST_HPP_*/

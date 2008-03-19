////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Collection.Interface
// Author:				Eduard Urbach
// Description:			Collection interface
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_COLLECTION_INTERFACE_HPP_
#define BLITZPROG_COLLECTION_INTERFACE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//TCollection
template <typename T>
class TCollection
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//Constructor
		TCollection()
		{
			//Debug info
			EngineLogNew("Collection");
		}
		
		//Destructor
		virtual ~TCollection()
		{
			//Debug info
			EngineLogDelete("Collection");
		}
		
		////////////////////////////////////////////////////////////////////////
		// Operators
		////////////////////////////////////////////////////////////////////////
		
		//Operator []
		virtual T &operator[](size_t index) = 0;
		
		//Operator []
		virtual const T &operator[](size_t index) const = 0;
		
		////////////////////////////////////////////////////////////////////////
		// Casts
		////////////////////////////////////////////////////////////////////////
		
		
		
		////////////////////////////////////////////////////////////////////////
		// Methods
		////////////////////////////////////////////////////////////////////////
		
		//Add
		virtual void Add(const T &element) = 0;
		
		//Add
		//virtual void Add(const SharedPtr<TCollection<T> > c) = 0;
		
		//Remove
		virtual bool Remove(const T &element) = 0;
		
		//RemoveAll
		virtual size_t RemoveAll(const T &value) = 0;
		
		//RemoveAll
		//virtual size_t RemoveAll(const SharedPtr<TCollection<T> > c) = 0;
		
		//RemoveElementByIndex
		virtual void RemoveElementByIndex(size_t index) = 0;
		
		//RetainAll
		//virtual size_t RetainAll(const SharedPtr<TCollection<T> > c) = 0;
		
		//Insert
		virtual void Insert(const T &element, size_t at) = 0;
		
		//InsertBefore
		virtual void InsertBefore(const T &element, const T &before) = 0;
		
		//InsertAfter
		virtual void InsertAfter(const T &element, const T &after) = 0;
		
		//GetElementByIndex
		virtual T &GetElementByIndex(size_t index) = 0;
		
		//GetElementByIndex
		virtual const T &GetElementByIndex(size_t index) const = 0;
		
		//CountOccurenceOf
		virtual size_t CountOccurenceOf(const T &value) const = 0;
		
		//Clear
		virtual void Clear() = 0;
		
		//Sort
		virtual void Sort(bool ascending = true) = 0;
		
		//Reverse
		virtual void Reverse(size_t from = 0, size_t to = -1) = 0;
		
		//Reverse
		virtual void Reverse(const T &from, const T &to) = 0;
		
		//Erase
		virtual void Erase(size_t index) = 0;
		
		//Erase
		virtual void Erase(size_t from, size_t to) = 0;
		
		//GetSize
		virtual size_t GetSize() const = 0;
		
		//Find
		virtual int Find(const T &element, size_t from=0) const = 0;	//TODO: Replace int
		
		//Contains
		virtual bool Contains(const T &element) const = 0;
		
		//ContainsAll
		//virtual bool ContainsAll(const SharedPtr<TCollection<T> > &element) const = 0;
		
		//IsEmpty
		virtual bool IsEmpty() const = 0;
		
		//GetBegin
		//virtual T *GetBegin() const = 0;
		
		//GetEnd
		//virtual T *GetEnd() const = 0;
		
		////////////////////////////////////////////////////////////////////////
		// Inline methods
		////////////////////////////////////////////////////////////////////////
		
		//GetLength
		inline size_t GetLength() const
		{
			return GetSize();
		}
		
		//GetSizeInBytes
		inline size_t GetSizeInBytes(const T &element) const
		{
			return GetSize() * sizeof(T);
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



#endif /*BLITZPROG_COLLECTION_INTERFACE_HPP_*/

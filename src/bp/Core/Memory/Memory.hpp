#include <cstring>

template <typename TSource, typename TDest, typename sizeType>
inline TDest *bp_copyMem(TSource *source, TDest *dest, const sizeType numBytes) {
	return static_cast<TDest*>(memcpy(dest, source, numBytes));
}

template <typename TSource, typename TDest, typename sizeType>
inline bool bp_compareMem(TSource *source, TDest *dest, const sizeType numBytes) {
	return memcmp(dest, source, numBytes) == 0;
}

/*template <typename TDataType>
class BPMemPointer {
	public:
		inline BPMemPointer() : ptr(NULL) {}
		inline BPMemPointer(Size size) : ptr(new TDataType[size]) {}
		inline BPMemPointer(BPMemPointer<TDataType> *memPtr) : ptr(memPtr->ptr) {}
		inline BPMemPointer(TDataType *memPtr) : ptr(memPtr) {}
		
		inline TDataType &getData() {
			return *ptr;
		}
		
		template <typename setType>
		inline void setData(const setType &newData) {
			*ptr = newData;
		}
		
		template <typename sizeType>
		inline TDataType operator [](sizeType index) {
			return ptr[index];
		}
		
		inline void operator =(TDataType *memPtr) {
			ptr = memPtr;
		}
		
		inline void operator =(const BPMemPointer &memPtr) {
			ptr = memPtr.ptr;
		}
		
		inline bool operator ==(const BPMemPointer &memPtr) {
			return ptr == memPtr.ptr;
		}
		
		template <typename sizeType>
		inline void operator +=(sizeType size) {
			ptr += size;
		}
		
		template <typename sizeType>
		inline void operator -=(sizeType size) {
			ptr -= size;
		}
		
		inline size_t operator-(const BPMemPointer<TDataType> &ref) {
			return ptr - ref.ptr;
		}
		
		inline BPMemPointer *operator->() {
			return this;
		}
		
		inline operator TDataType*() {
			return ptr;
		}
		
		inline void free() {
			delete [] ptr;
		}
		
	private:
		TDataType *ptr;
};*/

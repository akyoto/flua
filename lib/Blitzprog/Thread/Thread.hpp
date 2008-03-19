////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Thread
// Author:				Eduard Urbach
// Description:			Multithreading
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_THREAD_HPP_
#define BLITZPROG_THREAD_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>

//Boost
#include <boost/thread.hpp>
#include <boost/bind.hpp>

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//Thread
class TThread: public boost::thread
{
	public:
		
		////////////////////////////////////////////////////////////////////////
		// Constructors and destructors
		////////////////////////////////////////////////////////////////////////
		
		//TODO: More constructors
		
		//Constructor
		template <typename returnType>
		TThread(returnType (*func)()) : boost::thread(func)
		{
			
		}
		
		//Constructor: 1 parameter
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1>
		TThread(returnType (*func)(parameterFType1), parameterAType1 parameter1) : boost::thread(boost::bind(func, parameter1))
		{
			
		}

		//Constructor: 2 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2>
		TThread(returnType (*func)(parameterFType1, parameterFType2), parameterAType1 parameter1, parameterAType2 parameter2) : boost::thread(boost::bind(func, parameter1, parameter2))
		{
			
		}

		//Constructor: 3 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3))
		{
			
		}

		//Constructor: 4 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4))
		{
			
		}

		//Constructor: 5 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5))
		{
			
		}

		//Constructor: 6 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6))
		{
			
		}

		//Constructor: 7 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7))
		{
			
		}

		//Constructor: 8 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8))
		{
			
		}

		//Constructor: 9 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9))
		{
			
		}

		//Constructor: 10 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10))
		{
			
		}

		//Constructor: 11 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11))
		{
			
		}

		//Constructor: 12 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12))
		{
			
		}

		//Constructor: 13 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13))
		{
			
		}

		//Constructor: 14 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14))
		{
			
		}

		//Constructor: 15 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15))
		{
			
		}

		//Constructor: 16 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16))
		{
			
		}

		//Constructor: 17 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17))
		{
			
		}

		//Constructor: 18 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18))
		{
			
		}

		//Constructor: 19 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19))
		{
			
		}

		//Constructor: 20 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20))
		{
			
		}

		//Constructor: 21 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21))
		{
			
		}

		//Constructor: 22 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22))
		{
			
		}

		//Constructor: 23 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23))
		{
			
		}

		//Constructor: 24 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24))
		{
			
		}

		//Constructor: 25 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25))
		{
			
		}

		//Constructor: 26 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25, 
			typename parameterFType26, typename parameterAType26>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25, parameterFType26), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25, parameterAType26 parameter26) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25, parameter26))
		{
			
		}

		//Constructor: 27 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25, 
			typename parameterFType26, typename parameterAType26, 
			typename parameterFType27, typename parameterAType27>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25, parameterFType26, parameterFType27), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25, parameterAType26 parameter26, parameterAType27 parameter27) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25, parameter26, parameter27))
		{
			
		}

		//Constructor: 28 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25, 
			typename parameterFType26, typename parameterAType26, 
			typename parameterFType27, typename parameterAType27, 
			typename parameterFType28, typename parameterAType28>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25, parameterFType26, parameterFType27, parameterFType28), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25, parameterAType26 parameter26, parameterAType27 parameter27, parameterAType28 parameter28) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25, parameter26, parameter27, parameter28))
		{
			
		}

		//Constructor: 29 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25, 
			typename parameterFType26, typename parameterAType26, 
			typename parameterFType27, typename parameterAType27, 
			typename parameterFType28, typename parameterAType28, 
			typename parameterFType29, typename parameterAType29>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25, parameterFType26, parameterFType27, parameterFType28, parameterFType29), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25, parameterAType26 parameter26, parameterAType27 parameter27, parameterAType28 parameter28, parameterAType29 parameter29) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25, parameter26, parameter27, parameter28, parameter29))
		{
			
		}

		//Constructor: 30 parameters
		template <
			typename returnType, 
			typename parameterFType1, typename parameterAType1, 
			typename parameterFType2, typename parameterAType2, 
			typename parameterFType3, typename parameterAType3, 
			typename parameterFType4, typename parameterAType4, 
			typename parameterFType5, typename parameterAType5, 
			typename parameterFType6, typename parameterAType6, 
			typename parameterFType7, typename parameterAType7, 
			typename parameterFType8, typename parameterAType8, 
			typename parameterFType9, typename parameterAType9, 
			typename parameterFType10, typename parameterAType10, 
			typename parameterFType11, typename parameterAType11, 
			typename parameterFType12, typename parameterAType12, 
			typename parameterFType13, typename parameterAType13, 
			typename parameterFType14, typename parameterAType14, 
			typename parameterFType15, typename parameterAType15, 
			typename parameterFType16, typename parameterAType16, 
			typename parameterFType17, typename parameterAType17, 
			typename parameterFType18, typename parameterAType18, 
			typename parameterFType19, typename parameterAType19, 
			typename parameterFType20, typename parameterAType20, 
			typename parameterFType21, typename parameterAType21, 
			typename parameterFType22, typename parameterAType22, 
			typename parameterFType23, typename parameterAType23, 
			typename parameterFType24, typename parameterAType24, 
			typename parameterFType25, typename parameterAType25, 
			typename parameterFType26, typename parameterAType26, 
			typename parameterFType27, typename parameterAType27, 
			typename parameterFType28, typename parameterAType28, 
			typename parameterFType29, typename parameterAType29, 
			typename parameterFType30, typename parameterAType30>
		TThread(returnType (*func)(parameterFType1, parameterFType2, parameterFType3, parameterFType4, parameterFType5, parameterFType6, parameterFType7, parameterFType8, parameterFType9, parameterFType10, parameterFType11, parameterFType12, parameterFType13, parameterFType14, parameterFType15, parameterFType16, parameterFType17, parameterFType18, parameterFType19, parameterFType20, parameterFType21, parameterFType22, parameterFType23, parameterFType24, parameterFType25, parameterFType26, parameterFType27, parameterFType28, parameterFType29, parameterFType30), parameterAType1 parameter1, parameterAType2 parameter2, parameterAType3 parameter3, parameterAType4 parameter4, parameterAType5 parameter5, parameterAType6 parameter6, parameterAType7 parameter7, parameterAType8 parameter8, parameterAType9 parameter9, parameterAType10 parameter10, parameterAType11 parameter11, parameterAType12 parameter12, parameterAType13 parameter13, parameterAType14 parameter14, parameterAType15 parameter15, parameterAType16 parameter16, parameterAType17 parameter17, parameterAType18 parameter18, parameterAType19 parameter19, parameterAType20 parameter20, parameterAType21 parameter21, parameterAType22 parameter22, parameterAType23 parameter23, parameterAType24 parameter24, parameterAType25 parameter25, parameterAType26 parameter26, parameterAType27 parameter27, parameterAType28 parameter28, parameterAType29 parameter29, parameterAType30 parameter30) : boost::thread(boost::bind(func, parameter1, parameter2, parameter3, parameter4, parameter5, parameter6, parameter7, parameter8, parameter9, parameter10, parameter11, parameter12, parameter13, parameter14, parameter15, parameter16, parameter17, parameter18, parameter19, parameter20, parameter21, parameter22, parameter23, parameter24, parameter25, parameter26, parameter27, parameter28, parameter29, parameter30))
		{
			
		}
		
		//Destructor
		~TThread()
		{
			
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
		
		//Join
		inline void Join()
		{
			this->join();
		}
		
		//Friends
		//friend inline bool operator==(TThread &t1, TThread &t2);
		//friend inline bool operator!=(TThread &t1, TThread &t2);
};
typedef SharedPtr<TThread> Thread;
#define CreateThread new TThread

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



#endif /*BLITZPROG_THREAD_HPP_*/

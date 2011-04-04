#ifndef bp_Thread_hpp
#define bp_Thread_hpp

#include <boost/thread/thread.hpp>

/*volatile int counter;
boost::mutex m;

void bp_helloWorld(int iterationsPerThread)
{
	//bp_print(iterationsPerThread);
	
	float a;
	float b;
	float result;
	float result2;
	float result3;
	float result4;
	
	boost::mutex::scoped_lock l(m);
	for(int i = 0; i < iterationsPerThread; ++i) {
		a = rand();
		b = rand();
		result = a * b / (a + b);
		result2 = a * result / (a + result);
		result3 = a * b / (result + result2);
		result4 = a * result / (result2 + result3);
		result *= result2 * result3 * result4;
	}
}

void bp_testThreads() {
	int start;
	int numberOfThreads = 1;
	int iterationsPerThread = 500000;
	
	srand(1337);
	
	while(numberOfThreads <= 16) {
		std::cout << "#Threads: " << numberOfThreads << " x " << iterationsPerThread << " iterations" << std::endl;
		
		boost::thread **thrd = new boost::thread*[numberOfThreads];
		
		int a;
		for(a = 0; a < numberOfThreads; ++a) {
			thrd[a] = new boost::thread(&bp_helloWorld, iterationsPerThread);
		}
		
		start = bp_systemTime();
			for(a = 0; a < numberOfThreads; ++a) {
				thrd[a]->join();
			}
		start = bp_systemTime() - start;
		std::cout << "Multi:  " << start << " ms" << std::endl;
		
		//bp_print(counter);
		
		for(a = 0; a < numberOfThreads; ++a) {
			delete thrd[a];
		}
		delete [] thrd;
		
		// next step
		numberOfThreads *= 2;
		iterationsPerThread /= 2;
	}
	
	counter = 0;
	
	std::cout << std::endl;
	
	start = bp_systemTime();
		int maxNum = numberOfThreads * iterationsPerThread;
		
		bp_helloWorld(maxNum);
	start = bp_systemTime() - start;
	std::cout << "Single: " << start << " ms" << std::endl << std::endl;
}*/

#endif

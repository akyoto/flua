// Simple wrapper functions
#define BP_WRAP_1(_TYPE, _BP_FUNC, _C_FUNC) template <typename _T> inline _TYPE _BP_FUNC (_T _param) { return _C_FUNC(_param); }
#define BP_WRAP_2(_TYPE, _BP_FUNC, _C_FUNC) template <typename _T1, typename _T2> inline _TYPE _BP_FUNC (_T1 _param1, _T2 _param2) { return _C_FUNC(_param1, _param2); }

//#ifdef __linux__
// 	//include <sys/wait.h>
// 	//include <unistd.h>
// 	
// 	void flua_dumpBacktrace(int) {
// 		pid_t dying_pid = getpid();
// 		pid_t child_pid = fork();
// 		if (child_pid < 0) {
// 			perror("fork() while collecting backtrace:");
// 		} else if (child_pid == 0) {
// 			char buf[1024];
// 			sprintf(buf, "gdb -p %d -batch -ex bt 2>/dev/null | "
// 			             "sed '0,/<signal handler/d'", dying_pid);
// 			const char* argv[] = {"sh", "-c", buf, NULL};
// 			execve("/bin/sh", (char**)argv, NULL);
// 			_exit(1);
// 		} else {
// 			waitpid(child_pid, NULL, 0);
// 		}
// 		_exit(1);
// 	}
// 	
// 	void flua_backtraceOnSegv() {
// 		struct sigaction action = {};
// 		action.sa_handler = flua_dumpBacktrace;
// 		if (sigaction(SIGSEGV, &action, NULL) < 0) {
// 			perror("sigaction(SEGV)");
// 		}
// 	}
//#endif
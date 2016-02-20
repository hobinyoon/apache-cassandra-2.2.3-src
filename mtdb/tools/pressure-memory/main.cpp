#include <string.h>
#include <stdio.h>
#include <unistd.h>

#include <algorithm>
#include <iostream>
#include <sstream>

// Not implemented on Ubuntu 14.04, g++ 4.8.4
// #include <regex>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include "conf.h"
#include "util.h"

using namespace std;


// A child process is pre-created and serves memory pressure requests. Parent
// process is free to call fork() without having to worry about duplicating the
// child process's memory.
class MemPressurer {
private:
	// pipefd[0] refers to the read end of the pipe. pipefd[1] refers to the
	// write end of the pipe.
	// Parent-to-child and child-to-parent pipes
	int pipe_pc[2];
	int pipe_cp[2];
	vector<char*> allocated_mem;

	// Child process
	void _ServeRequests() {
		while (true) {
			char cmd;
			Util::readn(pipe_pc[0], &cmd, sizeof(cmd));
			if (cmd == 'a') {
				int to_alloc_mb;
				Util::readn(pipe_pc[0], &to_alloc_mb, sizeof(to_alloc_mb));

				boost::timer::cpu_timer timer;
				int allocated = 0;
				for (int i = 0; i < (to_alloc_mb / Conf::mem_alloc_chunk_mb); i ++) {
					char* c = new (nothrow) char[Conf::mem_alloc_chunk_mb * 1024 * 1024];
					if (c == NULL) {
						cout << boost::format("Could not allocate. i=%d\n") % i;
						break;
					}
					// It works with just initializing the memory, without
					// randomization. The kernel doesn't have compressed memory on.
					memset(c, 0, Conf::mem_alloc_chunk_mb * 1024 * 1024);
					allocated_mem.push_back(c);
					allocated += Conf::mem_alloc_chunk_mb;
				}
				//cout << boost::format("C: Allocated %d MB of memory in %f sec\n")
				//	% allocated % (timer.elapsed().wall / 1000000000.0);
				cout << boost::format("a:%d ") % allocated << flush;
			} else if (cmd == 'f') {
				int to_free_mb;
				Util::readn(pipe_pc[0], &to_free_mb, sizeof(to_free_mb));

				boost::timer::cpu_timer timer;
				int freed = 0;
				for (int i = 0; i < (to_free_mb / Conf::mem_alloc_chunk_mb); i ++) {
					if (allocated_mem.size() == 0)
						break;
					char* c = allocated_mem.back();
					allocated_mem.pop_back();
					delete[] c;
					freed += Conf::mem_alloc_chunk_mb;
				}
				//cout << boost::format("C: Freed %d MB of memory in %f sec\n")
				//	% freed % (timer.elapsed().wall / 1000000000.0);
				cout << boost::format("f:%d ") % freed << flush;
			} else {
				throw runtime_error(str(boost::format("Unexpected cmd=[%c]") % cmd));
			}

			// Done
			char response = 'd';
			Util::writen(pipe_cp[1], &response, sizeof(response));
		}
	}

	void _PipeAndFork() {
		if (pipe(pipe_pc) == -1)
			throw runtime_error(str(boost::format("pipe() failed: errno=%d") % errno));
		if (pipe(pipe_cp) == -1)
			throw runtime_error(str(boost::format("pipe() failed: errno=%d") % errno));

		pid_t pid = fork();
		if (pid == 0) {
			// Child. Close unused ends.
			close(pipe_pc[1]);
			close(pipe_cp[0]);
			_ServeRequests();
		} else if (pid < 0) {
			throw runtime_error(str(boost::format("fork() failed: errno=%d") % errno));
		} else {
			// Parent. Close unused ends.
			close(pipe_pc[0]);
			close(pipe_cp[1]);
		}
	}

public:
	MemPressurer() {
		_PipeAndFork();
	}

	// These two are called by parent

	void Alloc(int to_alloc_mb) {
		const char cmd = 'a';
		Util::writen(pipe_pc[1], &cmd, sizeof(cmd));
		Util::writen(pipe_pc[1], &to_alloc_mb, sizeof(int));

		char response;
		Util::readn(pipe_cp[0], &response, sizeof(response));
		if (response != 'd')
			throw runtime_error(str(boost::format("Unexpected response [%c]") % response));
	}

	void Free(int to_free_mb) {
		const char cmd = 'f';
		Util::writen(pipe_pc[1], &cmd, sizeof(cmd));
		Util::writen(pipe_pc[1], &to_free_mb, sizeof(int));

		char response;
		Util::readn(pipe_cp[0], &response, sizeof(response));
		if (response != 'd')
			throw runtime_error(str(boost::format("Unexpected response [%c]") % response));
	}
};


// Pre-fork memory pressurer sub process
MemPressurer _mp;


//void GetFreeAndCachedMemorySizeMbCpp11(int& free, int& cached) {
//	free = cached = 0;
//
//	string lines = Util::exec("free -mt");
//	//              total       used       free     shared    buffers     cached
//	// Mem:         11991      11576        415         16        116      10938
//	// -/+ buffers/cache:        521      11469
//	// Swap:            0          0          0
//	// Total:       11991      11576        415
//
//	// swap partition better be disabled. EC2 EBS-backed instances don't have swap. Good.
//	stringstream ss(lines);
//
//	// On Ubuntu 14.04, g++ 4.8.4, this throws an regex_error. Interesting that it compiles.
//	// http://stackoverflow.com/questions/15671536/why-does-this-c11-stdregex-example-throw-a-regex-error-exception
//	regex rgx("^Mem:\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+");
//
//	string line;
//	const auto sep = boost::is_any_of(" ");
//	while (getline(ss, line, '\n')) {
//		//cout << boost::format("[%s]\n") % line;
//		smatch match;
//		if (regex_search(line, match, rgx)) {
//			vector<string> tokens;
//			boost::split(tokens, line, sep, boost::token_compress_on);
//			if (tokens.size() != 7)
//				throw runtime_error(str(boost::format("Unexpected format [%s]") % line));
//			free = atoi(tokens[3].c_str());
//			cached = atoi(tokens[6].c_str());
//			return;
//		}
//	}
//
//	throw runtime_error(str(boost::format("Unexpected format [%s]") % lines));
//}


// A thread-safe queue
class OutputQueue {
private:
	queue<string> _q;

public:
	void Put(char* line) {
		// TODO: lock
		_q.push(line);
	}

	string Get() {
		string latest_line;

		while (!_q.empty()) {
			latest_line = _q.front();
			myqueue.pop();

			_q.pop();
		}

		while (_q.empty()) {
			// TODO: wait for a notification
		}
		_q.pop();
		// TODO: get the latest one.
	}
};

OutputQueue output_q;


void PressureMemory() {
	string line = output_q.GetLatest();

	// Careful not to trigger OOM killer. If the free memory is too small, no
	// more allocation.

	// swap partition better be disabled. EC2 EBS-backed instances don't have
	// swap. Good.
	static const auto sep = boost::is_any_of(" ");
	vector<string> tokens;
	boost::split(tokens, line, sep, boost::token_compress_on);
	if (tokens.size() == 0)
		return;
	if (tokens[0] != "Mem:")
		return;
	if (tokens.size() != 7)
		throw runtime_error(str(boost::format("Unexpected format [%s]") % line));
	int free = atoi(tokens[3].c_str());
	int cached = atoi(tokens[6].c_str());

	// 1. Initial pressure. Pressure till there is (128MB) free memory left
	// 2. Pressure till cached becomes below (16MB), while making sure free is above (64MB)
	//   2.1 After pressuing, back off to secure (512MB) of free memory.
	//   Go back to step 2
	static int phase = 1;
	if (phase == 1) {
		int to_pressure = free - Conf::initial_pressure_free_mb;
		to_pressure = (to_pressure / Conf::mem_alloc_chunk_mb) * Conf::mem_alloc_chunk_mb;
		_mp.Alloc(to_pressure);
		// TODO: I see the problem. This takes too long and the next free, cached are outdated.
		cout << boost::format("\nS: switch to phase=%d\n") % phase;
		phase = 2;
	} else if (phase == 2) {
		int need_to_return = Conf::pressure_free_lower_bound_mb - free;
		need_to_return = (need_to_return / Conf::mem_alloc_chunk_mb) * Conf::mem_alloc_chunk_mb;
		if (need_to_return > 0) {
			_mp.Free(need_to_return);
		} else {
			int to_pressure = cached - Conf::cached_memory_target_mb;
			if (to_pressure < 0) {
				// Back off
				int free_back_off = ((Conf::free_back_off_mb - free) / Conf::mem_alloc_chunk_mb) * Conf::mem_alloc_chunk_mb;
				if (free_back_off > 0)
					_mp.Free(free_back_off);
			} else {
				int room_to_pressure = free - Conf::pressure_free_lower_bound_mb;
				room_to_pressure = (room_to_pressure / Conf::mem_alloc_chunk_mb) * Conf::mem_alloc_chunk_mb;
				to_pressure = std::min(to_pressure, room_to_pressure);
				to_pressure = (to_pressure / Conf::mem_alloc_chunk_mb) * Conf::mem_alloc_chunk_mb;
				if (to_pressure > 0)
					_mp.Alloc(to_pressure);
			}
		}
	}
}


int main() {
	//              total       used       free     shared    buffers     cached
	// Mem:         11991      11576        415         16        116      10938
	// -/+ buffers/cache:        521      11469
	// Swap:            0          0          0
	// Total:       11991      11576        415

	// fork(), called by popen(), fails when there is not enough free memory.
	// Even with pre-fork, this seems to consume quite a lot of memory. Maybe C++
	// runtime and boost library.
	//
	// Forking once, by making "free" continuously report.
	const char* cmd = "free -mt -s 0.2";
	FILE* pipe = popen(cmd, "r");
	if (pipe == NULL) {
		if (errno == ENOMEM) {
			cerr << "popen failed: ENOMEM\n";
			exit(1);
		} else {
			cerr << boost::format("Popen returned NULL. errno=%d\n") % errno;
			exit(1);
		}
	}

	thread t_pm(PressureMemory);

	// 1024 is enough for the output of free, since I know the output.
	const int bufsize = 1024;
	char buffer[bufsize];
	char* bp = buffer;
	while (!feof(pipe)) {
		*bp = fgetc(pipe);
		if (*bp == '\n') {
			*bp = '\0';
			output_q.Put(buffer);
			bp = buffer;
		} else {
			bp ++;
			if (bp - buffer >= bufsize)
				throw runtime_error("Unexpected output from free");
		}
	}

	// Won't reach here
	t_pm.join();
	pclose(pipe);

	// TODO: How does OOM killer selects a victim process? Can a child of this
	// process be always selected?

	// TODO: Keep the cached memory size to proportional to the shrinked heap size
	// c3.2xlarge has 15 GB of memory.
	// Measure the heap memory size of unmodified Cassandra and cached size.
	// Should have a better idea then.

	return 0;
}

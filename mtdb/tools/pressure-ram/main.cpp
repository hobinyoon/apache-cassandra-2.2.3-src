#include <string.h>
#include <stdio.h>
#include <unistd.h>

#include <algorithm>
#include <iostream>
#include <regex>
#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include "util.h"

using namespace std;


// Cached memory size in mb
void GetFreeAndCachedMemorySizeMb(int& free, int& cached) {
	free = cached = 0;

	string lines = Util::exec("free -mt");
	//              total       used       free     shared    buffers     cached
	// Mem:         11991      11576        415         16        116      10938
	// -/+ buffers/cache:        521      11469
	// Swap:            0          0          0
	// Total:       11991      11576        415

	// TODO: think about what to do with swap
	stringstream ss(lines);
	regex rgx("^Mem:\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+");

	string line;
	const auto sep = boost::is_any_of(" ");
	while (getline(ss, line, '\n')) {
		//cout << boost::format("[%s]\n") % line;
		smatch match;
		if (regex_search(line, match, rgx)) {
			vector<string> tokens;
			boost::split(tokens, line, sep, boost::token_compress_on);
			if (tokens.size() != 7)
				throw runtime_error(str(boost::format("Unexpected format [%s]") % line));
			free = atoi(tokens[3].c_str());
			cached = atoi(tokens[6].c_str());
			return;
		}
	}

	throw runtime_error(str(boost::format("Unexpected format [%s]") % lines));
}


// TODO: good name?
class SubProcPipe {
private:
	// pipefd[0] refers to the read end of the pipe. pipefd[1] refers to the
	// write end of the pipe.
	// Parent-to-child and child-to-parent pipes
	int pipe_pc[2];
	int pipe_cp[2];

	// Child process
	void _ServeRequests() {
		while (true) {
			char cmd;
			Util::readn(pipe_pc[0], &cmd, 1);
			if (cmd != 'w')
				throw runtime_error(str(boost::format("Unexpected cmd=[%c]") % cmd));
			//cout << "C: received a request\n";
			int free, cached;
			GetFreeAndCachedMemorySizeMb(free, cached);

			Util::writen(pipe_cp[1], &free, sizeof(free));
			Util::writen(pipe_cp[1], &cached, sizeof(cached));
			//cout << boost::format("C: returned %d, %d\n") % free % cached;
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
	SubProcPipe() {
		_PipeAndFork();
	}

	// Called by parent
	void GetFreeMem(int& free, int& cached) {
		// "w": work, child.
		Util::writen(pipe_pc[1], "w", 1);

		Util::readn(pipe_cp[0], &free, sizeof(free));
		Util::readn(pipe_cp[0], &cached, sizeof(cached));
	}
};


int main() {
	SubProcPipe spp;
	vector<char*> allocated_mem;

	while (true) {
		int free, cached;
		spp.GetFreeMem(free, cached);
		cout << boost::format("S: %d, %d\n") % free % cached;

		try {
			const int cached_memory_allowance_mb = 128;
			const int free_memory_allowance_mb = 256;
			int to_alloc = std::min(free - free_memory_allowance_mb, cached - cached_memory_allowance_mb);

			//const int _1mb = 1024 * 1024;
			const int mem_alloc_chunk_mb = 10;

			if (to_alloc > 0) {
				cout << boost::format("Allocating %d MB of memory ... ") % to_alloc << flush;
				boost::timer::cpu_timer timer;

				for (int j = 0; j < (to_alloc / mem_alloc_chunk_mb); j ++) {
					char* c = new (nothrow) char[mem_alloc_chunk_mb * 1024 * 1024];
					if (c == NULL) {
						cout << boost::format("Could not allocate. j=%d\n") % j;
						break;
					}
					// Need to randomize content?
					memset(c, 0, mem_alloc_chunk_mb * 1024 * 1024);
					allocated_mem.push_back(c);
				}
				//cout << boost::format("\n");

				cout << boost::format("%f sec\n") % (timer.elapsed().wall / 1000000000.0);
			} else {
				// TODO: lower the pressure
			}
		} catch (const Util::ErrorNoMem& e) {
				cout << "ErrorNoMem\n";
		}

		// Sleep for 0.1 sec
		// TODO: make it configurable.
		struct timespec req;
		req.tv_sec = 0;
		req.tv_nsec = 500000000;
		nanosleep(&req, NULL);
	}




//	while (true) {
//		int free, cached;
//		try {
//			GetFreeAndCachedMemorySizeMb(free, cached);
//			//cout << boost::format("%ld\n") % cached;
//
//
//		// Sleep for 0.1 sec
//		// TODO: make it configurable.
//		struct timespec req;
//		req.tv_sec = 0;
//		req.tv_nsec = 100000000;
//		nanosleep(&req, NULL);
//	}

	// TODO: Keep the cached memory size to proportional to the shrinked heap size
	// c3.2xlarge has 15 GB of memory.
	// @ Measure the heap memory size of unmodified Cassandra, and calculate the shrink ratio
	//
	//
	// like 100 MB

	return 0;
}

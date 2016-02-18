#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <algorithm>
#include <iostream>
#include <mutex>
#include <random>
#include <regex>
#include <thread>

#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>

#include "conf.h"
#include "util.h"

using namespace std;

class LatMon {
private:
	long sum = 0;
	long cnt = 0;
	thread* t = NULL;
	std::mutex _mutex;

	void _SpawnReporter() {
		t = new thread(&LatMon::_Report, this);
	}

	void _Report() {
		while (true) {
			sleep(1);

			{
				lock_guard<mutex> _(_mutex);

				if (cnt == 0) {
					cout << "-\n";
				} else {
					double avg = ((double) sum) / cnt;
					cout << boost::format("%7.0f ns %ld\n") % avg % cnt;
				}
				sum = 0;
				cnt = 0;
			}
		}
	}

public:
	LatMon() {
		_SpawnReporter();
	}

	void Add(long lap_time, long cnt_) {
		lock_guard<mutex> _(_mutex);
		sum += lap_time;
		cnt += cnt_;
	}

	void Join() {
		t->join();
	}
};


int main() {
	LatMon lm;

	const char* fn = Conf::fn_tmp;

	long file_size = Util::GetFileSize(fn);
	cout << boost::format("%s %d\n") % fn % file_size;

	//int fd = open(fn, O_RDONLY | O_DIRECT);
	int fd = open(fn, O_RDONLY);

	const int bufsize = 4 * 1024;
	
	// buffer Needs to be aligned for direct IO
	// http://stackoverflow.com/questions/10996539/read-from-a-hdd-with-o-direct-fails-with-22-einval-invalid-argument
	//char buf[bufsize] __attribute__ ((__aligned__ (4*1024)));
	char buf[bufsize] __attribute__ ((__aligned__ (512)));

	// http://stackoverflow.com/questions/13445688/how-do-generate-a-random-number-in-c
	std::mt19937 rng;
	rng.seed(std::random_device()());
	// distribution in range [a, b]
	int b = (file_size / bufsize) - 1;
	if (b < 0)
		throw runtime_error(str(boost::format("Unexpected file_size=%d bufsize=%d") % file_size % bufsize));
	std::uniform_int_distribution<std::mt19937::result_type> randdist(0, b);

	while (true) {
		boost::timer::cpu_timer timer;
		for (int i = 0; i < Conf::num_rand_reads_at_a_time; i ++) {
			off_t offset = randdist(rng) * bufsize;
			//cout << boost::format("offset=%d\n") % offset;
			if (lseek(fd, offset, SEEK_SET) == -1) {
				cerr << boost::format("lseek() failed. errno=%d\n") % errno;
				exit(-1);
			}
			ssize_t read_bytes = read(fd, buf, bufsize);
			if (read_bytes == 0) {
				cout << "done\n";
				exit(0);
			} else if (read_bytes == -1) {
				cerr << boost::format("read() failed. errno=%d\n") % errno;
				exit(-1);
			} else if (read_bytes != bufsize) {
				cerr << boost::format("read() returned %d\n") % read_bytes;
				// It happens at the end of the file.
			}
		}
		lm.Add(timer.elapsed().wall, Conf::num_rand_reads_at_a_time);
	}

	close(fd);
	lm.Join();

	return 0;
}

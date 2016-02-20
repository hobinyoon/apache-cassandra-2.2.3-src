#include <string>
#include <memory>
#include <boost/format.hpp>

#include "util.h"

using namespace std;

namespace Util {
	std::string exec(const char* cmd) {
		// http://stackoverflow.com/questions/478898/how-to-execute-a-command-and-get-output-of-command-within-c

		// fork(), which is called by popen(), fails when the parent process
		// already consumes a lot of memory.
		FILE* pipe = popen(cmd, "r");
		if (pipe == NULL) {
			if (errno == ENOMEM) {
				throw ErrorNoMem();
			} else {
				throw runtime_error(str(boost::format("Popen returned NULL. errno=%d") % errno));
			}
		}

		const size_t BUFSIZE = 1024;
		char buffer[BUFSIZE];
		string result = "";
		while (!feof(pipe)) {
			if (fgets(buffer, BUFSIZE, pipe) != NULL)
				result += buffer;
		}

		pclose(pipe);

		return result;
	}


	// http://www.informit.com/articles/article.aspx?p=169505&seqNum=9
	ssize_t writen(int fd, const void *vptr, size_t n) {
		const char *ptr = static_cast<const char*>(vptr);
		size_t nleft = n;
		ssize_t nwritten = 0;
		while (nleft > 0) {
			if ( (nwritten = write(fd, ptr, nleft)) <= 0) {
				if (nwritten < 0 && errno == EINTR) {
					nwritten = 0;   // and call write() again
				} else {
					throw runtime_error(str(boost::format("write() failed. errno=%d") % errno));
				}
			}

			nleft -= nwritten;
			ptr += nwritten;
		}

		return n;
	}


	ssize_t readn(int fd, void *vptr, size_t n) {
		char* ptr = static_cast<char*>(vptr);
		size_t  nleft = n;
		ssize_t nread = 0;
		while (nleft > 0) {
			if ( (nread = read(fd, ptr, nleft)) < 0) {
				if (errno == EINTR)
					nread = 0;	// and call read() again
				else
					throw runtime_error(str(boost::format("read() failed. errno=%d") % errno));
			} else if (nread == 0)
				break;	// EOF

			nleft -= nread;
			ptr += nread;
		}

		return (n - nleft);	// return >= 0
	}


	CpuTimer::CpuTimer(const string& msg, int indent) {
		_tmr = new boost::timer::cpu_timer();
		_indent = indent;
		for (int i = 0; i < _indent; i ++)
			cout << " ";
		cout << msg;
	}

	CpuTimer::~CpuTimer() {
		for (int i = 0; i < _indent + 2; i ++)
			cout << " ";
		cout << _tmr->elapsed().wall / 1000000000.0 << " sec.\n";
		delete _tmr;
	}
}

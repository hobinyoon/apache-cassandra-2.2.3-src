#pragma once

#include <string>
#include <boost/timer/timer.hpp>

namespace Util {
	class ErrorNoMem { };

	std::string exec(const char* cmd);

	ssize_t writen(int fd, const void *vptr, size_t n);
	ssize_t readn(int fd, void *vptr, size_t n);

	struct CpuTimer {
		boost::timer::cpu_timer* _tmr;
		int _indent;
		CpuTimer(const std::string& msg, int indent = 0);
		~CpuTimer();
	};
}

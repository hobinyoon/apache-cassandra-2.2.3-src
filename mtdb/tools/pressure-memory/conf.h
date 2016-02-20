#pragma once

namespace Conf {
	const int cached_memory_target_mb = 16;

	//const int free_lower_bound_mb = 128;
	const int free_lower_bound_mb = 64;

	const int free_back_off_mb = 512;

	const int mem_alloc_chunk_mb = 10;

	const long sleep_nsec = 100000000;
	//                      123456789
};

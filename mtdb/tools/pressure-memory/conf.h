#pragma once

namespace Conf {
	const int cached_memory_target_mb = 64;
	const int free_memory_after_pressure_mb = 2048;

	//const int free_lower_bound_mb = 128;
	const int free_lower_bound_mb = 32;

	const int mem_alloc_chunk_mb = 10;

	const long sleep_nsec = 100000000;
	//                      123456789
};

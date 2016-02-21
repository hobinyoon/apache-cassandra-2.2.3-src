#pragma once

namespace Conf {
	const int initial_pressure_free_mb = 1024;

	const int pressure_free_lower_bound_mb = 768;

	const int cached_memory_target_mb = 36;

	const int free_back_off_mb = 512;

	const int mem_alloc_chunk_mb = 4;

	const long sleep_nsec = 100000000;
	//                      123456789
};

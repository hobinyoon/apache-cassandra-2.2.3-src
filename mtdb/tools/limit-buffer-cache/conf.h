#pragma once

namespace Conf {
	const int cached_memory_target_mb = 64;
	const int free_memory_target_mb = 1024;

	const int free_lower_bound_mb = 96;

	const int mem_alloc_chunk_mb = 10;

	const long sleep_nsec = 500000000;
};

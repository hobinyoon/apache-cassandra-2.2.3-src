package mtdb;

import java.util.concurrent.atomic.AtomicLong;

// Latency (response time. time to get a whole record, not the first byte.)
// monitor

class LatMon {
	static AtomicLong _writeTime = new AtomicLong(0);
	static AtomicLong _writeCnt = new AtomicLong(0);
	static AtomicLong _readTime = new AtomicLong(0);
	static AtomicLong _readCnt = new AtomicLong(0);

	public static void Write(long time) {
		_writeTime.addAndGet(time);
		_writeCnt.incrementAndGet();
	}

	public static void Read(long time) {
		_readTime.addAndGet(time);
		_readCnt.incrementAndGet();
	}

	public static class Result {
		long avgWriteTime;
		long avgReadTime;
		long writeCnt;
		long readCnt;
	}

	public static Result GetAndReset() {
		Result r = new Result();

		// Not a strongly consistent implementation. We prefer performance.
		long totalWriteTime = _writeTime.getAndSet(0);
		r.writeCnt = _writeCnt.getAndSet(0);
		r.avgWriteTime = (r.writeCnt == 0) ? 0 : (totalWriteTime / r.writeCnt);

		long totalReadTime = _readTime.getAndSet(0);
		r.readCnt = _readCnt.getAndSet(0);
		r.avgReadTime = (r.readCnt == 0) ? 0 : (totalReadTime / r.readCnt);

		return r;
	}
}

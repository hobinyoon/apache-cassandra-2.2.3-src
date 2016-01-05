package mtdb;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

// Latency (response time. time to get a whole record, not the first byte.)
// monitor

class LatMon {
	static List<Long> _writeTimes = new ArrayList();
	static List<Long> _readTimes = new ArrayList();
	static List<Long> _writeTimesAll = new ArrayList();
	static List<Long> _readTimesAll = new ArrayList();

	public static void Write(long time) {
		synchronized (_writeTimes) {
			_writeTimes.add(time);
		}
	}

	public static void Read(long time) {
		synchronized (_readTimes) {
			_readTimes.add(time);
		}
	}

	public static class Result {
		long avgWriteTime;
		long avgReadTime;
		long writeCnt;
		long readCnt;
	}

	public static Result GetAndReset() {
		Result res = new Result();

		{
			long sum = 0;
			long cnt = 0;
			synchronized (_writeTimes) {
				for (long w: _writeTimes) {
					sum += w;
					cnt ++;
					_writeTimesAll.add(w);
				}
				_writeTimes.clear();
			}
			res.writeCnt = cnt;
			res.avgWriteTime = (cnt == 0) ? 0 : (sum / cnt);
		}
		{
			long sum = 0;
			long cnt = 0;
			synchronized (_readTimes) {
				for (long r: _readTimes) {
					sum += r;
					cnt ++;
					_readTimesAll.add(r);
				}
				_readTimes.clear();
			}
			res.readCnt = cnt;
			res.avgReadTime = (cnt == 0) ? 0 : (sum / cnt);
		}

		return res;
	}

	public static class Stat {
		long cnt;
		long min;
		long max;
		long avg;
		long _50;
		long _90;
		long _95;
		long _99;

		// Note: values are sorted
		Stat(List<Long> values) {

			Collections.sort(values);
			min = values.get(0);
			max = values.get(values.size() - 1);

			boolean set_50 = false;
			boolean set_90 = false;
			boolean set_95 = false;
			boolean set_99 = false;
			long sum = 0;
			cnt = 0;
			int v_size = values.size();
			for (int i = 0; i < v_size; i ++) {
				if ((set_50 == false) && (i >= 0.5 * v_size)) {
					_50 = values.get(i);
					set_50 = true;
				}
				if ((set_90 == false) && (i >= 0.5 * v_size)) {
					_90 = values.get(i);
					set_90 = true;
				}
				if ((set_95 == false) && (i >= 0.5 * v_size)) {
					_95 = values.get(i);
					set_95 = true;
				}
				if ((set_99 == false) && (i >= 0.5 * v_size)) {
					_99 = values.get(i);
					set_99 = true;
				}
				sum += values.get(i);
				cnt ++;
			}
			avg = (cnt == 0) ? 0 : (sum / cnt);
		}
	}

	public static Stat GetWriteStat() {
		Stat stat = new Stat(_writeTimesAll);
		return stat;
	}

	public static Stat GetReadStat() {
		Stat stat = new Stat(_readTimesAll);
		return stat;
	}
}


//class LatMon {
//	static AtomicLong _writeTime = new AtomicLong(0);
//	static AtomicLong _writeCnt = new AtomicLong(0);
//	static AtomicLong _readTime = new AtomicLong(0);
//	static AtomicLong _readCnt = new AtomicLong(0);
//
//	public static void Write(long time) {
//		_writeTime.addAndGet(time);
//		_writeCnt.incrementAndGet();
//	}
//
//	public static void Read(long time) {
//		_readTime.addAndGet(time);
//		_readCnt.incrementAndGet();
//	}
//
//	public static class Result {
//		long avgWriteTime;
//		long avgReadTime;
//		long writeCnt;
//		long readCnt;
//	}
//
//	public static Result GetAndReset() {
//		Result r = new Result();
//
//		// Not a strongly consistent implementation. We prefer performance.
//		long totalWriteTime = _writeTime.getAndSet(0);
//		r.writeCnt = _writeCnt.getAndSet(0);
//		r.avgWriteTime = (r.writeCnt == 0) ? 0 : (totalWriteTime / r.writeCnt);
//
//		long totalReadTime = _readTime.getAndSet(0);
//		r.readCnt = _readCnt.getAndSet(0);
//		r.avgReadTime = (r.readCnt == 0) ? 0 : (totalReadTime / r.readCnt);
//
//		return r;
//	}
//}

from __future__ import print_function, division

# Extensive tests of the similarity search functions
import unittest2
import sys
import random
import contextlib

import chemfp
from chemfp import search
from chemfp import bitops
from chemfp import fps_search

import support

FULL_TEST = False

def _get_flag():
    import sys
    for (option, retval) in (
            ("--fast", "fast"),
            ("--full", "full")):
        try:
            i = sys.argv.index(option)
        except ValueError:
            continue
        del sys.argv[i]
        return retval
    return None


NUM_BITS = 128

if __name__ == "__main__":
    flag = _get_flag()
    if flag in ("fast", None):
        FULL_TEST = False
    elif flag == "full":
        FULL_TEST = True
        NUM_BITS = 1024
    else:
        raise AssertionError(flag)


_everything_arena = None
_everything_slow_arena = None
_everything_fps = None
def get_everything_data():
    global _everything_arena, _everything_fps, _everything_slow_arena
    if _everything_arena is None:
        fps = []
        bitlist = []
        for i in range(NUM_BITS+1):
            fps.append((str(i), bitops.byte_from_bitlist(bitlist, NUM_BITS)))
            bitlist.append(i)
        _everything_fps = fps
        _everything_arena = chemfp.load_fingerprints(fps, chemfp.Metadata(num_bits=NUM_BITS))
        _everything_slow_arena = _everything_arena.copy()
        _everything_slow_arena.popcount_indices = b""
    return _everything_fps, _everything_arena, _everything_slow_arena

# Code used to make "everything.fps"
## def make_everything_fps():
##     with chemfp.open_fingerprint_writer("everything.fps") as writer:
##         for id, fp in get_everything_data()[1]:
##             writer.write_fingerprint(id, fp)
## make_everything_fps()

EVERYTHING_FPS = support.fullpath("everything.fps")

def get_everything_arena():
    return get_everything_data()[1]

def get_slow_everything_arena():
    slow_arena = get_everything_data()[2]
    assert slow_arena.popcount_indices == b""
    return slow_arena

def get_both_arenas():
    return get_everything_data()[1], get_everything_data()[2]

def _get_check_bits():
    return [x for x in _raw_get_check_bits() if x <= NUM_BITS]

def _raw_get_check_bits():
    if FULL_TEST:
        #return range(arena.num_bits)
        return [0, 1, 2,
                77, 78, 79,         #   1024 / 13
                203, 204, 205,      #   1024 / 5
                253, 255, 256,      #   1024 / 4
                341, 342,           #   1024 / 3
                510, 511, 512, 513, #   1024 / 2
                682, 683,           # 2*1024 / 3
                1022, 1023,         #   1024
            ]

    else:
        return [0, 1, 2, 511, 512, 513, 1022, 1023]

interesting_thresholds = (
        0.0,
        sys.float_info.min,

        0.10373443983402489,  # 5/48.2  (1 ulp less than the next value)
        0.1037344398340249,   # 50/482  -- caused problems during initial testing
        0.10373443983402492,  # (1 ulp greater than the previous)

        0.39999999999999997,  # (1 ulp less than the next value)
        0.4,                  # 4/10
        0.4000000000000001,   # (1 ulp greater than the previous)

        0.49999999999999994,  # (1 ulp less than the next value)
        0.5,                  # 1/2
        0.5000000000000001,   # (1 ulp greater than the previous)

        0.7692307692307692,   # 1/1.3  (1 ulp less than the next value)
        0.7692307692307693,   # 10/13
        0.7692307692307694,   # (1 ulp greater than the previous)

        0.9999999999999999,   # 1 ulp less than 1.0
        1.0,
        )
assert len(set(interesting_thresholds)) == len(interesting_thresholds)

class BaseSearch(object):
    def test_empty_query(self):
        arena = self.arena
        # count
        fp = bitops.byte_from_bitlist([], NUM_BITS)
        self.assertEqual(self.count_hits_fp(fp, arena, 0.00001), 0)
        self.assertEqual(self.count_hits_fp(fp, arena, 0.00000), len(arena))
        
        # threshold
        self.assertEqual(len(self.threshold_search_fp(fp, arena, 0.00001)), 0)
        self.assertEqual(len(self.threshold_search_fp(fp, arena, 0.00000)), len(arena))

        # threshold
        self.assertEqual(len(self.knearest_search_fp(
            fp, arena, k=3, threshold=0.00001)), 0)
        self.assertEqual(len(self.knearest_search_fp(
            fp, arena, k=3, threshold=0.00000)), 3)
        self.assertEqual(len(self.knearest_search_fp(
            fp, arena, k=len(arena), threshold=0.00000)), len(arena))

        
    def test_single_bit_scan_count(self):
        arena = self.arena
        check_bits = _get_check_bits()
        
        for bitno in check_bits:
            fp = bitops.byte_from_bitlist([bitno], NUM_BITS)
            expected_scores = [(i>bitno)/(i+(i<=bitno)) for i in range(NUM_BITS+1)]
            expected_scores.sort(reverse=True)
            # Check at the threshold borders
            for threshold in sorted(set(expected_scores)):
                # Are the theshold counts correct?
                found_count = self.count_hits_fp(fp, arena, threshold)
                # We go from lowest threshold to highest, so keep reducing the list
                expected_scores = [score for score in expected_scores if score >= threshold]
                expected_count = len(expected_scores)
                self.assertEqual(found_count, expected_count, (bitno, threshold))


    def test_single_bit_threshold(self):
        arena = self.arena
        check_bits = _get_check_bits()
        
        for bitno in check_bits:
            fp = bitops.byte_from_bitlist([bitno], NUM_BITS)
            expected_scores = [(i>bitno)/(i+(i<=bitno)) for i in range(NUM_BITS+1)]
            expected_scores.sort(reverse=True)
            # Check at the threshold borders
            for threshold in sorted(set(expected_scores)):
                # We go from lowest threshold to highest, so keep reducing the list
                expected_scores = [score for score in expected_scores if score >= threshold]
        
                # Are the theshold scores correct?
                found_hits = self.threshold_search_fp(fp, arena, threshold)
                found_hits.reorder("decreasing-score")
                found_scores = list(found_hits.get_scores())
                self.assertEqual(found_scores, expected_scores, (bitno, threshold))

    def test_single_bit_knearest(self):
        arena = self.arena
        check_bits = _get_check_bits()
        
        for bitno in check_bits:
            fp = bitops.byte_from_bitlist([bitno], NUM_BITS)
            expected_scores = [(i>bitno)/(i+(i<=bitno)) for i in range(NUM_BITS+1)]
            expected_scores.sort(reverse=True)
            # Check at the threshold borders
            for threshold in sorted(set(expected_scores)):
                # We go from lowest threshold to highest, so keep reducing the list
                expected_scores = [score for score in expected_scores if score >= threshold]
                        
                ## Are the k-nearest searches correct?
                found_hits = self.knearest_search_fp(fp, arena, len(arena), threshold)
                found_scores = list(found_hits.get_scores())
                self.assertEqual(found_scores, expected_scores, (bitno, threshold))
                
                ## found_hits = search.knearest_tanimoto_search_fp(fp, arena, 5, threshold)
                ## found_scores = list(found_hits.get_scores())
                ## self.assertEqual(found_scores, expected_scores[:5], (bitno, threshold))
                ## self.assertEqual(len(found_hits), 5, (bitno, threshold))

    def test_count_arena(self):
        exact_hits = compute_exact_scaled_tversky_scores(10, 10)
        for threshold in interesting_thresholds:
            counts = self.count_hits_arena(get_one_bit_arena(), self.arena, threshold)
            expected_counts = [sum(1 for hit in hits if hit[1] >= threshold) for hits in exact_hits]
            self.assertEqual(list(counts), expected_counts, (threshold,))
        
    def test_threshold_arena(self):
        # This is the same code path as the fp x arena fingerprints
        # so I am more cursory
        arena = self.arena
        assert len(arena) == NUM_BITS+1
        query_arena = chemfp.load_fingerprints(
            [(str(bitno), bitops.byte_from_bitlist([bitno], NUM_BITS))
                   for bitno in range(NUM_BITS)], arena.metadata)
        
        all_expected_hits = []
        for bitno in range(NUM_BITS):
            expected_hits = [(str(i), (i>bitno)/(i+(i<=bitno))) for i in range(NUM_BITS+1)]
            expected_hits.sort(reverse=True, key=lambda x: x[1])
            all_expected_hits.append(expected_hits)

        for threshold in interesting_thresholds:
            all_hits = self.threshold_search_arena(
                query_arena, arena, threshold=threshold)
            all_hits.reorder_all("decreasing-score")
            for query_i, hits in enumerate(all_hits):
                expected = [x for x in all_expected_hits[query_i] if x[1] >= threshold]
                self.assertEqual(sorted(hits.get_ids_and_scores()), sorted(expected), (query_i, threshold))


                
    def test_knearest_arena(self):
        # This is the same code path as the fp x arena fingerprints
        # so I am more cursory
        arena = self.arena
        assert len(arena) == NUM_BITS+1
        query_arena = chemfp.load_fingerprints(
            [(str(bitno), bitops.byte_from_bitlist([bitno], NUM_BITS))
                for bitno in range(NUM_BITS)], arena.metadata)
        assert len(query_arena) == NUM_BITS
        
        all_expected_scores = []
        for bitno in range(NUM_BITS):
            expected_scores = [(i>bitno)/(i+(i<=bitno)) for i in range(NUM_BITS+1)]
            expected_scores.sort(reverse=True)
            all_expected_scores.append(expected_scores)

        for threshold in interesting_thresholds:

            all_hits = self.knearest_search_arena(
                query_arena, arena, k=len(arena), threshold=threshold)
            all_hits.reorder_all("decreasing-score")
            for query_i, hits in enumerate(all_hits):
                expected = [score for score in all_expected_scores[query_i] if score >= threshold]
                self.assertEqual(len(hits), len(expected), (query_i, threshold))
                self.assertEqual(list(hits.get_scores()), expected, (query_i, threshold))

            all_hits = self.knearest_search_arena(
                query_arena, arena, k=5, threshold=threshold)
            all_hits.reorder_all("decreasing-score")
            for query_i, hits in enumerate(all_hits):
                expected = [score for score in all_expected_scores[query_i] if score >= threshold]
                if len(expected) > 5:
                    expected = expected[:5]
                self.assertEqual(list(hits.get_scores()), expected, (query_i, threshold))


class Symmetric(object):
    def test_count_hits_symmetric(self):
        # At this point I trust the fp x arena search.
        # Use that to test the symmetric code
        arena = get_everything_arena()
        for threshold in interesting_thresholds:
            
            all_counts = self.count_hits_symmetric(arena, threshold)
            for query_i, (query_id, query_fp) in enumerate(arena):
                expected_count = self.count_hits_fp(query_fp, arena, threshold)
                if threshold == 0.0:
                    expected_count = len(arena)-1
                elif query_i == 0:
                    # 0/0 case
                    assert expected_count == 0, (expected_count, threshold)
                else:
                    expected_count -= 1
                
                self.assertEqual(all_counts[query_i], expected_count, (query_i, query_id, threshold, query_fp))


    def test_threshold_search_symmetric(self):
        # At this point I trust the fp x arena search.
        # Use that to test the symmetric code
        arena = get_everything_arena()
        for threshold in interesting_thresholds:
            
            all_hits = self.threshold_search_symmetric(arena, threshold)
            all_hits.reorder_all("decreasing-score")
            for query_i, (query_id, query_fp) in enumerate(arena):
                fp_hits = self.threshold_search_fp(query_fp, arena, threshold)
                fp_hits.reorder("decreasing-score")
                expected_hits = [x for x in fp_hits.get_ids_and_scores() if x[0] != query_id]
                self.assertEqual(all_hits[query_i].get_ids_and_scores(),
                                 expected_hits,
                                 (query_i, threshold))
                        
    def test_knearest_search_symmetric(self):
        # At this point I trust the fp x arena search.
        # Use that to test the k-nearest symmetric code
        arena = get_everything_arena()
        for threshold in interesting_thresholds:
            all_hits = self.knearest_search_symmetric(arena, len(arena), threshold)
            if threshold == 0.0:
                for query_i, hits in enumerate(all_hits):
                    if len(hits) != len(arena)-1:
                        print("oops", hits.get_indices_and_scores())
                    self.assertEqual(len(hits), len(arena)-1, (query_i, threshold))
                
            #print("QQQ", all_hits[0].get_indices_and_scores())
            for query_i, (query_id, query_fp) in enumerate(arena):
                fp_hits = self.knearest_search_fp(query_fp, arena, len(arena), threshold)
                expected_hits = [x for x in fp_hits.get_ids_and_scores() if x[0] != query_id]
                self.assertEqual(all_hits[query_i].get_ids_and_scores()[:10], expected_hits[:10], (query_i, query_id, threshold))
                self.assertEqual(all_hits[query_i].get_ids_and_scores(), expected_hits, (query_i, query_id, threshold))

            all_hits = self.knearest_search_symmetric(arena, 5, threshold)
            for query_i, (query_id, query_fp) in enumerate(arena):
                hits = self.knearest_search_fp(query_fp, arena, 6, threshold)
                self.assertEqual(all_hits[query_i].get_ids_and_scores(),
                                 [x for x in hits.get_ids_and_scores() if x[0] != query_id])

class SingleThreaded(object):
    def setUp(self):
        self._num_threads = chemfp.get_num_threads()
        chemfp.set_num_threads(0)
        
    def tearDown(self):
        chemfp.set_num_threads(self._num_threads)

class MultiThreaded(object):
    def setUp(self):
        self._num_threads = chemfp.get_num_threads()
        chemfp.set_num_threads(4)
        
    def tearDown(self):
        chemfp.set_num_threads(self._num_threads)
        
class UseIndexedArena(Symmetric):
    def setUp(self):
        self.arena = get_everything_arena()

class UseUnindexedArena(object):
    def setUp(self):
        self.arena = get_slow_everything_arena()

class Tanimoto(object):        
    count_hits_fp = staticmethod(search.count_tanimoto_hits_fp)
    threshold_search_fp = staticmethod(search.threshold_tanimoto_search_fp)
    knearest_search_fp = staticmethod(search.knearest_tanimoto_search_fp)
    count_hits_arena = staticmethod(search.count_tanimoto_hits_arena)
    threshold_search_arena = staticmethod(search.threshold_tanimoto_search_arena)
    knearest_search_arena = staticmethod(search.knearest_tanimoto_search_arena)
    count_hits_symmetric = staticmethod(search.count_tanimoto_hits_symmetric)
    threshold_search_symmetric = staticmethod(search.threshold_tanimoto_search_symmetric)
    knearest_search_symmetric = staticmethod(search.knearest_tanimoto_search_symmetric)

class TestTanimotoSingleThreadedIndexed(BaseSearch, Tanimoto, SingleThreaded, UseIndexedArena, unittest2.TestCase):
    def setUp(self):
        SingleThreaded.setUp(self)
        UseIndexedArena.setUp(self)
        self.assertTrue(self.arena.popcount_indices)
    
class TestTanimotoSingleThreadedUnindexed(BaseSearch, Tanimoto, SingleThreaded, UseUnindexedArena, unittest2.TestCase):
    def setUp(self):
        SingleThreaded.setUp(self)
        UseUnindexedArena.setUp(self)
        self.assertFalse(self.arena.popcount_indices)
    
class TestTanimotoMultiThreadedIndexed(BaseSearch, Tanimoto, MultiThreaded, UseIndexedArena, unittest2.TestCase):
    def setUp(self):
        MultiThreaded.setUp(self)
        UseIndexedArena.setUp(self)
        self.assertTrue(self.arena.popcount_indices)
    
class TestTanimotoMultiThreadedUnindexed(BaseSearch, Tanimoto, MultiThreaded, UseUnindexedArena, unittest2.TestCase):
    def setUp(self):
        MultiThreaded.setUp(self)
        UseUnindexedArena.setUp(self)
        self.assertFalse(self.arena.popcount_indices)
    
        

# For the Tversky NxM queries, set up a query arena with each on-bit set

_one_bit_arena = None
def get_one_bit_arena():
    global _one_bit_arena
    if _one_bit_arena is None:
        metadata = chemfp.Metadata(num_bits=NUM_BITS)
        _one_bit_arena = chemfp.load_fingerprints(
            ((str(bitno), bitops.byte_from_bitlist([bitno], NUM_BITS))
                  for bitno in range(NUM_BITS)),
            metadata)
    return _one_bit_arena

def compute_exact_scaled_tversky_scores(scaled_alpha, scaled_beta):
    queries = get_one_bit_arena()
    
    all_hits = []
    for query_bitno in range(len(queries)):
        hits = []
        for target_num_bits in range(NUM_BITS+1):
            if target_num_bits == 0:
                c = 0
            else:
                if query_bitno < target_num_bits:
                    c = 1
                else:
                    c = 0
            if c == 0:
                score = 0.0
            else:
                score = 10*c / (scaled_alpha * (1-c) + scaled_beta * (target_num_bits-c) + 10*c)
            hits.append((str(target_num_bits), score))
        all_hits.append(hits)
    return all_hits


def compute_exact_scaled_tversky_scores_symmetric(alpha, beta):
    all_hits = []
    str_ids = [str(x) for x in range(NUM_BITS+1)]
    for num_bits1 in range(NUM_BITS+1):
        hits = []
        for num_bits2 in range(num_bits1):
            A = num_bits1 - num_bits2
            B = 0
            c = num_bits2
            score = 10*c / (alpha * A + beta * B + 10*c)
            hits.append( (str_ids[num_bits2], score) )

        for num_bits2 in range(num_bits1+1, NUM_BITS+1):
            A = 0
            B = num_bits2 - num_bits1
            c = num_bits1
            score = 10*c / (alpha * A + beta * B + 10*c)
            hits.append( (str_ids[num_bits2], score) )
        #scores.sort()
        all_hits.append(hits)
    return all_hits


#### The file-based tests

class FakeArena(object):
    def __init__(self):
        arena = get_everything_arena()
        self._len = len(arena)
        self.metadata = arena.metadata
    def __len__(self):
        return self._len

class FPSTanimoto(object):
    def setUp(self):
        self.arena = FakeArena()

    @contextlib.contextmanager
    def _get_targets(self):
        reader = chemfp.open(EVERYTHING_FPS)
        try:
            yield reader
        finally:
            reader.close()
        
    def count_hits_fp(self, fp, targets, threshold):
        with self._get_targets() as targets:
            return fps_search.count_tanimoto_hits_fp(fp, targets, threshold)
        
    def threshold_search_fp(self, fp, targets, threshold):
        with self._get_targets() as targets:
            return fps_search.threshold_tanimoto_search_fp(fp, targets, threshold)

    def knearest_search_fp(self, fp, targets, k, threshold):
        with self._get_targets() as targets:
            return fps_search.knearest_tanimoto_search_fp(fp, targets, k, threshold)
    
    def count_hits_arena(self, queries, targets, threshold):
        with self._get_targets() as targets:
            return fps_search.count_tanimoto_hits_arena(queries, targets, threshold)
        
    def threshold_search_arena(self, queries, targets, threshold):
        with self._get_targets() as targets:
            return fps_search.threshold_tanimoto_search_arena(queries, targets, threshold)
        
    def knearest_search_arena(self, queries, targets, k, threshold):
        with self._get_targets() as targets:
            return fps_search.knearest_tanimoto_search_arena(queries, targets, k, threshold)
        
class TestFPSTanimotoSearch(BaseSearch, FPSTanimoto, unittest2.TestCase):
    pass


class TestArenaMemoryLeak(unittest2.TestCase):
    def test_arena_leak(self):
        arena = get_everything_arena()
        subarena = arena.copy(indices=[55, 66, 77, 88, 99])
        arena_refcount = sys.getrefcount(arena.arena)
        arena_indices_refcount = sys.getrefcount(arena.popcount_indices)
        subarena_refcount = sys.getrefcount(subarena.arena)
        subarena_indices_refcount = sys.getrefcount(subarena.popcount_indices)
        def check_counts():
            self.assertEqual(sys.getrefcount(arena.arena), arena_refcount)
            self.assertEqual(sys.getrefcount(arena.popcount_indices), arena_indices_refcount)
            self.assertEqual(sys.getrefcount(subarena.arena), subarena_refcount)
            self.assertEqual(sys.getrefcount(subarena.popcount_indices), subarena_indices_refcount)

        # Regression tests for a memory leak caught during the beta relase of v3.0.
        search.knearest_tanimoto_search_arena(arena, subarena)
        check_counts()
        search.knearest_tanimoto_search_arena(arena, subarena, k=8, threshold=0.2)
        check_counts()

        search.threshold_tanimoto_search_arena(arena, subarena)
        check_counts()
        search.threshold_tanimoto_search_arena(arena, subarena, threshold=0.4)
        check_counts()
        
        search.count_tanimoto_hits_arena(arena, subarena)
        check_counts()
        search.count_tanimoto_hits_arena(arena, subarena, threshold=0.3)
        check_counts()

        search.threshold_tanimoto_search_symmetric(arena)
        check_counts()
        search.threshold_tanimoto_search_symmetric(subarena)
        check_counts()

        search.count_tanimoto_hits_symmetric(arena)
        check_counts()
        search.count_tanimoto_hits_symmetric(subarena)
        check_counts()

        search.knearest_tanimoto_search_symmetric(arena)
        check_counts()
        search.knearest_tanimoto_search_symmetric(subarena)
        check_counts()
    
        # Found during v3.2 development
        search.contains_arena(subarena, arena)
        check_counts()
        
            
if __name__ == "__main__":
    flag = _get_flag()
    if flag in ("fast", None):
        FULL_TEST = False
    elif flag == "full":
        FULL_TEST = True
    else:
        raise AssertionError(flag)
    unittest2.main()

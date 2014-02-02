import numpy
import numbers
import math
import struct
from six.moves import zip

from .. import SetIntersectionIndexBase, SearchResults, EmptySearchResults

def _check_numpy ():
    missing = []
    for fn in ("zeros", "empty", "digitize", "resize", "concatenate", "unique", "bincount", "argsort"):
        if not getattr (numpy, fn, False):
            missing.append (fn)
    if missing:
        raise ImportError ("setix.backends.numpy: required functions not provided by installed numpy: " + ", ".join(missing))
_check_numpy ()

class SetIntersectionIndex (SetIntersectionIndexBase):
    def __init__ (self,
                  max_sets=2**32,
                  max_symbols=2**16,
                  init_bucket_size=16,
                  support_most_frequent=True,
                  support_find_similar=True):
        
        self._sets = numpy.empty (64, dtype="object")
        self._num_sets = 0
        
        self._symbols = []
        self._index = {}
        self._sets_by_sig = {}
        self._init_bs = init_bucket_size
        self._packers = {}
        self._support_most_frequent = bool (support_most_frequent)
        self._support_find_similar = bool (support_find_similar)
        
        if not isinstance (max_sets, numbers.Number):
            raise TypeError ("max_sets")
        
        if not isinstance (max_symbols, numbers.Number):
            raise TypeError ("max_symbols")
        
        if not isinstance (init_bucket_size, numbers.Number):
            raise TypeError ("init_bucket_size")
        
        if max_sets < 1 or max_sets >= 2**64:
            raise ValueError ("max_sets")
        
        if max_symbols < 1 or max_symbols >= 2**64:
            raise ValueError ("max_sets")
        
        if init_bucket_size < 4:
            raise ValueError ("init_bucket_size")
        
        set_bits = int (round (math.log (max_sets, 2)))
        symbol_bits = int (round (math.log (max_symbols, 2)))
        
        sz = (9, 17, 33, 65)
        dt = (numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64)
        sf = ("B", "H", "I", "L")
        
        x = numpy.digitize([set_bits], sz)[0]
        self._dtype_sets = dt[x]
        self._max_sets = 2 ** (sz[x]-1)
        
        x = numpy.digitize([symbol_bits], sz)[0]
        self._dtype_symbols = dt[x]
        self._max_symbols = 2 ** (sz[x]-1)
        self._struct_symbols = sf[x]
        
        if support_find_similar:
            self._set_sizes = numpy.zeros (8 * init_bucket_size, dtype=self._dtype_symbols)
        
        if support_most_frequent:
            self._symbol_counts = numpy.zeros (8 * init_bucket_size, dtype=self._dtype_sets)
    
    @property
    def symbol_count (self):
        return len (self._symbols)
    
    @property
    def set_count (self):
        return self._num_sets
    
    @property
    def symbols (self):
        return tuple (self._symbols)
    
    @property
    def payloads (self):
        for s in self._sets:
            for pl in s:
                yield pl
    
    @property
    def supports_most_frequent (self):
        return self._support_most_frequent
    
    @property
    def supports_find_similar (self):
        return self._support_find_similar
    
    @property
    def max_sets (self):
        return self._max_sets
    
    @property
    def max_symbols (self):
        return self._max_symbols
    
    def __getstate__ (self):
        state = dict (self.__dict__)
        del state["_packers"]
        return state
    
    def __setstate__ (self, state):
        self.__dict__ = state
        state["_packers"] = {}
    
    def add (self, iterable, payload=SetIntersectionIndexBase._SENTINEL):
        if payload is self._SENTINEL:
            payload = iterable
        
        max_sets = self._max_sets
        max_symbols = self._max_symbols
        init_bs = self._init_bs
        
        symbols = self._symbols
        index = self._index
        
        buckets = []  # list of per-symbol buckets this set belongs in
        sig = set()   # set of symbol ids for identifying the set
        num_syms = len (symbols)
        
        for symbol in iterable:
            bucket = index.get (symbol)
            
            if bucket is None:
                # register new symbol
                
                id = len (symbols)
                
                if id >= max_symbols:
                    raise RuntimeError ("index full: maximum number of symbols reached")
                
                bucket = index[symbol] = [id, 0, numpy.zeros (init_bs, dtype=self._dtype_sets)]
                symbols.append (symbol)
            
            buckets.append (bucket)
            sig.add (bucket[0])
        
        sig = sorted (sig)
        
        # packed signature used as a key in self._sets
        # this saves memory compared to a tuple of ints
        lsig = len (sig)
        packer = self._packers[lsig] = self._packers.get(lsig) or struct.Struct(self._struct_symbols * lsig).pack
        ssig = packer (*sig)
        
        S = self._sets_by_sig.get (ssig)
        if S is None:
            # register new set
            
            sid = self._num_sets
            if sid >= max_sets:
                raise RuntimeError ("index full: maximum number of sets reached")
            
            self._num_sets += 1
            sets = self._sets
            if sid >= sets.size:
                sets = self._sets = numpy.resize (sets, int(sid * 1.25))
            
            S = self._sets_by_sig[ssig] = []
            sets[sid] = S
            
            if self._support_find_similar:
                if self._set_sizes.size <= sid:
                    self._set_sizes = numpy.resize (self._set_sizes, int(sid * 1.25))
                self._set_sizes[sid] = len (buckets)
            
            # add set to per-symbol buckets
            for bucket in buckets:
                arr = bucket[2]
                idx = bucket[1]
                if arr.size <= idx:
                    arr = bucket[2] = numpy.resize (arr, int(idx * 1.25))
                arr[idx] = sid
                bucket[1] += 1
        
        if self._support_most_frequent:
            # update counts of symbol occurrences
            
            symbol_counts = self._symbol_counts
            
            new_syms = len (symbols)
            if new_syms > num_syms and new_syms >= symbol_counts.size:
                self._symbol_counts = symbol_counts = numpy.resize (symbol_counts, int(new_syms * 1.25))
                symbol_counts[num_syms:new_syms] = 0
            
            if len (sig) == len (buckets): #no repetitions
                symbol_counts[ numpy.array (sig, dtype=self._dtype_symbols) ] += 1
            else:
                for bucket in buckets:
                    symbol_counts[bucket[0]] += 1
        
        S.append (payload)
    
    def _find (self, iterable):
        buckets = []
        sig = set()
        occurrences = []
        L = 0
        
        for symbol in iterable:
            L += 1
            bucket = self._index.get (symbol)
            if bucket is not None:
                buckets.append (bucket)
                sig.add (bucket[0])
                if bucket[1]:
                    occurrences.append (bucket[2][0:bucket[1]])
        
        if occurrences:
            sids, indices = numpy.unique (numpy.concatenate (occurrences), return_inverse=True)
            counts = numpy.bincount (indices)
        
            return L, sids, indices, counts
        else:
            return L, [], [], []
    
    class SearchResults (SearchResults):
        def __init__ (self, sids, scores, sets):
            self._sids = sids
            self._scores = scores
            self._sets = sets
            self._sort = None
            self._list = None
            self._list_for = None
            
        def get (self, max_results=None):
            scores = self._scores
            sort = self._sort = self._sort or numpy.argsort (scores)
            
            if max_results is not None:
                sort = sort[-max_results:]
            
            sort = sort[::-1]
            r_sids = self._sids[sort]
            r_counts = scores[sort]
            
            return zip (r_counts, self._sets[r_sids])
        
        def __len__ (self):
            return self._scores.size
    
    def find (self, iterable, threshold=1, max_results=None):
        if not isinstance (threshold, numbers.Number):
            raise TypeError ("threshold")
        
        if threshold < 1 and threshold >= 0:
            raise ValueError ("threshold")
        
        L, sids, indices, counts = self._find (iterable)
        
        if threshold < 0:
            threshold = L + threshold
            if threshold < 1:
                raise ValueError ("threshold")
        
        if len (counts) == 0:
            return EmptySearchResults ()
        
        mask = counts >= threshold
        counts = counts[mask]
        sids = sids[mask]
        
        return self.SearchResults (sids, counts, self._sets)
    
    def find_similar (self, iterable, threshold=0.3):
        if not isinstance (threshold, numbers.Number):
            raise TypeError ("threshold")
        
        if threshold > 1 or not (threshold > 0):
            raise ValueError ("threshold")
        
        if not self._support_find_similar:
            raise RuntimeError ("find_similar support disabled")
        
        L, sids, indices, counts = self._find (iterable)
        
        if len (counts) == 0:
            return EmptySearchResults ()
        
        smls = counts / (self._set_sizes[sids] + (L * 1.0) - counts)
        
        mask = smls >= threshold
        smls = smls[mask]
        sids = sids[mask]
        
        return self.SearchResults (sids, smls, self._sets)
    
    def most_frequent (self, threshold=2.0/3.0, max_results=None, with_counts=False):
        if not self._support_most_frequent:
            raise RuntimeError ("most_frequent support disabled")
        
        counts = self._symbol_counts
        if self._num_sets == 0:
            return
        
        sort = numpy.argsort (counts[0:len(self._symbols)])
        limit = counts[sort[-1]] * 1.0 * threshold
        
        symbols = self._symbols
        
        if max_results:
            sort = sort[-max_results:]
        
        if with_counts:
            for x in sort[::-1]:
                count = counts[x]
                if count < limit:
                    break
                yield (symbols[x], count)
        else:
            for x in sort[::-1]:
                count = counts[x]
                if count < limit:
                    break
                yield symbols[x]

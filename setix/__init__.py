import numbers

def similarity (set1, set2):
    """
    Similarity function used.
    Input: two arbitrary python sets.
    Output: floating point measure of similarity between 0.0 and 1.0.
    """
    
    i = len (set1 & set2)
    return i * 1.0 / (len (set1) + len (set2) - i)

class SearchResults (object):
    def get (self, max_results=None):
        """
        Get an iterator for found results.
        
        Keyword arguments:
        
        max_results
            Max number of results to return.
        """
        
        raise NotImplementedError ()
    
    def get_list (self, max_results=None):
        """
        Get a list of found results. The list is cached between calls.
        
        Keyword arguments:
        
        max_results
            Max number of results to return.
        """
        
        if self._list is None\
        or (max_results is None and self._list_for is not None)\
        or (max_results is not None and self._list_for is not None and self._list_for < max_results):
            self._list = list (self.get (max_results))
            self._list_for = max_results
        
        if max_results is not None and len(self._list) > max_results:
            return self._list[0:max_results]
        
        return self._list
    
    def __iter__ (self):
        return self.get ()

class SetIntersectionIndexBase (object):
    _SENTINEL = []
    
    def __init__ (self, *args, **kwargs):
        """
        See the factory function `SetIntersectionIndex` in this module.
        """
        
        raise NotImplementedError
    
    @property
    def symbol_count (self):
        """
        Number of unique symbols added to the index.
        """
        
        raise NotImplementedError
    
    @property
    def set_count (self):
        """
        Number of unique sets indexed. The order of elements in the input iterables counted here is disregarded.
        """
        
        raise NotImplementedError
    
    @property
    def symbols (self):
        """
        An iterable containing all the unique symbols in the index.
        """
        
        raise NotImplementedError
    
    @property
    def payloads (self):
        """
        An iterator over all the payloads added to the index.
        """
        
        raise NotImplementedError
    
    @property
    def supports_most_frequent (self):
        """
        Boolean value indicating whether this index supports the .most_frequent() method.
        """
        
        raise NotImplementedError
    
    @property
    def supports_find_similar (self):
        """
        Boolean value indicating whether this index supports the .find_similar() method.
        """
        
        raise NotImplementedError
    
    @property
    def max_sets (self):
        """
        Max number of sets that can fit in this index. Note that this value may be larger than the constructor argument.
        """
        
        raise NotImplementedError
    
    @property
    def max_symbols (self):
        """
        Max number of symbols that can fit in this index. Note that this value may be larger than the constructor argument.
        """
        
        raise NotImplementedError
    
    def add (self, iterable, payload=_SENTINEL):
        """
        Index a set of symbols.
        
        Arguments:
        
        iterable
            Any iterable representing the set to be indexed. Items in the iterable need to be hashable.
            The value of the iterable is not stored (unless: see the payload argument).
        
        Keyword arguments:
        
        payload
            Any object to store alongside the set. If omitted, the iterable itself is stored.
            Payloads don't need to be hashable.
        """
        
        raise NotImplementedError
    
    def find (self, iterable, threshold=1, max_results=None):
        """
        Find sets in the index with at least `threshold` intersections with the given `iterable`.
        Returns: a SearchResults iterable returning (payload, number of intersections) tuples.
        
        If threshold is negative, the number of unique symbols in `iterable` is added to it.
        """
        
        raise NotImplementedError
    
    def find_similar (self, iterable, threshold=0.3):
        """
        Find sets in the index with at least `threshold` similarity score to the given `iterable`.
        Returns: a SearchResults iterable returning (payload, similarity) tuples.
        
        The similarity score is computed as:
                i
            ---------
            A + B - i
        where
        `i` is the number of common symbols to both sets,
        `A` and `B` are sizes of the two sets.
        
        (This scoring function was borrowed from the PostgreSQL extension pg_trgm.)
        """
        
        raise NotImplementedError
    
    def most_frequent (self, threshold=2.0/3.0, max_results=None, with_counts=False):
        """
        Find the most frequently occurring symbols in the index.
        
        Keyword arguments:
        
        threshold (default: 2/3, min: 0, max: 1)
            Frequency factor relative to the highest occuring frequency, over which symbols are returned.
            Ie. if the most frequent symbol occurred 100 times in the index and the threshold is 0.667, then symbols
            occurring 67 or more times are returned by this method.
        
        with_counts (default: False)
            If false - the result is a generator returning symbols
            If true - the result is a generator returning (symbol, count) tuples
        """
        
        raise NotImplementedError

try:
    import importlib
except ImportError:
    def import_backend (name):
        return __import__ ("setix.backends.b_" + name)
else:
    def import_backend (name):
        return importlib.import_module (".backends.b_" + name, __name__)

_BACKENDS = {}

def SetIntersectionIndex (backend="numpy",
                          max_sets=2**32,
                          max_symbols=2**16,
                          init_bucket_size=16,
                          support_most_frequent=True,
                          support_find_similar=True):
        """
        Create a new index for finding intersecting sets.
        
        Keyword arguments:
        
        backend (default: "numpy")
            Specific implementation of a set intersection index to use.
            Currently only "numpy" is supported.
        
        max_sets (default: 2**32, min: 1, max: 2**64)
            Maximum number of sets that this index should be able to handle, note that this doesn't mean unique sets,
            but rather all calls to .add().
            The implementation is free to choose a different number at least as high as the given one.
        
        max_symbols (default: 2**16, min: 1, max: 2**64)
            Maximum number of unique symbols (set items) the index should be able to handle.
            The implementation is free to choose a different number at least as high as the given one.
            Currently, max_symbols should not be greater than max_sets.
        
        init_bucket_size (default: 16, min: 4)
            Initial number of elements in arrays holding (set, symbol) mappings, when they are first allocated.
            (The arrays grow automatically.)
        
        support_most_frequent (default: True)
            Boolean indicating whether additional data allowing the determination of most frequently occurring symbols
            should be kept. Required by the .most_frequent() method.
        
        support_find_similar (default: True)
            Boolean indicating whether the size of each added set should be remembered, for calculating normalized
            similarities between sets by the .find_similar() method.
        """
        
        module = _BACKENDS[backend] = _BACKENDS.get (backend, False) or import_backend (backend)
        return module.SetIntersectionIndex (max_sets=max_sets,
                                            max_symbols=max_symbols,
                                            init_bucket_size=init_bucket_size,
                                            support_most_frequent=support_most_frequent,
                                            support_find_similar=support_find_similar)

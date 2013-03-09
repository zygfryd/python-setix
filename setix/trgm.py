import re
import six

from . import SetIntersectionIndex, similarity

__delim_pat = re.compile (r"[\W_]+", flags=re.UNICODE)
__2s = six.u ("  ")
__s = six.u (" ")
__e = six.u ("")

def get_trigrams (phrase):
    """
    A pg_trgm compatible trigram extraction routine.
    
    It treats all non-alphanumeric characters as breaks and disregards word order, count or case.
    Words are prepended with two spaces and appended with one.
    
    [!] In python 2.x be sure to pass unicode objects if phrases contain non-ASCII characters.
    
    Example:
        Input:    It's
        Words:    (  it ), (  s )
        Trigrams: (  i), ( it), (it ), (  s), ( s )
    """
    
    phrase = phrase.lower ()
    grams = set()
    for word in __delim_pat.split (phrase):
        if word:
            word = __e.join ([__2s, word, __s])
            grams.update ([word[i:i+3] for i in range(len(word)-2)])
    return grams

def phrase_similarity (phrase1, phrase2):
    return similarity (get_trigrams (phrase1), get_trigrams (phrase2))

class TrigramIndex (object):
    """
    A pg_trgm compatible trigram phrase index.
    
    See `get_trigrams` for specifics of the trigram extraction algorithm.
    
    [!] In python 2.x be sure to pass unicode objects if phrases contain non-ASCII characters.
    """
    
    _SENTINEL = []
    
    def __init__ (self, set_index=None, max_phrases=2**32, max_trigrams=2**16):
        """
        Keyword arguments:
        
        set_index (default: a numpy set index)
            A SetIntersectionBase-derived object to use as backend.
        
        max_phrases (default: 2**32, min: 1, max: 2**64)
            Max number of unique phrases that need to be supported.
            Translates to max_sets in the the default set_index.
        
        max_trigrams (default: 2**16, min: 1, max: 2**64)
            Max number of unique trigrams that need to be supported.
            Translates to max_symbols in the default set_index.
        """
        
        self.set_index = set_index or SetIntersectionIndex (max_sets=max_phrases,
                                                            max_symbols=max_trigrams)
    
    @property
    def trigram_count (self):
        """
        Number of unique trigrams added to the index.
        """
        return self.set_index.symbol_count
    
    @property
    def phrase_count (self):
        """
        Number of unique (equivalent) phrases added to the index.
        """
        return self.set_index.set_count
    
    @property
    def trigrams (self):
        """
        An iterable returning all unique trigrams in the index.
        """
        return self.set_index.symbols
    
    @property
    def payloads (self):
        """
        An iterator over all the payloads added to the index.
        """
        return self.set_index.payloads
    
    def add (self, phrase, payload=_SENTINEL):
        """
        Analogous to `SetIntersectionIndexBase.add`
        
        If given a string, it extracts trigrams from it for indexing.
        If given a different iterable, it assumes it's a set of trigrams.
        """
        
        if payload is self._SENTINEL:
            payload = phrase
        
        if isinstance (phrase, six.string_types):
            data = get_trigrams (phrase)
        else:
            data = phrase
        
        return self.set_index.add (data, payload)
    
    def find (self, phrase, threshold=1):
        """
        Analogous to `SetIntersectionIndexBase.find`
        """
        
        if isinstance (phrase, six.string_types):
            data = get_trigrams (phrase)
        else:
            data = phrase
        
        return self.set_index.find (data, threshold)
    
    def find_similar (self, phrase, threshold=0.3):
        """
        Analogous to `SetIntersectionIndexBase.find_similar`
        """
        
        if isinstance (phrase, six.string_types):
            data = get_trigrams (phrase)
        else:
            data = phrase
        
        return self.set_index.find_similar (data, threshold)
    
    def most_frequent (self, threshold=2.0/3.0, max_results=None, with_counts=False):
        """
        Analogous to `SetIntersectionIndexBase.most_frequent`
        """
        
        return self.set_index.most_frequent (threshold, max_results, with_counts)

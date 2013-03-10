=====
setix
=====

At its core setix provides a "set intersection index", an inverted index data structure designed for storing sets
of symbols and fast querying of sets intersecting the given set, with sorting based on the number of intersections
or a similarity measure.

Additionally, a wrapper for indexing strings is provided in setix.trgm, which implements a trigram index compatible
with the PostgreSQL extension pg_trgm.

Examples
========

Using a set index:

..  code-block:: python
    
    import setix
    
    ix = setix.SetIntersectionIndex ()
    ix.add ((1, 2, 3))
    ix.add ((1, 2, 4))
    ix.add ((2, 3, 4))
    
    ix.find ((1, 2), 1).get_list()
    # returns [(2, [(1, 2, 3)]),
    #          (2, [(1, 2, 4)]),
    #          (1, [(2, 3, 4)])]
    # (the order of the first two results can change as they have equal scores)

Using a trigram index:

..  code-block:: python

    import setix.trgm
    
    ix = setix.trgm.TrigramIndex ()
    ix.add ("strength")
    ix.add ("strenght")
    ix.add ("strength and honor")
    
    ix.find ("stremgth", threshold=1).get_list()
    # returns [(6, ["strength and honor"])
    #          (6, ["strength"]),
    #          (4, ["strenght"])]
    
    ix.find_similar ("stremgth", threshold=0.1).get_list()
    # returns [(0.5,  ["strength"]),           # 6 intersections / (9 total + 9 total - 6)
    #          (0.29, ["strenght"]),           # 4 intersections / (9 total + 9 total - 4)
    #          (0.27, ["strength and honor"])] # 6 intersections / (9 total + 19 total - 6)

In general, to search for phrases containing a misspelt word, a threshold of -3*N can be given where N is the number
of misspellings.

..  code-block:: python

    ix.find ("stremgth", threshold=-3).get_list()
    # returns [(6, ["strength and honor"]),
    #          (6, ["strength"])]

Benchmarks
==========

A benchmark is included in tests/dvd_db_test.py

Results from an Athlon II running at 2.6GHz:

Python 2.7
----------------------

..  code-block:: none

    In [1]: import tests.dvd_db_test
    Loading database...
    Extracted 240577 titles
    Memory used by data: 107.8MB
    Building index...
    CPU time used: 43.1s
    Unique trigrams indexed: 11352
    Unique phrases indexed: 228620
    Memory used by index: 80.9MB
    
    In [2]: %timeit list (tests.dvd_db_test.titles.find("daft punk", 8))
    10 loops, best of 3: 27.8 ms per loop
    
    In [3]: %timeit list (tests.dvd_db_test.titles.find("daft punk", 1))
    10 loops, best of 3: 86.4 ms per loop

Python 3.2
----------------------

..  code-block:: none

    In [1]: import tests.dvd_db_test
    Loading database...
    Extracted 240577 titles
    Memory used by data: 108.8MB
    Building index...
    CPU time used: 45.8s
    Unique trigrams indexed: 11352
    Unique phrases indexed: 228620
    Memory used by index: 86.2MB
    
    In [2]: %timeit list (tests.dvd_db_test.titles.find("daft punk", 8))
    10 loops, best of 3: 27.9 ms per loop
   
    In [3]: %timeit list (tests.dvd_db_test.titles.find("daft punk", 1))
    10 loops, best of 3: 86.3 ms per loop

DVD title list used in the benchmark was obtained from http://www.hometheaterinfo.com/dvdlist.htm
Thanks for making it available.

"""
Benchmark indexing a database of DVD titles.

The package `psutil` is required by this test.
"""

import zipfile
import psutil
import os
import six
import setix.trgm

this = psutil.Process (os.getpid())

title_list = []
mem1 = this.get_memory_info()

six.print_("Loading database...")

with zipfile.ZipFile (os.path.join (os.path.dirname (__file__), "dvd_csv.zip")).open ("dvd_csv.txt", "r") as f:
    for line in f.readlines():
        title_list.append (line.decode("utf8","replace").split(",")[0].strip(' "'))
six.print_("Extracted {0} titles".format (len(title_list)))

mem2 = this.get_memory_info()
six.print_("Memory used by data: {0:.1f}MB".format ((mem2.rss - mem1.rss) / 1024.0 / 1024.0))

titles = setix.trgm.TrigramIndex ()

six.print_("Building index...")
this.get_cpu_times()
mem1 = this.get_memory_info()

for title in title_list:
    titles.add (title)

mem2 = this.get_memory_info()

six.print_("CPU time used: {0:.1f}s".format (this.get_cpu_times().user))
six.print_("Unique trigrams indexed: {0}".format (titles.trigram_count))
six.print_("Unique phrases indexed: {0}".format (titles.phrase_count))
six.print_("Memory used by index: {0:.1f}MB".format ((mem2.rss - mem1.rss) / 1024.0 / 1024.0))

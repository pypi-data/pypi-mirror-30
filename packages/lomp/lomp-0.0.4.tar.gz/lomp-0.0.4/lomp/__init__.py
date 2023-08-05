import sys

if sys.version_info[0] < 3:
    from lomp import parallel_map, parallel_iterator
else:
    from lomp.lomp import parallel_map, parallel_iterator

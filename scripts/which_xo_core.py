#!/usr/bin/env python3
import xo_core, inspect, sys, os
print("xo_core from:", inspect.getsourcefile(xo_core))
print("sys.path[0:5]:")
for p in sys.path[:5]:
    print("  ", p)

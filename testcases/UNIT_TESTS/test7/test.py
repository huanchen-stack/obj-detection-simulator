"""This test focus on sequential execution on a single device."""

import os
import sys

import simulator

path = os.path.abspath(os.getcwd())
path = os.path.join(path, "testcases/UNIT_TESTS/test7/")
dep = os.path.join(path, "dep.csv")
prof = os.path.join(path, "prof.csv")
part = os.path.join(path, "part.csv")
priority = os.path.join(path, "priority.csv")

out = os.path.join(path, "out")
sys.stdout = open(out, "w")

simulator.Simulator(
    dep,
    [
        prof,
        prof,
        prof,
        prof,
        prof,
        prof,
    ],
    part_filename=part,
    # priority_filename=priority,
    # bandwidth = 200,
)
import os

path = os.path.abspath(os.getcwd())
path = os.path.join(path, "testcases/UNIT_TESTS")
unit_tests = []
for i in range(24, 25):
    unit_tests.append(os.path.join(path, f"test{i}/test.py"))

for unit_test in unit_tests:
    exec(open(unit_test).read())

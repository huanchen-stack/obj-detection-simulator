import simulator

simulator.Simulator(
    "test_dep.csv",
    [
        "test_prof.csv",
        "test_prof.csv",
        "test_prof.csv",
        "test_prof.csv",
    ],
    part_filename="test_partition.csv",
    priority_filename="test_priority.csv",
)
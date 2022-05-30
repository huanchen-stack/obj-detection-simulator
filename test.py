import simulator

simulator.Simulator(
    "test_dep.csv",
    [
        "test_prof.csv",
        "test_prof.csv",
        "test_prof.csv"
    ], 
    part_filename="test_partition1.csv",
    priority_filename="test_priority1.csv",
)
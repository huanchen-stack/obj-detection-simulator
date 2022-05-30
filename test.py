import simulator

simulator.Simulator(
    "test_dep1.csv", 
    [
        "test_prof1.csv", 
        "test_prof1.csv", 
        "test_prof1.csv"
    ], 
    part_filename="test_partition1.csv",
    priority_filename="test_priority1.csv",
)
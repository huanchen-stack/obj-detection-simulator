# obj-detection-simulator

## How to use & Attribution explanation:
###1. Test.py

```python
import simulator
simulator.Simulator(
    dep_filename="dep.csv",
    prof_filenames=[
        "prof.csv",
    ],
    bandwidth=200,
    device_names=[],
    part_filename="partition.csv",
    priority_filename="priority.csv",
)
```
###2. dep_filename
* This csv file contains the dependency relation between layers of a network. 
* It has two columns: source, destination. Every entry represents an edge in the network.
###3. prof_filenames
* This csv file contains the profiling result of every layer on a particular device.
* It has five columns: layer_name, time,cpu_mem, cuda_mem, size, MACs
###4. bandwidth
* The bandwidth of communication network between drones.
###5. device_names
* Specifies the names of drones. This attribute can be left empty, and the drones used in simulation will be named from 0 to (#drones-1).
###6. part_filename
* This csv file specifies the device on which each layer will be executed. 
* It has two columns: layer_name, device (represented by index)
###7. priority_filename
* This csv file specifies the priority of each layer. If a layer has multiple "next layers", the simulator will execute the one with the highest priority first.
* This attribute can be left empty, and the layers will have same priority (1). 
* This file has two columns: layer_name, priority. 
###8. Device setting
In device.py, the attribute "parallel" specifies whether devices can send data and execute layers at the same time. 



## Result
The simulator prints the simulation trail of the network before it outputs simulation results. 

###1. Time Result
The time needed to reach every output. 

###2. Time Result per Device
Time spent on every device. 

###3. Memory Result
Total memory consumption and peak memory usage on every device.  

###4. MACs Result
Total and peak number of operations on every device. 


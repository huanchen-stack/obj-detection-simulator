from device import Device
import pandas as pd
from layer import Layer


class Simulator(object):

    def __init__(self,
                 dep_filename,
                 prof_filenames,
                 bandwidth=200,
                 device_names=None,
                 priority_filename=None,
                 part_filename=None):
        super().__init__()
        self.bandwidth = bandwidth

        self.current_device = 0  # spin
        self.device_names = []  # spinning through all devices
        self.devices = {}  # Dictionary of Device objects: device_name -> Device object
        self.layers = {}  # Dictionary of Layer objects: layername -> Layer objects
        self.priorities = {}  # Dictionary of integers: layername -> integer
        self.cut_points = {}

        self.time_result = {}
        self.mem_result = {}

        self.stack = []  # for DFS
        self.waiting_queue = []  # for DFS: when layer cannot be explored due to
        #      dependencies are not fulfilled
        #      need to change device

        # load and initialize devices
        if device_names is None:
            # TODO: should #device determined by prof?
            self.device_names = [str(i) for i in range(len(prof_filenames))]
        for name, prof_filename in zip(self.device_names, prof_filenames):
            self.devices[name] = Device(name, prof_filename)

        # load dependencies and initialize all Layers
        self.load_dependencies(dep_filename)

        # if priority file is not given, init with even priorities
        if priority_filename is not None:
            self.load_priorities(priority_filename)
        else:
            for name in list(self.layers.keys()):
                self.priorities[name] = 1

        self.load_partitions(part_filename)  # Intermediate result of partition, now load from handcoded csv
        # self.partition(part_filename)

        print(self.device_names)
        for device in list(self.devices.values()):
            # TODO: Now exec has not much to do with assigned layers
            print(f"Device name: {device.name}, with layers: {device.assigned_layer}")
        print("{:<15} {:<15}".format("layer", "device"))
        for layer in list(self.layers.values()):
            print("{:<15} {:<15}".format(layer.name, layer.device_id))
        print(f"Layer priority: {self.priorities}")

        self.simulate()

    def load_dependencies(self, dep_filename):
        """
        Dependencies file has the following format for each line:
            source, destination, size (temporarily remove shape)
        Use source layer name as the name of the data
        Update Layer's dependencies and next lists
        """
        df_list = pd.read_csv(dep_filename).values.tolist()
        for entry in df_list:
            src = entry[0]
            dst = entry[1]
            size = entry[2]
            if src not in self.layers.keys():
                self.layers[src] = Layer(src)
            if dst not in self.layers.keys():
                self.layers[dst] = Layer(dst)
            self.layers[src].next.append(dst)
            self.layers[dst].dependencies.append(src)
            # TODO: Here size is with layers. If necessary, can be with dependencies.
            self.layers[src].size = size

    def load_priorities(self, priority_filename):
        priorities = pd.read_csv(priority_filename).values.tolist()
        for layername, priority in priorities:
            self.priorities[layername] = priority

    def load_partitions(self, part_filename):
        partitions = pd.read_csv(part_filename).values.tolist()
        for layername, device_id in partitions:
            self.layers[layername].device_id = str(device_id)
            self.devices[str(device_id)].assigned_layer.append(layername)

    def go_through_path(self, layer_name, device_idx):
        # TODO: Perhaps only keep one of the following two lines
        if self.layers[layer_name].device_id is None:
            # if not assigned yet (see case 02)
            self.layers[layer_name].device_id = self.device_names[device_idx]
            self.devices[self.device_names[device_idx]].assigned_layer.append(layer_name)
        if layer_name == "output":
            return
        elif layer_name in self.cut_points.keys():
            for next_layer_name in self.cut_points[layer_name]:
                self.go_through_path(next_layer_name, device_idx + 1)
                device_idx += 1
            # go on with other next layers
            for next_layer_name in self.layers[layer_name].next:
                if next_layer_name not in self.cut_points[layer_name]:
                    self.go_through_path(next_layer_name, device_idx)
        else:
            for next_layer_name in self.layers[layer_name].next:
                self.go_through_path(next_layer_name, device_idx)

    def partition(self, part_filename):
        """
        Partition this graph. Assign every layer to a specific device.
        Assuming cut points are specified by two vertices.
        """
        if part_filename is None:
            # end to end on one device
            for key, value in self.layers.items():
                value.device_id = self.device_names[0]
        else:
            part_list = pd.read_csv(part_filename).values.tolist()
            for entry in part_list:
                if entry[0] not in self.cut_points.keys():
                    self.cut_points[entry[0]] = []
                self.cut_points[entry[0]].append(entry[1])
            self.go_through_path("input", 0)

    def device_exec(self, device_id, start_time, start_layer_name):
        """
        Update device current time.
        Returns the next layers.
        """
        device = self.devices[device_id]
        device.cur_time = start_time
        if start_layer_name not in device.assigned_layer:
            exit(1)
        else:
            print("")
            print(f"Device {device.name} is running: {start_layer_name}, starting at time {device.cur_time}")
            cur_layer = self.layers[start_layer_name]
            for dep in cur_layer.dependencies:
                if not self.layers[dep].completed:
                    cur_layer.arrival_time_pool.append(device.cur_time)
                    # cease exec
                    print(f"Dependencies not satisfied. Ceasing at {device.cur_time} on device {device.name}")
                    return
            if len(cur_layer.arrival_time_pool) > 0:
                cur_layer.arrival_time_pool.append(device.cur_time)
                device.cur_time = max(cur_layer.arrival_time_pool)
                print(f"Dependencies now satisfied. Arrival time pool: {cur_layer.arrival_time_pool}")
                print(f"Resuming at {device.cur_time} on device {device.name}")

            device.cur_time += device.time[start_layer_name]
            cur_layer.completed = True
            print(f"Finishing at time {device.cur_time}")

            print(f"Next layers: {cur_layer.next}")
            cur_layer.next = sorted(cur_layer.next, key=lambda e: self.priorities[e], reverse=True)
            print(f"Sorted next layers: {cur_layer.next}")

            for next_layer_name in cur_layer.next:
                if next_layer_name == "output":
                    self.time_result[start_layer_name] = device.cur_time
                    device.assigned_layer.pop()
                    continue
                if self.layers[next_layer_name].device_id != device_id:
                    transfer_latency = self.bandwidth
                    # transfer_latency = cur_layer.size / self.bandwidth

                    print(f"Sending data to device {self.layers[next_layer_name].device_id}, latency {transfer_latency}")

                    # change device
                    # for tail recursion
                    if not device.parallel:
                        device.cur_time += transfer_latency
                        self.device_exec(self.layers[next_layer_name].device_id,
                                         device.cur_time,
                                         next_layer_name)
                    else:
                        self.device_exec(self.layers[next_layer_name].device_id,
                                         device.cur_time + transfer_latency,
                                         next_layer_name)
                    # if not device.parallel:
                    #     device.cur_time += transfer_latency
                else:
                    self.device_exec(device.name, device.cur_time, next_layer_name)

    def simulate(self):
        # start with device idx == 0
        # self.device_exec("0", 0, "layer1")
        # self.device_exec("1", 0, "layer4")

        self.device_exec("0", 0, "input")

        print("\n=========Time Result=========")
        print("{:<15} {:<15}".format("output_layer", "time"))
        for key, value in self.time_result.items():
            print("{:<15} {:<15}".format(key, value))
        print("\n=========Mem Result=========")
        print("{:<15} {:<15} {:<15} {:<15} {:<15}".format("device", "cpu sum", "cpu peak", "cuda sum", "cuda peak"))
        for name, device in self.devices.items():
            device.get_mem_consumption()

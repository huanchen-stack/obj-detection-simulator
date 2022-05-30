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

        self.stack = []  # for DFS
        self.waiting_queue = []  # for DFS: when layer cannot be explored due to
        #      dependencies are not fulfilled
        #      need to change device

        # load and initialize devices
        if device_names is None:
            # TODO: device 数量并不是用prof来决定
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
        a = 1  # check status for testing

        print(self.device_names)
        for device in list(self.devices.values()):
            print(device.name)
            print(device.assigned_layer)
        for layer in list(self.layers.values()):
            print(layer.name, layer.device_id)
            # print(layer.next)
            # print(layer.dependencies)
        print(self.priorities)

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
            self.devices[self.device_names[device_idx]].append(layer_name)
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

    def device_exec(self, device_id, start_time):
        """
        Update device current time.
        Returns the next layers.
        """
        time_sum = 0
        device = self.devices[device_id]
        print("running")
        print(device.assigned_layer)
        for layer_name in device.assigned_layer:

            print(device.assigned_layer)
            print("exploring layer: ", layer_name)

            cur_layer = self.layers[layer_name]
            for dep in cur_layer.dependencies:
                if not self.layers[dep].completed:
                    # cease exec
                    return
            time_sum += device.time[layer_name]
            cur_layer.completed = True
            
            print("cur_layer:", cur_layer.name)
            # device.assigned_layer.remove(layer_name)

            # TODO: next priority

            print(cur_layer.next)
            cur_layer.next = sorted(cur_layer.next, key=lambda e:self.priorities[e], reverse=True)
            print(cur_layer.next)

            for next_layer_name in cur_layer.next:
                if next_layer_name == "output":
                    print("{:<15} {:<15}".format(layer_name, start_time + time_sum))
                    device.assigned_layer.pop()
                    continue
                if self.layers[next_layer_name].device_id != device_id:
                    # TODO: is_parallel
                    transfer_latency = self.bandwidth * self.layers[layer_name].size
                    # change device
                    self.device_exec(self.layers[next_layer_name].device_id, start_time + time_sum + transfer_latency)

    def simulate(self):
        """
        Similar to BFS, use self.stack to explore.
        Check if the stack and waiting queue are both empty.
        If a layer cannot be explored due to dependency or change of device,
            put layername in waiting queue.
        When stack is empty, check the waiting queue:
            while the length of waiting queue still changes:
                (otherwise we must change device),
                pop out all layers that can be explored (by then),
                sort them in ascending order of priorities,
                add to the back of self.stack.
            change device:
                add current device idx,
                send data to the current device (check if cached already)
        """
        print("{:<15} {:<15}".format("layer_name", "final time"))
        # start with device idx == 0
        self.device_exec(self.device_names[0], 0)

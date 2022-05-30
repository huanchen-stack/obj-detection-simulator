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
        self.cut_points={}

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

        self.partition(part_filename)
        a = 1  # check status for testing

        self.simulate()

    def load_dependencies(self, dep_filename):
        """
        Dependencies file has the following format for each line:
            source, destination (temporarily remove shape and size)
        Use source layer name as the name of the data
        Update Layer's dependencies and next lists
        """
        df_list = pd.read_csv(dep_filename).values.tolist()  # a 4d list of the above info (TODO: untested)
        for entry in df_list:
            src = entry[0]
            dst = entry[1]
            if src not in self.layers.keys():
                self.layers[src] = Layer(src)
            if dst not in self.layers.keys():
                self.layers[dst] = Layer(dst)
            self.layers[src].next.append(dst)
            self.layers[dst].dependencies.append(src)

    def go_through_path(self, layer_name, device_idx):
        self.layers[layer_name].device_id = self.device_names[device_idx]
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
        (for now, use a global var as the name of file that stores partition info)
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
        pass

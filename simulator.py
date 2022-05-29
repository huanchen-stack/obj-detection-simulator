
from device import Device
from layer import Layer

class Simulator(object):
    
    def __init__(self, dep_filename, prof_filenames, bandwidth=200, device_names=None, priority_filename=None):
        super().__init__()
        self.bandwidth = bandwidth

        self.current_device = 0  # spin
        self.device_names = []  # spinning through all devices
        self.devices = {}  # Dictionary of Device objects: device_name -> Device object
        self.layers = {}  # Dictionary of Layer objects: layername -> Layer objects
        self.priorities = {}  # Dictionary of integers: layername -> integer

        self.stack = []  # for DFS
        self.waiting_queue = []  # for DFS: when layer cannot be explored due to
                                 #      dependencies are not fulfilled
                                 #      need to change device

        # load and initialize devices
        if device_names is None:
            device_names = [str(i) for i in range(len(prof_filenames))]
        for name, prof_filename in zip(device_names, prof_filenames):
            self.devices[name] = Device(name, prof_filename)

        # load dependencies and initialize all Layers
        self.load_dependencies(dep_filename)

        # if priority file is not given, init with even priorities
        if priority_filename is None:
            self.load_priorities(priority_filename)
        else:
            for name in list(self.layers.keys()):
                self.priorities[name] = 1

        self.partition()

    def load_dependencies(self, dep_filename):
        """
        Dependencies file has the following format for each line:
            source, destination, tensorshape, tensorsize\n
        Use source layer name as the name of the data
        Update Layer's dependencies and next lists
        """
        pass

    def partition(self):
        """
        Partition this graph. Assign every layer to a specific device.
        (for now, use a global var as the name of file that stores partition info)
        """
        pass

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

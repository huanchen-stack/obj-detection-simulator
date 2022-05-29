class Device(object):

    def __init__(self, name, prof_filename):
        super().__init__()
        self.name = name
        self.profile = {}  # Dictionary of Dictionary: layername -> two/three entries
        self.time = {}  # Dictionary of Time: layername -> time
        self.cache = set()  # Set of cached data
        self.cur_time = None

        self.load_profile(prof_filename)

    def load_profile(self, prof_filename):
        """
        Profiling file has the following format for each line:
            layername, time, cpu_mem\n
            or layername, time, cpu_mem, cuda_mem\n
        """
        pass

import pandas as pd

class Device(object):

    def __init__(self, name, prof_filename, parallel=True):
        super().__init__()
        self.name = name
        self.parallel = parallel
        self.profile = {}  # Dictionary of Dictionary: layername -> two/three entries
        self.time = {}  # Dictionary of Time: layername -> time
        self.cache = set()  # Set of cached data
        self.cur_time = None

        self.assigned_layer = []

        self.load_profile(prof_filename)

    def load_profile(self, prof_filename):
        """
        Profiling file has the following format for each line:
            layername, time, cpu_mem\n
            or layername, time, cpu_mem, cuda_mem\n
        """
        prof_df_list = pd.read_csv(prof_filename).values.tolist()
        for entry in prof_df_list:
            if entry[0] not in self.time.keys():
                self.time[entry[0]] = 0.0
            self.time[entry[0]] = entry[1]

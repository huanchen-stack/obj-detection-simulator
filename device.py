import pandas as pd
from layer import Layer

class Device(object):

    def __init__(self, name, prof_filename, parallel=True):
        super().__init__()
        self.name = name
        self.parallel = parallel
        self.profile = {}  # Dictionary of Dictionary: layername -> two/three entries
        self.time = {}  # Dictionary of Time: layername -> time
        self.cpu_mem = {}  # Dictionary of Mem (cpu)
        self.cuda_mem = {}
        self.cache = set()  # Set of cached data
        self.cur_time = None

        self.assigned_layer = []

        self.load_profile(prof_filename)

    def load_profile(self, prof_filename):
        """
        Profiling file has the following format for each line:
            or layername, time, cpu_mem, cuda_mem\n
        """
        prof_df_list = pd.read_csv(prof_filename).values.tolist()
        for layername, time, cpu_mem, cuda_mem in prof_df_list:
            self.time[layername] = time
            self.cpu_mem[layername] = cpu_mem
            self.cuda_mem[layername] = cuda_mem

    def get_mem_consumption(self):
        cpu_peak, cpu_sum = 0.0, 0.0
        cuda_peak, cuda_sum = 0.0, 0.0
        for layername in self.assigned_layer:
            cpu_sum += self.cpu_mem[layername]
            cuda_sum += self.cuda_mem[layername]
            cpu_peak = cpu_peak if self.cpu_mem[layername] < cpu_peak else self.cpu_mem[layername]
            cuda_peak = cuda_peak if self.cuda_mem[layername] < cuda_peak else self.cuda_mem[layername]

        print("{:<15} {:<15} {:<15} {:<15} {:<15}".format(self.name, cpu_sum, cpu_peak, cuda_sum, cuda_peak))
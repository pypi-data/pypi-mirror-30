import os.path
import logging

class ClassCfg():

    def __init__(self):
        self._home = os.path.expanduser('~')
        self.dataset = None
        self.batch_size = None  #dict:{'train': , 'val':}
        self.csv = None

        #OptimArgs
        self.GPUIDS = None
        self.MaxEpoch = None
        self.Optim = None

        self._home = os.path.expanduser('~')
        self.dataset = None
        self.batch_size = None  # dict:{'train': , 'val':}
        self.csv = None

        # OptimArgs
        self.GPUIDS = None
        self.MaxEpoch = None
        self.Optim = None

        # CommonArgs
        self.Criterion = None
        self.LogFileLoggerLevel = logging.DEBUG
        self.ConsoleLoggerLevel = logging.INFO

        # DataLoader
        self.num_workers = 8
        self.shuffle = True

        #CommonArgs
        self.Criterion = None
        self.LogFileLoggerLevel = logging.DEBUG
        self.ConsoleLoggerLevel = logging.INFO

        #DataLoader
        self.num_workers = 8
        self.shuffle = True

cfg = ClassCfg()

from . import config
from . import utils

class ConfigManager(object):
    """
    Input:
        file_type: Class,Txt,Edict
        cfg_type: net, para
    """
    def __init__(self, cfg_file, cfg_type, file_type):
        config_cls_name = file_type + 'Config'
        self.cfg = config.read_cfg_file(cfg_file, cfg_type, file_type)




class NetConfigManager(ConfigManager):

    def __init__(self, cfg_file, cfg_type, file_type):
        super(NetConfigManager, self).__init__(cfg_file, cfg_type, file_type)
        self.net = utils.build(self.cfg.model_def)




para_cfg = None
net_cfg = None
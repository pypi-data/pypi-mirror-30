import importlib
import configparser
from easydict import EasyDict as edict

_CFG_SUFFIX = ['.cfg']


def _convert_fr_class_to_edict(cfg):
    return edict(cfg.__dict__)


def read_cfg_file(cfg_file, cfg_type, file_type):
    #covert all modes to edict
    if cfg_file.endswith('.py'):
        # delete suffix .py, imitate import path
        module_path = 'config.{}cfgs.{1}'.format(cfg_type, cfg_file[:-3])
        # import module
        module_obj = importlib.import_module(module_path)
        config = module_obj.cfg

        if file_type is 'Class':
            config = _convert_fr_class_to_edict(config)

    # elif cfg_file.endswith(_CFG_SUFFIX):
        #_config = configparser.ConfigParser('.paracfgs'+cfg_file)
    else:
        raise NotImplementedError

    return config

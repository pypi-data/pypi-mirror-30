from src.config import config_manager


# Caution: Don't import spec file directly

def init_cfg():
    config_manager.para_cfg = None



if __name__ == '__main__':
    # TODO ArgParser
    init_cfg()
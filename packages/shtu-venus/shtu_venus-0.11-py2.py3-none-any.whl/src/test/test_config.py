import sys
sys.path.append('../')

from src.config import ConfigManager


class TestConfig(object):

    def test_edict_config(self):

        #test if configFactory work correctly
        #test edict
        #Caution: Don't ignore the file suffix such as .py .cfg


        cfg_mgr = ConfigManager('edict_example.py', mode='EDict')
        cfg = cfg_mgr.cfg

        #test write and read
        cfg['name'] = 'Hello'
        _name1 = cfg['name']
        assert _name1 is 'Hello'

        cfg.name = 'VeNus'
        _name2 = cfg.name
        assert _name2 is 'VeNus'

    def test_class_config(self):

        cfg_mgr = ConfigManager('class_example.py', mode='Class')
        cfg = cfg_mgr.cfg

        #test write and read
        cfg['name'] = 'Hello'
        _name1 = cfg['name']
        assert _name1 is 'Hello'

        cfg.name = 'VeNus'
        _name2 = cfg.name
        assert _name2 is 'VeNus'

if __name__ == '__main__':
    TestConfig().test_edict_config()
    TestConfig().test_class_config()
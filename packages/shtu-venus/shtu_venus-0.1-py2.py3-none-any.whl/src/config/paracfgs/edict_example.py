from easydict import EasyDict as edict

cfg = edict()

cfg.name = 'xxx_config'

# training

# validation

# dataloader

# section optimizer
cfg.optim = {}
opt = cfg.optim
opt.optim_type  = 'Adam'
opt.optim_paras = {
                'lr': 3e-3,
                'weight_decay': 0,
                }


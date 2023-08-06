from easydict import EasyDict as edict

from .basic_modules_spec import *
from ..config_manager import para_cfg

cfg = edict()

cfg.ResBlock = lambda _inCh, _outCh, kernel, _pad, _leak=0.1 :{
    "name":"ResBlock",
    "modules":[
        Conv2d(_inCh, _outCh, kernel, _Padding=_pad),
        BatchNorm2d(_outCh),
        LeakyReLU(_leak),
    ],
}

cfg.ShortCut = lambda _inCh, _outCh, kernel:{
    "name":"Shortcut",
    "modules":[
        Conv2d(_inCh, _outCh, kernel),
    ]
}

cfg.ResLayer = lambda _inCh, _outCh:{
    "name":"ResLayer",
    "modules":[
        cfg.ResBlock(_inCh, _outCh, 3, 1),
        cfg.ResBlock(_outCh, _outCh, 3, 1),
        cfg.ResBlock(_outCh, _outCh, 3, 1),
    ],
    "parameters": {
        "hasShortcut": True,
        "shortcut": cfg.ShortCut(_inCh, _outCh, 1),
    },
    "base": "EmbeddingNet",
}

cfg.miniImgNetEmdFc1={
    "name":"EmbeddingFc1",
    "modules":[
        Dropout2d(0.5),
        Conv2d(256, 2048, 1),
        AvgPool2d(6),
        ReLU(),
    ]
}

cfg.miniImgNetEmdFc2={
    "name":"EmbeddingFc2",
    "modules":[
        Dropout2d(0.5),
        Conv2d(2048, 512, 1),
        BatchNorm2d(512),
    ]
}

# Mid Level

cfg.embedding_net = {
    "name": "EmbeddingNet",
    "modules": [
        cfg.ResLayer(3, 64),
        MaxPool2d(2),
        cfg.ResLayer(64, 96),
        MaxPool2d(2),
        cfg.ResLayer(96, 128),
        MaxPool2d(2),
        cfg.ResLayer(128, 256),
        cfg.miniImgNetEmdFc1,
        cfg.miniImgNetEmdFc2,
    ]
}


C_a0 = 512+para_cfg.Nway
C_t1 = C_a0 + 32
C_a1 = C_t1 + 128*4
C_t2 = C_a1 + 128
C_a2 = C_t2 + 128*4
C_lr = C_a2 + 256
cfg.tc_net = {
    "name": "TCNet",
    "modules":[
        AttentionBlock(C_a0, dim_k=64, dim_v=32),
        TCMLBlock(C_t1, growth_rate=128),
        AttentionBlock(C_a1, dim_k=256, dim_v=128),
        TCMLBlock(C_t2, growth_rate=128),
        AttentionBlock(C_a2, dim_k=512, dim_v=256, drop_train_example=True),
        Linear(C_lr, para_cfg.Nway)
    ]
}

# Top Level

cfg.model_def = {
            "name": "MetaTCML",
            "modules":{
                'embedding_net': cfg.embedding_net,
                'tc_net': cfg.tc_net,
            }
        }


# Module Def
Linear = lambda in_ch, out_ch, bias=True:{
    'name': 'Linear',
    'parameters':{
        'in_features': in_ch,
        'out_features': out_ch,
    }
}

Conv2d = lambda _inCh, _outCh, _Kernel, _Stride=1, _Dilation=1, _Padding=0:{
    "name": "Conv2d",
    "parameters":{
         'in_channels': _inCh,
         'out_channels': _outCh,
         'kernel_size': _Kernel,
         'stride': _Stride,
         'dilation': _Dilation,
         'padding': _Padding,
    }
}

BatchNorm2d= lambda outCh:{
    "name": "BatchNorm2d",
    "parameters":{
        'num_features': outCh,
    }
}

LeakyReLU= lambda leak=0.1:{
    "name": "LeakyReLU",
    "parameters":{
        'negative_slope': leak,
    }
}

AvgPool2d= lambda kernel:{
    "name": "AvgPool2d",
    "parameters":{
        'kernel_size': kernel,
    }
}

MaxPool2d= lambda kernel:{
    "name": "MaxPool2d",
    "parameters":{
        'kernel_size': kernel,
    }
}

ReLU = lambda :{
    "name": "ReLU",
    "parameters":{
    }
}

Dropout2d = lambda p=0.5:{
    "name": "Dropout",
    "parameters":{
    'p': p,
    }
}

AttentionBlock = lambda C, dim_k, dim_v, \
                        dtype, drop_train_example=False:{
    "name": "AttentionBlock",
    "parameters":{
        'C': C,
        'dim_k': dim_k,
        'dim_v': dim_v,
        'dtype': dtype,
        'drop_train_example': drop_train_example,
    },
    "base": "attention",
}

TCMLBlock = lambda C, growth_rate, drop_train_example=False:{
    "name": "TCMLBlock",
    "parameters":{
        'C': C,
        'growth_rate': growth_rate,
        'drop_train_example': drop_train_example,
    },
    "base": "tcblock",
}
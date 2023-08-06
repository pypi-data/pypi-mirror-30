from torch import nn

net = {}

def build(spec):
    """
    Build model
    :param spec:specification
    :return: modules
    """
    # print(spec['name'])
    assert isinstance(spec, dict), "Specification must be a dictionary."

    # create module according to specification
    module_name = spec["name"]

    if ('modules' not in spec) or ('base' in spec):
        if 'base' in spec:
            # Note: the modules implemented by ourselves
            base = net[spec['base']]
        else:
            # Note: basic modules which are implemented in torch
            base = nn
        if 'modules' not in spec:
            spec = spec['parameters']
        module = getattr(base, module_name)(**spec)

    elif isinstance(spec['modules'], list):
        submodule_specs = spec["modules"]
        submodule_list = [build(submodule_spec) for submodule_spec in submodule_specs]
        module = nn.Sequential(*submodule_list)

    elif isinstance(spec['modules'], dict):
        module = {submodule_name: build(submodule_spec)
            for submodule_name, submodule_spec in spec['modules'].items()}

    else:
        raise ValueError("Format wrong.")

    return module
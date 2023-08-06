class ModelToolBase(object):
    regis_hook = {
        'pre_forward': register_pre_forward_hook,
        'forward': register_forward_hook,
        'backward': register_backward_hook,
    }

    def __init__(self, model):
        self.model = model

    def insert_pdb_layer(self, layer_index, debugger_type='pdb', where='pre_forward'):
        """Insert (i)pdb into some layer (in/out)
        :param layer_index:
        :param debugger: ['pdb', 'ipdb']
        :param where: ['pre_forward', 'forward']
        :return:
        """
        try:
            layer = self.get_layer(layer_index)
            self.regis_hook[where](layer, self.debugger(debugger_type))
        except ValueError:
            raise ValueError("where arg in pdb_layer method should be pre or after.")

    def get_layer(self, layer_index):
        #Caution: Depends on pytorch
        layers_index = layer_index.split('.')
        model = self.model
        ind_path = ''
        for ind in layers_index:
            # if ind.isdigit():
            #     ind = int(ind)
            try:
                model = model._modules[ind]
            except KeyError as e:
                print('\n', repr(e), 'Current model is {},index should be in :'.format(ind_path))
                print('\t\n'.join(model.state_dict().keys()))
                import pdb
                pdb.set_trace()
            finally:
                ind_path = ind_path + '.' + ind
        layer = model
        return layer

    def get_para(self, layer_index, para_name):
        # Caution: Depends on pytorch

        layer = self.get_layer(layer_index)
        try:
            para = layer._parameters[para_name]

        except KeyError as e:
            print(repr(e))
            print('Hint:')
            print("\t layer: ")
            print("\t\tClass Info: ", layer.__class__)
            print("\t\tLayer Index: ", layer_index)
            print("\t para: ", list(layer._parameters.keys()))
            import pdb;
            pdb.set_trace()

        return para

    def register_para_gradient_hook(self, layer_index, para_name):
        para = self.get_layer(layer_index, para_name)
        para.register_hook(lambda grad: grad)

    @staticmethod
    def register_var_gradient_hook(var):
        pass

    @staticmethod
    def register_pre_forward_hook(mod, hook):
        mod.register_forward_pre_hook(hook)

    @staticmethod
    def register_forward_hook(mod, hook):
        mod.register_forward_hook(hook)

    @staticmethod
    def register_backward_hook(mod, hook):
        mod.register_backward_hook(hook)

    @staticmethod
    def debugger(debugger_type):
        def debug(*args):
            if debugger_type == 'pdb':
                import pdb
                pdb.set_trace()
            elif debugger_type == 'ipdb':
                import ipdb
                ipdb.set_trace()
        return debug

    @staticmethod
    def list_sub_paras(layer):
        print("\n".join(layer.state_dict().keys()))

    @staticmethod
    def list_sub_modules(layer):
        for l in layer.named_modules():
            print(l)
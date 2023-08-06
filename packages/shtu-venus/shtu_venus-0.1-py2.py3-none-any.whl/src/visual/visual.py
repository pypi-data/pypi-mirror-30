"""Visual Utilities
Problems:
TODO:
Visual Design:
    Consider that people may want to customize their own plot, I recommend that create a plotter class that combines these plotter provided by the lib.

"""

import matplotlib

# TODO: support register plot, like the genetic algorithm lib we used last sememster
# TODO: Now some functions like weight_ratio don't support Multiple GPU situation.
from src.base import ModelToolBase

matplotlib.use('Agg')
import visdom
from tensorboardX import SummaryWriter
import torch

from torchnet.logger import VisdomPlotLogger

# Temporarily, don't consider multiple progress situation
# And in the current design, the Visual Class is designed for the oneshot situation

buffer = []


def hook_pre_forward(module, input):
    # only records input
    module.in_ = input


def hook_forward(module, input, output):
    # records input and output
    # if isinstance(module, nn.Linear):
    #     import pdb;pdb.set_trace()
    # if not hasattr(module, 'out_'):
    module.out_ = output.data
    # else:
    # module.out_ = torch.cat([module.out_, output.data])
    # module.in_ = input


######## Plotter ##########

# TODO: Do we need a plotter manager

class BasePlotter(ModelToolBase):
    vis_func = {'Norm':None, 'WeightRatio':None, 'MeanStd':None}

    #TODO: Visualize feature map

    def __init__(self, model):
        super(ModelToolBase).__init__(model)
        self.plotters = []

    def update_plot(self):
        for ele in self.plotters:
            ele.plot()

    def regis_plot(self, plotter, kwargs):
        assert type(kwargs) is dict
        self.plotters.append(plotter(**kwargs))



class Matplotter(ModelToolBase):
    def __init__(self, model):
        super(Matplotter, self).__init__(model)


class VisdomPlotter(BasePlotter):
    vis_funcs = {'WeightRatio': WeightRatioTB, 'Norm': NormTB, 'MeanStd': MeanStdTB}

    def __init__(self, model, env, port=8097):
        super(VisdomPlotter, self).__init__(model)
        self.env = env
        self.port = port
        self.viz = visdom.Visdom(env=env, port=port)

    def text(self, msg):
        self.viz.text(msg, self.env, opts={'title': 'Message'})


    # def register_vis_featuremap(self, layer_index, where='record_forward'):
    #     """
    #     :param layer_index:
    #     :param where: pre_forward, forward
    #     """
    #     mapping = {
    #         'record_forward': 'forward_out',
    #         'record_forward_in': 'forward_in',
    #     }
    #     layer = self.get_layer(layer_index)
    #     hook = self.hooks[where]
    #     regis_idx = mapping[where]
    #     self.regis_hook[regis_idx](layer, hook)


    # def vis_featuremap(self, layer_index, ch=None, wheres=('forward_out', 'forward_in')):
    #     mapping = {
    #         'forward_out': 'out_',
    #         'forward_in': 'in_',
    #     }
    #
    #     wheres = tuple(wheres)
    #     layer = self.get_layer(layer_index)
    #
    #     fmaps = []
    #     for where in wheres:
    #         fmap = getattr(layer, mapping[where])
    #         if isinstance(fmap, tuple):
    #             assert len(fmap) == 1
    #             fmap = fmap[0]
    #         *__, H, W = tuple(fmap.shape)
    #         fmap = fmap.view(-1, H, W).cpu()
    #         fmap = np.asarray(fmap.data)
    #         fmap /= 2 * np.amax(fmap)
    #         fmap += 0.5
    #         fmaps.append(fmap[0:1])
    #     # import pdb;pdb.set_trace()
    #     title = str(layer_index) + '_feature_map'
    #     # viz = VisdomLogger('images', env=self.env,opts={'title':title, 'caption':"\t".join(wheres)})
    #     self.viz.images(fmaps)
    #     # viz.log(fmaps,
    #     #         # padding=2,
    #     #         nrow=len(fmaps),
    #     #         # env=self.env,
    #     #
    def regis_weight_ratio_plot(self, layer_index, para_name, logger_name='', caption=''):
        """
        :param layer_index:
        :param para_name:
        :param logger_name:
        :param caption:
        """
        para = self.get_para(layer_index, para_name)
        kwargs = {
            'para': para,
            'env': self.env,
            'logger_name': layer_index + '_' + para_name + '_weightratio' if logger_name == '' else logger_name,
            'caption': caption,
        }
        self.regis_plot(plotter=self.vis_funcs['WeightRatio'], kwargs=kwargs)

    def regis_norm_plot(self, layer_index, para_name, logger_name='', caption=''):
        """
        :param layer_index:
        :param para_name:
        :param env:
        :param logger_name:
        :param caption:
        """
        para = self.get_para(layer_index, para_name)
        kwargs = {
            'para': para,
            'env': self.env,
            'logger_name': layer_index + '_' + para_name + '_norm' if logger_name == '' else logger_name,
            'caption': caption,
        }
        self.regis_plot(plotter=self.vis_funcs['Norm'], kwargs=kwargs)


    def regis_mean_std(self, layer_index, logger_name='', caption=''):
        layer = self.get_layer(layer_index)
        kwargs = {
            'layer': layer,
            'env': self.env,
            'logger_name': layer_index  + '_meanstd' if logger_name == '' else logger_name,
            'caption': caption,
        }
        self.regis_plot(plotter=self.vis_funcs['MeanStd'], kwargs=kwargs)


class TensorboardPlotter(BasePlotter):
    vis_funcs = {'WeightRatio':WeightRatioTB, 'Norm':NormTB, 'MeanStd':MeanStdTB}

    def __init__(self, model, comment):
        """
        Tensorboad Backend Visual tool
        """
        super(TensorboardPlotter, self).__init__()
        self.model = model
        self.comment = comment  # writer summary name
        self.writer = SummaryWriter(comment=comment)

        self.hooks = {
            # 'grad': hook_grad,
            'record_forward_in': hook_pre_forward,
            'record_forward': hook_forward,
        }

        self.regis_hook = {
            'forward_in': register_pre_forward_hook,
            'forward_out': register_forward_hook,
            'backward': register_backward_hook,
        }

        self.plots = []

    def regis_weight_ratio_plot(self, layer_index, para_name, logger_name=''):
        """
        :param layer_index:
        :param para_name:
        :param logger_name:
        :param caption:
        """
        para = self.get_para(layer_index, para_name)
        kwargs = {
            'para': para,
            'env': self.env,
            'logger_name': layer_index + '_' + para_name + '_weightratio' if logger_name == '' else logger_name,
        }
        self.regis_plot(plotter=self.vis_funcs['WeightRatio'], kwargs=kwargs)

    def regis_norm_plot(self, layer_index, para_name, logger_name=''):
        """
        :param layer_index:
        :param para_name:
        :param env:
        :param logger_name:
        :param caption:
        """
        para = self.get_para(layer_index, para_name)
        kwargs = {
            'para': para,
            'env': self.env,
            'logger_name': layer_index + '_' + para_name + '_norm' if logger_name == '' else logger_name,
        }
        self.regis_plot(plotter=self.vis_funcs['Norm'], kwargs=kwargs)

    def regis_mean_std(self, layer_index, logger_name=''):
        layer = self.get_layer(layer_index)
        kwargs = {
            'layer': layer,
            'env': self.env,
            'logger_name': layer_index  + '_meanstd' if logger_name == '' else logger_name,
        }
        self.regis_plot(plotter=self.vis_funcs['MeanStd'], kwargs=kwargs)


####### Visdom ########
class WeightRatio(object):
    def __init__(self, para, env, logger_name, caption=''):
        self.para = para
        self.para.register_hook(lambda grad: grad)
        self.logger = VisdomPlotLogger('line', env=env,
                                       opts={'title': caption + '\n' + logger_name, 'caption': caption})
        self.iter_n = 0

    def plot(self):
        eps = 1e-6
        ratio = torch.norm(self.para.grad.data, 2) / torch.norm(self.para.data + eps, 2)
        self.logger.log(self.iter_n, ratio)
        self.iter_n += 1

class MeanStd(object):
    """ plot the mean and std of the layer output """

    def __init__(self, layer, env, logger_name, caption):
        self.layer = layer
        self.layer.register_forward_hook(hook_forward)
        self.mean_logger = VisdomPlotLogger('line', env=env,
                                            opts={'title': 'mean_' + caption + logger_name, 'caption': caption})
        self.std_logger = VisdomPlotLogger('line', env=env,
                                           opts={'title': 'std_' + caption + logger_name, 'caption': caption})
        self.iter_n = 0

    def plot(self):
        mean = torch.mean(self.layer.out_)
        std = torch.std(self.layer.out_)
        del self.layer.out_
        self.mean_logger.log(self.iter_n, mean)
        self.std_logger.log(self.iter_n, std)
        self.iter_n += 1


class Norm(object):
    def __init__(self, para, env, logger_name, caption=''):
        self.para = para
        self.logger = VisdomPlotLogger('line', env=env,
                                       opts={'title': 'norm_' + caption + logger_name, 'caption': caption})
        self.iter_n = 0

    def plot(self):
        self.logger.log(self.iter_n, torch.mean(self.para.data ** 2))
        self.iter_n += 1

####### Tensorboard ########
class WeightRatioTB(object):
    def __init__(self, para, logger_tag):
        # import pdb;pdb.set_trace()
        self.para = para
        self.para.register_hook(lambda grad: grad)
        self.logger_tag = logger_tag
        self.iter_n = 0

    def plot(self, writer):
        eps = 1e-6

        ratio = torch.norm(self.para.grad.data, 2) / torch.norm(self.para.data + eps, 2)

        writer.add_scalar(self.logger_tag, ratio, self.iter_n)

        self.iter_n += 1


class MeanStdTB(object):
    """ plot the mean and std of the layer output """

    def __init__(self, layer, logger_tag):
        self.layer = layer
        self.layer.register_forward_hook(hook_forward)

        self.mean_logger_tag = 'mean_' + logger_tag
        self.std_logger_tag = 'std_' + logger_tag

        self.iter_n = 0

    def plot(self, writer):
        mean = torch.mean(self.layer.out_)
        std = torch.std(self.layer.out_)
        del self.layer.out_
        writer.add_scalar(self.mean_logger_tag, mean, self.iter_n)
        writer.add_scalar(self.std_logger_tag, std, self.iter_n)

        self.iter_n += 1


class NormTB(object):
    def __init__(self, para, logger_tag):
        self.para = para
        self.logger_tag = logger_tag
        # self.logger = VisdomPlotLogger('line', env=env, opts={'title': 'norm_' + caption + logger_name, 'caption': caption})
        self.iter_n = 0

    def plot(self, writer):
        writer.add_scalar(self.logger_tag, torch.mean(self.para.data ** 2), self.iter_n)

        self.iter_n += 1


# class TensorboardManager(object):
#     def __init__(self, model, comment):
#         self.model = model
#         self.comment = comment
#         self.comment_list = []
#
#         if comment in self.comment_list:
#             print("====================You have use this comment before==========================")
#         else:
#             self.comment_list.append(comment)






# Manage viz



##### Manager #####


class VisualManager(object):
    def __init__(self):
        self.viz_dict = {}

    def create_tensorboard_viz(self, name, model, port, comment=''):
        viz = VisdomPlotter(model, comment, port)
        assert name not in self.viz_dict, "Visual Manager: the name in viz_dict already exist"
        self.viz_dict[name] = viz

    def create_visdom_viz(self, name, model, env, port):
        viz = VisdomPlotter(model, env, port)
        assert name not in self.viz_dict, "Visual Manager: the name in viz_dict already exist"
        self.viz_dict[name] = viz


def get_viz(name=None):
    name = name if name else 'root'
    return viz_manager.viz_dict[name]


def create_viz(name, model, env='debug', port=8097):
    name = name if name else 'root'
    viz_manager.create_viz(name, model, env, port)
    return get_viz(name)


viz_manager = VisualManager()
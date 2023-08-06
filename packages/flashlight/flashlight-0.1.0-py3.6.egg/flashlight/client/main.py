import torch

from flashlight.client.python_tracer import PythonTracer


class FlashLight:
    """ The interface class """

    # TODO - pytorch/onnx version check
    def __init__(self, net):
        self.net = net

    def show_dynamic(self, x):
        """ Slow exploration but captures everything, works only in PyTorch """
        with PythonTracer() as pyt:
            trace, out = torch.jit.trace(self.net, x)
        for val in trace.graph().nodes():
            pass
        for val in pyt.trace:
            pass

    def show_static(self, x):
        """ Fast exploration, wont make dynamic graph, default option for
        graphing from ONNNX
        """
        pass

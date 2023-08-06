from nengo import Node, builder
from nengo.base import NengoObject
from nengo.builder.operator import Reset
from nengo.exceptions import ValidationError, SimulationError
from nengo.params import Default, IntParam, Parameter
import numpy as np
import tensorflow as tf

from nengo_dl.builder import Builder, OpBuilder


class TensorFuncParam(Parameter):
    """Performs validation on the function passed to TensorNode, and sets
    ``size_out`` if necessary."""

    def __init__(self, name, readonly=False):
        super(TensorFuncParam, self).__init__(
            name, optional=False, readonly=readonly)

    def coerce(self, node, func):
        output = super(TensorFuncParam, self).coerce(node, func)

        if node.size_out is None:
            node.size_out = self.check_size_out(node, func)

        return output

    def validate(self, node, func):
        # TODO: this method is just here for compatibility with nengo<2.4.1,
        # can be removed if we update requirements

        super(TensorFuncParam, self).validate(node, func)

        if node.size_out is None:
            node.size_out = self.check_size_out(node, func)

    def check_size_out(self, node, func):
        if not callable(func):
            raise ValidationError("TensorNode output must be a function",
                                  attr=self.name, obj=node)

        t, x = tf.constant(0.0), tf.zeros((1, node.size_in))
        args = (t, x) if node.size_in > 0 else (t,)
        try:
            result = func(*args)
        except Exception as e:
            raise ValidationError(
                "Calling TensorNode function with arguments %s produced an "
                "error:\n%s" % (args, e), attr=self.name, obj=node)

        if not isinstance(result, tf.Tensor):
            raise ValidationError("TensorNode function must return a Tensor",
                                  attr=self.name, obj=node)

        if result.get_shape().ndims != 2:
            raise ValidationError("Node output must be a minibatched vector "
                                  "(got shape %s)" % result.get_shape(),
                                  attr=self.name, obj=node)

        return result.get_shape()[1].value


class TensorNode(Node):
    """Inserts TensorFlow code into a Nengo model.  A TensorNode operates in
    much the same way as a :class:`~nengo:nengo.Node`, except its inputs and
    outputs are defined using TensorFlow operations.

    The TensorFlow code is defined in a function or callable class
    (``tensor_func``).  This function accepts the current simulation time as
    input, or the current simulation time and a Tensor ``x`` if
    ``node.size_in > 0``.  ``x`` will have shape
    ``(sim.minibatch_size, node.size_in``), and the function should return a
    Tensor with shape ``(sim.minibatch_size, node.size_out)``.
    ``node.size_out`` will be inferred by calling the function once and
    checking the output, if it isn't set when the Node is created.

    If ``tensor_func`` has a ``pre_build`` attribute, that function will be
    called once when the model is constructed.  This can be used to compute any
    constant values or set up variables -- things that don't need to
    execute every simulation timestep.

    Parameters
    ----------
    tensor_func : callable
        a function that maps node inputs to outputs
    size_in : int, optional (Default: 0)
        the number of elements in the input vector
    size_out : int, optional (Default: None)
        the number of elements in the output vector (if None, value will be
        inferred by calling ``tensor_func``)
    label : str, optional (Default: None)
        a name for the node, used for debugging and visualization
    """

    tensor_func = TensorFuncParam('tensor_func')
    size_in = IntParam('size_in', default=0, low=0, optional=True)
    size_out = IntParam('size_out', default=None, low=1, optional=True)

    def __init__(self, tensor_func, size_in=Default, size_out=Default,
                 label=Default):
        # note: we bypass the Node constructor, because we don't want to
        # perform validation on `output`
        NengoObject.__init__(self, label=label, seed=None)

        self.size_in = size_in
        self.size_out = size_out
        self.tensor_func = tensor_func


@builder.Builder.register(TensorNode)
def build_tensor_node(model, node):
    """This is the Nengo build function, so that Nengo knows what to do with
    TensorNodes."""

    # input signal
    if node.size_in > 0:
        sig_in = builder.Signal(np.zeros(node.size_in), name="%s.in" % node)
        model.add_op(Reset(sig_in))
    else:
        sig_in = None

    sig_out = builder.Signal(np.zeros(node.size_out), name="%s.out" % node)

    model.sig[node]['in'] = sig_in
    model.sig[node]['out'] = sig_out
    model.params[node] = None

    model.add_op(SimTensorNode(node.tensor_func, model.time, sig_in, sig_out))


class SimTensorNode(builder.Operator):
    """Operator for TensorNodes (constructed by :func:`.build_tensor_node`).

    Parameters
    ----------
    func : callable
        the TensorNode function (``tensor_func``)
    time : :class:`~nengo:nengo.builder.Signal`
        Signal representing the current simulation time
    input : :class:`~nengo:nengo.builder.Signal` or None
        input Signal for the TensorNode (or None if size_in==0)
    output : :class:`~nengo:nengo.builder.Signal`
        output Signal for the TensorNode
    tag : str, optional
        a label associated with the operator, for debugging

    Notes
    -----
    1. sets ``[output]``
    2. incs ``[]``
    3. reads ``[time] if input is None else [time, input]``
    4. updates ``[]``
    """

    def __init__(self, func, time, input, output, tag=None):
        super(SimTensorNode, self).__init__(tag=tag)

        self.func = func
        self.input = input
        self.output = output

        self.sets = [output]
        self.incs = []
        self.reads = [time] if input is None else [time, input]
        self.updates = []

    def make_step(self, *args, **kwargs):
        """``make_step`` is never called by the NengoDL simulator, so if this
        is called it means that someone is trying to execute a TensorNode in
        some other Simulator."""

        def error():
            raise SimulationError("TensorNode can only be simulated in the "
                                  "NengoDL simulator")

        return error


@Builder.register(SimTensorNode)
class SimTensorNodeBuilder(OpBuilder):
    """Builds a :class:`.SimTensorNode` operator into a NengoDL model."""

    def __init__(self, ops, signals):
        # SimTensorNodes should never be merged
        assert len(ops) == 1
        op = ops[0]

        if op.input is None:
            self.src_data = None
        else:
            self.src_data = signals.sig_map[op.input]
            self.src_data.load_indices()
            assert self.src_data.ndim == 1

        self.dst_data = signals.sig_map[op.output]
        self.dst_data.load_indices()

        self.func = op.func

        if hasattr(self.func, "pre_build"):
            self.func.pre_build(
                (signals.minibatch_size,) + self.src_data.shape,
                (signals.minibatch_size,) + self.dst_data.shape)

    def build_step(self, signals):
        if self.src_data is None:
            output = self.func(signals.time)
        else:
            input = signals.gather(self.src_data)

            # move minibatch dimension to front
            input = tf.transpose(input, (1, 0))

            output = self.func(signals.time, input)

        # move minibatch dimension back to end
        output_dim = output.get_shape().ndims - 1
        output = tf.transpose(
            output, [output_dim] + [i for i in range(output_dim)])

        signals.scatter(self.dst_data, output)

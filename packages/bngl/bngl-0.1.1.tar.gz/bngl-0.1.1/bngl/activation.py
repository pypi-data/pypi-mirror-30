import numpy as np
from .operation import Operation

class Relu(Operation):
    def __init__(self, input_shape):
        def operation_fn(x, params):
            return (x>0).astype(float) * x

        def input_gradient_fn(x, params):
            return np.identity(np.prod(input_shape))\
                   * (x>0).astype(float).reshape(-1, 1)

        super(Relu, self).__init__(input_shape,
                                   input_shape,
                                   operation_fn=operation_fn,
                                   input_gradient_fn=input_gradient_fn,
                                   trainable=False)

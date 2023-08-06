import numpy as np
from .operation import Operation

class FullyConnected1D(Operation):
    def __init__(self,
                 input_shape,
                 output_shape,
                 update_fn,
                 initializer_fn=None):

        if len(input_shape) != 2 or input_shape[-1] != 1:
            raise ValueError('input_shape expected to be : (-1, 1) but got: ', input_shape)
        if len(output_shape) != 2 or output_shape[-1] != 1:
            raise ValueError('output_shape expected to be : (-1, 1) but got: ', output_shape)


        total_weights = input_shape[0] * output_shape[0]
        weight_shape = (output_shape[0], input_shape[0])
        if initializer_fn is None:
            trainable_parameters = np.array([np.random.normal() for _ in range(total_weights)])
        else:
            trainable_parameters = initializer_fn()
            if type(trainable_parameters) != np.ndarray:
                raise TypeError('initializer function must return np.ndarray, but returned: ', type(trainable_parameters))
            if trainable_parameters.shape[0] != total_weights or np.ndim(trainable_parameters) != 1:
                raise ValueError('initializer function must return shape: (', total_weights, ', ) but returned len: ', trainable_parameters.shape)

        def operation_fn(x, params):
            params = params.reshape(weight_shape)
            return params @ x

        def input_gradient_fn(last_input, params):
            return params.reshape(weight_shape)

        def weight_gradient_fn(dloss_dout, last_input):
            dout_dweight = np.stack([last_input for _ in range(output_shape[0])])
            dout_dweight = dout_dweight.reshape(weight_shape)
            dloss_dweight = np.array(dloss_dout.T * dout_dweight).flatten()
            return dloss_dweight

        super(FullyConnected1D, self).__init__(input_shape,
                                               output_shape,
                                               operation_fn=operation_fn,
                                               input_gradient_fn=input_gradient_fn,
                                               weight_gradient_fn=weight_gradient_fn,
                                               update_fn=update_fn,
                                               trainable=True,
                                               trainable_parameters=trainable_parameters)


class Bias1D(Operation):
    def __init__(self,
                 input_shape,
                 update_fn,
                 initializer_fn=None):

        if len(input_shape) != 2 or input_shape[-1] != 1:
            raise ValueError('input_shape expected to be : (-1, 1) but got: ', input_shape)

        total_weights = input_shape[0]

        if initializer_fn is None:
            trainable_parameters = np.array([.01 for _ in range(total_weights)])
        else:
            trainable_parameters = initializer_fn()
            if type(trainable_parameters) != np.ndarray:
                raise TypeError('initializer function must return np.ndarray, but returned: ', type(trainable_parameters))
            if trainable_parameters.shape[0] != total_weights or np.ndim(trainable_parameters) != 1:
                raise ValueError('initializer function must return shape: (', total_weights, ', ) but returned len: ', trainable_parameters.shape)

        def operation_fn(x, params):
            return x + params.reshape(-1, 1)

        def input_gradient_fn(last_input, params):
            return np.identity(last_input.shape[0])

        def weight_gradient_fn(dloss_dout, last_input):
            return dloss_dout.flatten()

        super(Bias1D, self).__init__(input_shape,
                                     input_shape,
                                     operation_fn=operation_fn,
                                     input_gradient_fn=input_gradient_fn,
                                     weight_gradient_fn=weight_gradient_fn,
                                     update_fn=update_fn,
                                     trainable=True,
                                     trainable_parameters=trainable_parameters)

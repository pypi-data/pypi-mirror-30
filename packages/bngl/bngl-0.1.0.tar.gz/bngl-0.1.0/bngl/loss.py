import numpy as np
from .operation import Operation

class SoftmaxCrossEntropy(Operation):
    def __init__(self, input_shape):

        def operation_fn(pred_label_pair, params):
            x = pred_label_pair[0]
            y = pred_label_pair[1]

            m = np.max(x)
            smax = np.exp(x-m)/(np.sum(np.exp(x-m)))

            #NOTE this is done for numerical stability in the log
            smax = np.maximum(smax, np.ones_like(smax) * 1e-7)
            return (-1 * y.T @ np.log(smax)).reshape(-1, 1)

        def input_gradient_fn(pred_label_pair, params):
            x = pred_label_pair[0]
            y = pred_label_pair[1]

            m = np.max(x)
            smax = np.exp(x-m)/(np.sum(np.exp(x-m)))
            grad = (smax - y).reshape(-1, )
            #NOTE this is dne since the output of input_gradient_fn must return
            #a gradient for each dim of its input, including the label.
            grad = list(grad) + list(np.zeros_like(y).reshape(-1, ))
            return np.array(grad).reshape(1, -1)


        super(SoftmaxCrossEntropy, self).__init__(input_shape,
                                                  (1, 1),
                                                  operation_fn=operation_fn,
                                                  input_gradient_fn=input_gradient_fn,
                                                  trainable=False)

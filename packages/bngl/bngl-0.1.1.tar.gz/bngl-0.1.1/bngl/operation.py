import warnings
import numpy as np

class Operation(object):
    def __init__(self,
                 input_shape,
                 output_shape,
                 operation_fn=None,
                 input_gradient_fn=None,
                 weight_gradient_fn=None,
                 update_fn=None,
                 trainable=True,
                 trainable_parameters=None):

        self.input_shape = input_shape
        self.output_shape = output_shape

        #set trainable and trainable_parameters
        if trainable and trainable_parameters is None:
            warnings.warn('trainable layer initialized with empty trainable parameter list', Warning)
        if not trainable and not trainable_parameters is None:
            warnings.warn('non trainable layer initialized with trainable parameter list', Warning)
        self.trainable = trainable
        self.trainable_parameters = trainable_parameters


        #setting self.operation_fn
        if operation_fn is None:
            raise ValueError('operations must have an operation_fn. set it with kwarg operation_fn')
        else:
            test_input = np.zeros(input_shape)
            test_output = operation_fn(test_input, trainable_parameters)
            if type(test_output) != np.ndarray:
                raise TypeError('operation_fn must return numpy.ndarray, but returned: ', type(test_output))
            if test_output.shape != self.output_shape:
                raise ValueError('operation_fn must return shape: ', output_shape, ' but returned: ', test_output.shape)
            self.operation_fn = operation_fn

        #setting self.input_gradient_fn
        if input_gradient_fn is None:
            raise ValueError('operations must have a gradient_fn. set it with kwarg gradient_fn')

        else:
            test_input = np.zeros(input_shape)
            test_output = input_gradient_fn(test_input, trainable_parameters)
            desired_shape = (np.prod(output_shape),
                             np.prod(input_shape))
            if type(test_output) != np.ndarray:
                raise TypeError('input_gradient_fn must return numpy.ndarray, but returned: ', type(test_output))
            if test_output.shape != desired_shape:
                raise ValueError('input_gradient_fn must return shape: ', desired_shape, ' but returned: ', test_output.shape)
            self.input_gradient_fn = input_gradient_fn


        #setting self.weight_gradient_fn
        self.weight_gradient_fn = weight_gradient_fn

        #setting self.update_fn
        if update_fn is None:
            if self.trainable:
                raise ValueError('trainable layers must have update functions. set it with kwarg update_fn')
        else:
            if not self.trainable:
                warnings.warn('update_fn passed to non-trainable layer', Warning)
        self.update_fn = update_fn

        self.weight_gradients = []
        self.last_input = None


    def clear_weight_gradients(self):
        self.weight_gradients = []
        self.last_input = None
        return


    def do_operation(self, x):
        if type(x) != np.ndarray:
            raise TypeError('do_operation expected numpy.ndarray, got: ', type(x))

        if x.shape != self.input_shape:
            raise ValueError('do_operation expected array of shape: ', self.input_shape, ' got: ', x.shape)

        self.last_input = x
        return self.operation_fn(x, self.trainable_parameters)


    def get_input_gradient(self):
        #TODO check if last input is None here
        return self.input_gradient_fn(self.last_input, self.trainable_parameters)


    def register_weight_gradient(self, gradient):
        if type(gradient) != np.ndarray:
            raise TypeError('register_weight_gradient expected numpy.ndarray, got: ', type(gradient))

        if self.last_input is None:
            raise ValueError('register_weight_gradient requires an input through the operation first! Did you forget to do_operation?')

        weight_gradient = self.weight_gradient_fn(gradient, self.last_input)
        self.weight_gradients.append(weight_gradient)
        return


    def update(self, autoclear_gradients=True):
        self.trainable_parameters = self.update_fn(self.weight_gradients,
                                                   self.trainable_parameters)
        if autoclear_gradients:
            self.clear_weight_gradients()

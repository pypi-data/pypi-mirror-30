import numpy as np

class LinearGraph:
    def __init__(self):
        self.layers = []
        self.loss = None
        return


    def add_operation(self, layer):
        #TODO check if layer is operation
        self.layers.append(layer)
        return


    def add_loss(self, loss):
        #TODO check if loss is operation
        self.loss = loss


    def forward(self, x):
        for layer in self.layers:
            x = layer.do_operation(x)
        return x


    def train_on_batch(self, batch, labels):
        label_shape = labels[0].shape
        batch_loss = 0
        for idx, x in enumerate(batch):
            y = labels[idx]

            #forward pass
            for layer in self.layers    :
                x = layer.do_operation(x)
            cur_loss = self.loss.do_operation(np.stack([x, y]))
            batch_loss += cur_loss


            dloss_dout = self.loss.get_input_gradient()
            #slice here removes un-needed y gradient
            dloss_dout = dloss_dout.flatten()[:np.prod(label_shape)]
            #cast ensures that array is not of dtype Object for matmul
            dloss_dout = dloss_dout.reshape(1, -1).astype(float)
            for idx in range(len(self.layers)-1, -1, -1):
                layer = self.layers[idx]
                if layer.trainable:
                    layer.register_weight_gradient(dloss_dout)
                dout_din = layer.get_input_gradient()
                dloss_dout = dloss_dout @ dout_din

        #update
        for layer in self.layers:
            if layer.trainable:
                layer.update()

        return batch_loss
